"""Smoke checks for the larger synthetic files shipped with the project."""

import unittest
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from reportsmith import (
    build_quality_warnings,
    descriptive_statistics,
    make_chart,
    read_uploaded_data,
)


DATA_DIR = Path(__file__).parent.parent / "test_data"


class SampleDatasetTests(unittest.TestCase):
    def load(self, filename):
        path = DATA_DIR / filename
        return read_uploaded_data(path.read_bytes(), path.name)

    def test_sales_file_loads_and_has_expected_quality_flags(self):
        data = self.load("sales_performance.csv")
        self.assertEqual(data.shape, (242, 13))
        warnings = build_quality_warnings(data)
        self.assertTrue(any("duplicate row" in warning for warning in warnings))
        self.assertTrue(any("missing value" in warning for warning in warnings))
        self.assertFalse(descriptive_statistics(data).empty)

    def test_messy_file_loads_and_exposes_numeric_text_limitation(self):
        data = self.load("messy_customer_records.csv")
        self.assertEqual(len(data), 121)
        self.assertEqual(descriptive_statistics(data).shape[0], 0)
        self.assertIn("age_text", data.columns)

    def test_category_only_file_can_make_a_chart_without_numeric_columns(self):
        data = self.load("category_only.csv")
        self.assertTrue(data.select_dtypes(include="number").empty)
        chart = make_chart(data, "Category counts", "request_type")
        self.assertGreater(len(chart.axes[0].patches), 0)
        plt.close(chart)

    def test_excel_file_loads_and_supports_visualizations(self):
        data = self.load("regional_metrics.xlsx")
        self.assertEqual(data.shape, (96, 5))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(data["month"]))
        chart = make_chart(data, "Line chart", "month", "revenue")
        self.assertEqual(len(chart.axes[0].lines), 1)
        plt.close(chart)


if __name__ == "__main__":
    unittest.main()
