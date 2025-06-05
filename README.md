# Gene Filter Application

This is a user-friendly web application that helps you filter CSV files based on values from a template file.

## How to Use

1. **Install Requirements**
   ```
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```
   streamlit run gene_filter_app.py
   ```

3. **Using the Application**
   - The application will open in your web browser
   - Step 1: Upload your template CSV file
     - Select which column contains the values you want to keep
   - Step 2: Upload one or more CSV files that you want to filter
     - Select which column to filter on (should contain the same type of values as the template column)
   - Step 3: Click "Start Filtering" to process the files
   - Download buttons will appear for each filtered file

## Notes
- You can select any column from both the template and target files
- The application will keep only rows where the selected column's values match those in the template
- Filtered files will be prefixed with "filtered_"
- You can process multiple files at once
- The application shows statistics for each file (original rows, filtered rows, and rows removed