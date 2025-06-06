import pandas as pd
import streamlit as st
import io
from typing import List, Tuple
import time
import gc

def load_csv(file) -> pd.DataFrame:
    """Load CSV file into pandas DataFrame with error handling."""
    try:
        # Read the file content
        content = file.getvalue().decode('utf-8')
        # Create a StringIO object
        csv_data = io.StringIO(content)
        # Read CSV with more flexible parsing and optimized settings
        return pd.read_csv(
            csv_data,
            encoding='utf-8',
            on_bad_lines='skip',
            engine='c',  # Use C engine for better performance
            memory_map=True  # Use memory mapping for large files
        )
    except Exception as e:
        st.error(f"Error reading file {file.name}: {str(e)}")
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
            
        template_values = set(template_df[template_column].unique())
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
            filtered_df = filter_dataframe(target_df, template_values, target_column)
            
            # Get original filename without extension
            original_name = target_file.name.split('.')[0]
            results.append((original_name, filtered_df))
            
            # Clear target_df from memory
            del target_df
            gc.collect()
        
        return results
    except Exception as e:
        st.error(f"Error processing files: {str(e)}")
        return []

def main():
    st.set_page_config(
        page_title="CSV Filter",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("CSV Filter Application")
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
                                
                                # Display results
                                for original_name, filtered_df in results:
                                    st.write(f"### Results for {original_name}")
                                    st.write(f"Original rows: {len(load_csv(target_files[0]))}")
                                    st.write(f"Filtered rows: {len(filtered_df)}")
                                    st.write(f"Rows removed: {len(load_csv(target_files[0])) - len(filtered_df)}")
                                    
                                    # Create download button
                                    csv = filtered_df.to_csv(index=False)
                                    st.download_button(
                                        label=f"Download filtered {original_name}",
                                        data=csv,
                                        file_name=f"filtered_{original_name}.csv",
                                        mime="text/csv"
                                    )
                            else:
                                st.error("No results were generated. Please check your input files and try again.")

if __name__ == "__main__":
    main() 