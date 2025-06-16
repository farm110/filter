# File Filter Tool

A Streamlit application that allows you to filter CSV and Excel files based on values from a template file.

## Features

- Support for both CSV and Excel files (.csv, .xlsx, .xls)
- Multiple file processing
- Robust file handling with multiple encoding support
- Excel output with multiple sheets
- Individual file downloads
- Progress tracking and statistics

## Deployment on Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your forked repository
6. Set the main file path to `csv_filter.py`
7. Click "Deploy"

The app will be deployed in a few minutes and you'll get a public URL to share.

## Local Development

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the app:
```bash
streamlit run csv_filter.py
```

## Usage

1. Upload a template file (CSV or Excel)
2. Select the column to filter by
3. Upload one or more target files
4. Select the target column
5. Click "Start Filtering"
6. Download the filtered results

## Requirements

- Python 3.7+
- Dependencies listed in requirements.txt 