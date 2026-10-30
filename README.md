# ReportSmith

**Turn spreadsheets into meaningful, shareable data reports.**

ReportSmith is a Python-based data analysis and reporting application that transforms CSV and Excel spreadsheets into interactive data insights and downloadable HTML reports.

Upload a dataset, inspect its structure, identify common data-quality issues, explore visualizations, and generate a standalone report — all through a simple Streamlit interface.

## Features

### Data Exploration
- Import CSV and Excel (`.xlsx`) files.
- Preview the first 100 rows of a dataset.
- Inspect column names and data types.
- Explore dataset dimensions and structure.

### Data Quality Analysis
- Detect missing values.
- Identify duplicate rows.
- Flag columns containing only one distinct value.
- Review common structural data-quality issues.

### Statistical Analysis
- Generate descriptive statistics for numerical columns.
- Calculate count, mean, standard deviation, minimum, and maximum.
- Identify potential date columns.

### Data Visualization
- Histograms with mean and median markers.
- Category-count bar charts with counts and percentages.
- Aggregated line charts.
- Scatter plots with linear trend lines.
- Plain-language chart summaries.

### Report Generation
- Download analyzed data as CSV.
- Generate standalone HTML reports.
- Embed charts directly into HTML reports.
- Process uploaded files within the application session without saving uploads to disk.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web application interface |
| Pandas | Data processing and analysis |
| NumPy | Numerical calculations |
| Matplotlib | Data visualization |
| OpenPyXL | Excel file support |
| Unittest | Automated testing |

## Project Structure

```text
ReportSmith/
│
├── app.py                  # Streamlit interface
├── reportsmith.py          # Analysis and reporting engine
├── requirements.txt        # Project dependencies
├── generate_test_data.py   # Synthetic test-data generator
├── sample.csv              # Example dataset
│
├── test_data/
│   └── README.md           # Test dataset documentation
│
└── tests/
    ├── test_reportsmith.py
    └── test_sample_datasets.py
```

## Installation

### Requirements

- Python 3.11 or newer
- Windows, macOS, or Linux

### Windows

Clone the repository:

```bash
git clone https://github.com/TerryTheKnight/ReportSmith.git
cd ReportSmith
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Install dependencies:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the application:

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL displayed in your terminal.

Upload `sample.csv` to explore the application.

### macOS / Linux

```bash
git clone https://github.com/TerryTheKnight/ReportSmith.git
cd ReportSmith

python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Running Tests

Run the automated test suite:

```bash
python -m unittest discover -s tests -v
```

To regenerate the larger synthetic datasets:

```bash
python generate_test_data.py
```

See `test_data/README.md` for details about the included test scenarios.

## Current Limitations

ReportSmith is an educational data-analysis tool, not a replacement for professional data validation or statistical review.

Currently:
- It identifies common structural data-quality issues but does not automatically repair records.
- It does not determine the meaning of missing values.
- It does not perform statistical significance testing.
- Excel `.xls` files are not supported.
- PDF report generation is not implemented.

## Roadmap

Planned improvements:

- [ ] Excel worksheet selection.
- [ ] Downloadable PDF reports.
- [ ] More advanced date-aware visualizations.
- [ ] Configurable data-quality validation rules.
- [ ] More visualization options.
- [ ] Expanded automated test coverage.

## Privacy

Uploaded datasets are processed within the application session. ReportSmith does not save uploaded files to disk.

Avoid uploading confidential or sensitive datasets to any deployment unless its security and hosting configuration have been reviewed.

## License

No open-source license has been selected yet.

A license should be added before granting others explicit permission to reuse, modify, or distribute the project.

---

**Built with Python, Streamlit, Pandas, NumPy, and Matplotlib.**