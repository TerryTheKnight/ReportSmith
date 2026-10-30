# ReportSmith

ReportSmith turns a CSV or Excel spreadsheet into a quick, shareable data report. Upload a file to inspect its rows and columns, catch common data-quality issues, view descriptive statistics, explore a chart, and download the analyzed data or a standalone HTML report.

## Features

- Reads CSV and Excel `.xlsx` files.
- Previews the first 100 rows and shows each column's data type.
- Flags missing values, duplicate rows, and columns with one distinct value.
- Summarizes numeric columns with count, mean, standard deviation, minimum, and maximum.
- Draws Matplotlib histograms with mean/median markers, category-count bars with counts and shares, aggregated line charts, and scatter plots with a trend line.
- Adds a plain-language chart summary, suggests date columns first for trend charts, and lets users choose sum or average for repeated x-axis values.
- Downloads the source data as CSV and a self-contained HTML report with an embedded chart.
- Processes uploaded data in the app session; ReportSmith does not save uploads to disk.

## Requirements

- Python 3.11 or newer
- Windows, macOS, or Linux

## Run locally on Windows

Open PowerShell in this folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Then open the local address printed in the terminal. Upload `sample.csv` from the app's sidebar to try it.

### macOS or Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Run the tests

```powershell
python -m unittest discover -s tests -v
```

## Project layout

```text
ReportSmith/
├── app.py               # Streamlit user interface
├── reportsmith.py       # File reading, analysis, charts, and HTML report
├── requirements.txt     # Python packages
├── sample.csv           # Example data with a duplicate and a missing value
├── test_data/           # Larger synthetic datasets for manual testing
└── tests/               # Unit tests for the analysis functions
```

To regenerate the larger sample files, run `python generate_test_data.py` from this folder. See `test_data/README.md` for the scenarios covered by each file.

## Current scope

This is an educational analysis tool, not a replacement for validating data before making high-impact decisions. It reports common structural issues and summarizes numeric data; it does not infer what missing values mean, fix records automatically, or perform statistical significance testing. Excel `.xls` files are not supported yet.

## Next improvements

- Let the user choose an Excel worksheet.
- Add downloadable PDF reports.
- Add date-aware trends and category breakdown charts.
- Add configurable rules for acceptable missing-value rates and duplicate detection.

## License

No license has been selected yet. Choose a license before accepting outside contributions or inviting reuse.
