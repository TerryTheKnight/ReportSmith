"""Unit tests for ReportSmith's data and report functions."""

import unittest
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd

from reportsmith import (
    build_html_report,
    build_quality_warnings,
    chart_insight,
    date_columns,
    descriptive_statistics,
    make_chart,
    read_uploaded_data,
)


class ReadUploadedDataTests(unittest.TestCase):
    def test_reads_csv(self):
        data = read_uploaded_data(b"name,score\nAda,9\n", "scores.csv")
        self.assertEqual(data.loc[0, "name"], "Ada")
        self.assertEqual(data.loc[0, "score"], 9)

    def test_rejects_unsupported_file_type(self):
        with self.assertRaisesRegex(ValueError, "Unsupported file type"):
            read_uploaded_data(b"data", "scores.xls")

    def test_reads_excel_xlsx(self):
        buffer = BytesIO()
        pd.DataFrame({"name": ["Ada"], "score": [9]}).to_excel(buffer, index=False)
        data = read_uploaded_data(buffer.getvalue(), "scores.xlsx")
        self.assertEqual(data.loc[0, "name"], "Ada")

    def test_empty_csv_returns_a_friendly_error(self):
        with self.assertRaisesRegex(ValueError, "Could not read"):
            read_uploaded_data(b"", "empty.csv")

    def test_header_only_csv_is_read_as_zero_rows(self):
        data = read_uploaded_data(b"name,score\n", "headers.csv")
        self.assertEqual(data.shape, (0, 2))


class QualityAndStatisticsTests(unittest.TestCase):
    def test_finds_missing_values_duplicate_rows_and_constant_columns(self):
        data = pd.DataFrame(
            {"score": [10, 10, None], "group": ["A", "A", "A"]}
        )
        warnings = build_quality_warnings(data)
        self.assertTrue(any("duplicate row" in warning for warning in warnings))
        self.assertTrue(any("missing value" in warning for warning in warnings))
        self.assertTrue(any("one distinct value" in warning for warning in warnings))

    def test_statistics_include_numeric_columns_only(self):
        data = pd.DataFrame({"score": [2, 4], "label": ["A", "B"]})
        summary = descriptive_statistics(data)
        self.assertIn("score", summary.index)
        self.assertNotIn("label", summary.index)
        self.assertEqual(summary.loc["score", "Mean"], 3)

    def test_date_text_is_suggested_for_a_trend_chart(self):
        data = pd.DataFrame({"date": ["2026-01-01", "2026-01-02"], "sales": [4, 7]})
        self.assertEqual(date_columns(data), ["date"])


class ReportTests(unittest.TestCase):
    def test_category_chart_handles_text_and_missing_values(self):
        data = pd.DataFrame({"team": ["North", None, "North", "South"]})
        chart = make_chart(data, "Category counts", "team")
        labels = [label.get_text() for label in chart.axes[0].get_yticklabels()]
        self.assertIn("(missing)", labels)
        self.assertIn("North", labels)
        import matplotlib.pyplot as plt

        plt.close(chart)

    def test_line_chart_sorts_date_strings_chronologically(self):
        data = pd.DataFrame({"date": ["2026-01-02", "2026-01-01"], "sales": [20, 10]})
        chart = make_chart(data, "Line chart", "date", "sales")
        x_values = chart.axes[0].lines[0].get_xdata()
        self.assertLess(x_values[0], x_values[1])
        import matplotlib.pyplot as plt

        plt.close(chart)

    def test_line_chart_aggregates_repeated_dates_and_explains_the_trend(self):
        data = pd.DataFrame(
            {"date": ["2026-01-02", "2026-01-01", "2026-01-01"], "sales": [20, 4, 6]}
        )
        chart = make_chart(data, "Line chart", "date", "sales", "Sum")
        y_values = chart.axes[0].lines[0].get_ydata()
        self.assertEqual(list(y_values), [10, 20])
        self.assertIn("rose", chart_insight(data, "Line chart", "date", "sales", "Sum"))
        plt.close(chart)

    def test_html_report_escapes_filename_and_embeds_chart(self):
        data = pd.DataFrame({"amount": [1, 2, 3]})
        chart = make_chart(data, "Histogram", "amount")
        report = build_html_report(
            "<unsafe>.csv", data, [], descriptive_statistics(data), chart, "3 usable values."
        )
        self.assertIn("&lt;unsafe&gt;.csv", report)
        self.assertIn("data:image/png;base64,", report)
        self.assertIn("Descriptive statistics", report)
        self.assertIn("3 usable values.", report)
        import matplotlib.pyplot as plt

        plt.close(chart)


if __name__ == "__main__":
    unittest.main()
