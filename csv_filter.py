import pandas as pd
import streamlit as st
import io
from typing import List, Tuple
import time
import gc
import os
from datetime import datetime

def load_csv(file) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame with robust error handling."""
    try:
        # Reset file pointer to beginning
        file.seek(0)
        
        # Try different encodings and parameters
        encodings = ['utf-8', 'latin1', 'cp1252']
        for encoding in encodings:
            try:
                df = pd.read_csv(
                    file,
                    encoding=encoding,
                    on_bad_lines='skip',
                    engine='python',  # More forgiving engine
                    memory_map=False
                )
                if not df.empty:
                    return df
            except Exception:
                file.seek(0)  # Reset file pointer for next attempt
                continue
        
        # If all attempts fail, try with more lenient parameters
        file.seek(0)
        df = pd.read_csv(
            file,
            encoding='latin1',
            on_bad_lines='skip',
            engine='python',
            memory_map=False,
            sep=None,  # Auto-detect separator
            skipinitialspace=True
        )
        return df
    except Exception as e:
        st.error(f"Error loading file {file.name}: {str(e)}")
        return None
        
def filter_dataframe(df: pd.DataFrame, template_values: set, column_name: str) -> pd.DataFrame:
    """Filter DataFrame based on template values."""
    try:
        # Convert column to string type for consistent comparison
        df[column_name] = df[column_name].astype(str)
        template_values = {str(x) for x in template_values}Add commentMore actions
        return df[df[column_name].isin(template_values)]
    except Exception as e:
        st.error(f"Error filtering data: {str(e)}")
        return df
        
def process_files(template_file, target_files, template_column, target_column):
    """Process multiple files and return filtered results."""
    results = []
    template_df = load_csv(template_file)
    
    if template_df is None:
        return results
    
    # Ensure template column exists
    if template_column not in template_df.columns:
        st.error(f"Template column '{template_column}' not found in template file")
        return results
    
    template_values = set(template_df[template_column].astype(str))
    template_row_count = len(template_df)
    
    for target_file in target_files:
        target_df = load_csv(target_file)
        if target_df is not None:
            # Ensure target column exists
            if target_column not in target_df.columns:
                st.warning(f"Target column '{target_column}' not found in {target_file.name}, skipping...")
                continue
                
            original_row_count = len(target_df)
            filtered_df = target_df[target_df[target_column].astype(str).isin(template_values)]
            if not filtered_df.empty:
                # Store both DataFrame and CSV string
                csv_data = filtered_df.to_csv(index=False)
                results.append((target_file.name, filtered_df, csv_data, original_row_count, template_row_count))
    
    return results

def combine_filtered_results(filtered_dfs):
    """Combine all filtered DataFrames into one."""
    if not filtered_dfs:
        return None
    return pd.concat(filtered_dfs, ignore_index=True)

def create_excel_with_sheets(results):
    """Create an Excel file with multiple sheets, one for each result."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for filename, df, _, _, _ in results:
            # Clean the sheet name (Excel has a 31 character limit for sheet names)
            sheet_name = filename[:31].replace('.', '_')
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def main():
    st.set_page_config(
        page_title="CSV Filter Tool",
        page_icon="📊",
        layout="wide"
    )
    
    # Initialize session state for results if it doesn't exist
    if 'filtered_results' not in st.session_state:
        st.session_state.filtered_results = None
    
    st.title("CSV Filter Tool")
    st.write("Filter CSV files based on values from a template file")
    
    # Step 1: Upload template file
    st.header("Step 1: Upload Template File")
    template_file = st.file_uploader("Upload template CSV file", type=['csv'])
    
    if template_file:
        template_df = load_csv(template_file)
        if template_df is not None:
            st.write(f"Template file contains {len(template_df)} rows")
            template_column = st.selectbox(
                "Select template column to filter by",
                options=template_df.columns.tolist()
            )
            
            # Step 2: Upload target files
            st.header("Step 2: Upload Target Files")
            target_files = st.file_uploader(
                "Upload one or more CSV files to filter",
                type=['csv'],
                accept_multiple_files=True
            )
            
            if target_files:
                # Get column names from first target file
                first_target_df = load_csv(target_files[0])
                if first_target_df is not None:
                    target_column = st.selectbox(
                        "Select target column to filter on",
                        options=first_target_df.columns.tolist()
                    )
                    
                    if st.button("Start Filtering"):
                        with st.spinner("Processing files..."):
                            start_time = time.time()
                            results = process_files(template_file, target_files, template_column, target_column)
                            end_time = time.time()
                            
                            if results:
                                st.session_state.filtered_results = results
                                st.success(f"Processing completed in {end_time - start_time:.2f} seconds")
                            else:
                                st.error("No matching results found")
    
    # Display results from session state
    if st.session_state.filtered_results:
        results = st.session_state.filtered_results
        
        # Add download all button (Excel with multiple sheets)
        if len(results) > 1:
            excel_data = create_excel_with_sheets(results)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="Download All Results (Excel with multiple sheets)",
                data=excel_data,
                file_name=f"filtered_results_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_all"
            )
        
        # Display individual results
        for i, (filename, df, csv_data, original_rows, template_rows) in enumerate(results):
            st.write(f"### Results for {filename}")
            st.write(f"Template rows: {template_rows}")
            st.write(f"Original input rows: {original_rows}")
            st.write(f"Filtered rows: {len(df)}")
            st.write(f"Rows removed: {original_rows - len(df)}")
            
            # Create download button for individual file
            st.download_button(
                label=f"Download filtered {filename}",
                data=csv_data,
                file_name=f"filtered_{filename}",
                mime="text/csv",
                key=f"download_{i}"
            )

if __name__ == "__main__":
    main() 
