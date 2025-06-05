import streamlit as st
import pandas as pd
import io

# Set page configuration
st.set_page_config(
    page_title="Gene Filter App",
    page_icon="🧬",
    layout="wide"
)

def main():
    st.title("Gene Filter Application")
    st.write("""
    This application helps you filter CSV files based on values from a template file.
    Upload your template file and the files you want to filter, and specify which columns to use!
    """)

    # Upload template file
    st.header("Step 1: Upload Template File")
    template_file = st.file_uploader("Upload your template CSV file", type=['csv'])
    
    if template_file is not None:
        try:
            template_df = pd.read_csv(template_file)
            
            # Let user select the column from template file
            st.subheader("Select Column from Template File")
            template_column = st.selectbox(
                "Choose the column containing the values to keep:",
                options=template_df.columns.tolist()
            )
            
            # Get unique values from selected column
            value_set = set(template_df[template_column].astype(str))
            st.write(f"Template file loaded successfully! Found {len(value_set)} unique values in column '{template_column}'.")
            
            # Upload files to filter
            st.header("Step 2: Upload Files to Filter")
            uploaded_files = st.file_uploader("Upload the CSV files you want to filter", type=['csv'], accept_multiple_files=True)
            
            if uploaded_files:
                st.header("Step 3: Process Files")
                
                # Let user select the column from target files
                st.subheader("Select Column from Target Files")
                st.write("Note: This column should contain the same type of values as the template column")
                
                # Read first file to get columns
                first_file = pd.read_csv(uploaded_files[0])
                target_column = st.selectbox(
                    "Choose the column to filter on:",
                    options=first_file.columns.tolist()
                )
                
                process_button = st.button("Start Filtering")
                
                if process_button:
                    for uploaded_file in uploaded_files:
                        try:
                            # Read the file
                            df = pd.read_csv(uploaded_file)
                            
                            # Convert both columns to string for comparison
                            df[target_column] = df[target_column].astype(str)
                            
                            # Filter the data
                            filtered_df = df[df[target_column].isin(value_set)]
                            
                            # Create download button for filtered file
                            csv = filtered_df.to_csv(index=False)
                            st.download_button(
                                label=f"Download filtered {uploaded_file.name}",
                                data=csv,
                                file_name=f"filtered_{uploaded_file.name}",
                                mime="text/csv"
                            )
                            
                            # Show statistics
                            st.write(f"File: {uploaded_file.name}")
                            st.write(f"Original rows: {len(df)}")
                            st.write(f"Filtered rows: {len(filtered_df)}")
                            st.write(f"Rows removed: {len(df) - len(filtered_df)}")
                            st.write("---")
                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        except Exception as e:
            st.error(f"Error reading template file: {str(e)}")

if __name__ == "__main__":
    main() 