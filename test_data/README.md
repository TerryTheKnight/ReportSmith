# ReportSmith sample test data

These files are synthetic and contain no real customer or business information. They are designed to exercise different parts of the app.

| File | What it is useful for checking |
| --- | --- |
| `sales_performance.csv` | Numeric summaries, category counts, line and scatter plots, missing values, duplicate rows, and a high outlier. |
| `messy_customer_records.csv` | Mixed text, inconsistent yes/no values, Unicode, missing values, a constant column, and numeric values stored as text. |
| `category_only.csv` | Category-count charts and quality checks when the file has no numeric columns. |
| `regional_metrics.xlsx` | Excel upload, date trends, multiple numeric columns, a missing value, and an outlier. |

The CSV files use UTF-8 with a byte-order mark so spreadsheet programs are more likely to display their text correctly. The data is deterministic and can be regenerated with:

```powershell
python generate_test_data.py
```

The app currently reads the first sheet in an Excel workbook. `regional_metrics.xlsx` therefore contains one data sheet.
