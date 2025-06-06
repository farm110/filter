# CSV Filter Application

A Streamlit application that filters CSV files based on values from a template file.

## Features
- Upload template CSV file
- Upload multiple target CSV files
- Filter data based on selected columns
- Download filtered results

## Quick Start
1. Upload a template CSV file
2. Select the column to filter by
3. Upload one or more target CSV files
4. Select the target column
5. Click "Start Filtering"
6. Download the filtered results

## Local Development
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run csv_filter.py
``` 