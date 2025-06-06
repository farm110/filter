import pandas as pd
import streamlit as st
import io
from typing import List, Tuple
import time
import gc
import os
from datetime import datetime

def load_csv(file) -> pd.DataFrame:
    """Load CSV file into pandas DataFrame with error handling."""
    try:
        # Reset file pointer to beginning
        file.seek(0)
        
        # Try reading with python engine first (more forgiving)
        try:
            df = pd.read_csv(
                file,
                encoding='utf-8',
                on_bad_lines='skip',
                engine='python',  # Use python engine instead of c
                memory_map=False  # Disable memory mapping
            )
            return df
        except Exception as e1:
            # If first attempt fails, try with latin1 encoding
            file.seek(0)
            try:
                df = pd.read_csv(
                    file,
                    encoding='latin1',
                    on_bad_lines='skip',
                    engine='python',
                    memory_map=False
                )
                return df
            except Exception as e2:
                st.error(f"Error reading file {file.name}: First attempt: {str(e1)}, Second attempt: {str(e2)}")
                return None
    except Exception as e:
        st.error(f"Error accessing file {file.name}: {str(e)}")
        return None

def filter_dataframe(df: pd.DataFrame, template_values: set, column_name: str) -> pd.DataFrame:
    """Filter DataFrame based on template values."""
    try:
        # Convert column to string type for consistent comparison
        df[column_name] = df[column_name].astype(str)
        template_values = {str(x) for x in template_values}
        return df[df[column_name].isin(template_values)]
    except Exception as e:
        st.error(f"Error filtering data: {str(e)}")
        return df

def process_files(template_file, target_files: List, template_column: str, target_column: str) -> List[Tuple[str, pd.DataFrame]]:
    """Process template and target files."""
    try:
        # Load template file
        template_df = load_csv(template_file)
        if template_df is None:
            return []
            
        template_values = set(template_df[template_column].astype(str))
        # Clear template_df from memory
        del template_df
        gc.collect()
        
        results = []
        for target_file in target_files:
            # Load target file
            target_df = load_csv(target_file)
            if target_df is None:
                continue
                
            # Filter target file
            filtered_df = target_df[target_df[target_column].astype(str).isin(template_values)]
            
            # Get original filename without extension
            original_name = target_file.name.split('.')[0]
            if not filtered_df.empty:
                results.append((original_name, filtered_df))
            
            # Clear target_df from memory
            del target_df
            gc.collect()
        
        return results
    except Exception as e:
        st.error(f"Error processing files: {str(e)}")
        return []

def load_template(template_path):
    """Load the template CSV file."""
    try:
        return pd.read_csv(template_path)
    except Exception as e:
        st.error(f"Error loading template: {str(e)}")
        return None

def filter_csv(input_file, template_df):
    """Filter the input CSV based on the template columns."""
    try:
        # Read the input CSV file
        input_df = pd.read_csv(input_file)
        
        # Get the columns from the template
        template_columns = template_df.columns.tolist()
        
        # Filter the input DataFrame to only include columns that exist in the template
        # and match the template's column order
        available_columns = [col for col in template_columns if col in input_df.columns]
        filtered_df = input_df[available_columns]
        
        # Reorder columns to match template
        filtered_df = filtered_df[available_columns]
        
        return filtered_df
    except Exception as e:
        st.error(f"Error processing {input_file.name}: {str(e)}")
        return None

def combine_filtered_results(filtered_dfs):
    """Combine all filtered DataFrames into one."""
    if not filtered_dfs:
        return None
    return pd.concat(filtered_dfs, ignore_index=True)

def create_excel_with_sheets(results):
    """Create an Excel file with multiple sheets, one for each result."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for filename, df in results:
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
    
    st.title("CSV Filter Tool")
    st.write("Filter CSV files based on values from a template file")
    
    # Step 1: Upload template file
    st.header("Step 1: Upload Template File")
    template_file = st.file_uploader("Upload template CSV file", type=['csv'])
    
    if template_file:
        template_df = load_csv(template_file)
        if template_df is not None:
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
                                st.success(f"Processing completed in {end_time - start_time:.2f} seconds")
                                
                                # Add download all button (Excel with multiple sheets)
                                if len(results) > 1:
                                    excel_data = create_excel_with_sheets(results)
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    st.download_button(
                                        label="Download All Results (Excel with multiple sheets)",
                                        data=excel_data,
                                        file_name=f"filtered_results_{timestamp}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                                
                                # Display individual results
                                for filename, df in results:
                                    st.write(f"### Results for {filename}")
                                    st.write(f"Original rows: {len(load_csv(target_files[0]))}")
                                    st.write(f"Filtered rows: {len(df)}")
                                    st.write(f"Rows removed: {len(load_csv(target_files[0])) - len(df)}")
                                    
                                    # Create download button for individual file
                                    csv = df.to_csv(index=False)
                                    st.download_button(
                                        label=f"Download filtered {filename}",
                                        data=csv,
                                        file_name=f"filtered_{filename}",
                                        mime="text/csv"
                                    )
                            else:
                                st.error("No matching results found")

if __name__ == "__main__":
    main() 