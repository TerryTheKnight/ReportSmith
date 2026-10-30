"""Streamlit interface for ReportSmith."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from reportsmith import (
    build_html_report,
    build_quality_warnings,
    chart_insight,
    date_columns,
    descriptive_statistics,
    make_chart,
    read_uploaded_data,
)


def main() -> None:
    st.set_page_config(page_title="ReportSmith | Data reports", page_icon="📊", layout="wide")
    st.title("📊 ReportSmith")
    st.caption("Turn a spreadsheet into a clear, shareable data report.")

    st.subheader("Start with your data")
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx"],
        help="Supported formats: CSV and Excel (.xlsx).",
        key="main_file_picker",
    )
    st.caption("Your file is processed for this session and is not saved by ReportSmith.")

    # Return from main() so the rest of the script can never read an empty uploader.
    if uploaded_file is None:
        st.info("Choose a file above to preview it and create your report.")
        st.markdown("**ReportSmith can create:** data-quality checks, summary statistics, charts, and downloadable reports.")
        return

    try:
        file_bytes = uploaded_file.getvalue()
        if not file_bytes:
            st.error("The selected file is empty. Choose a CSV or Excel file with data.")
            return
        data = read_uploaded_data(file_bytes, uploaded_file.name)
    except (ValueError, UnicodeDecodeError, pd.errors.ParserError, ImportError) as error:
        st.error(str(error))
        return

    if data.empty and len(data.columns) == 0:
        st.error("This file has no rows or columns. Upload a file containing a table with headers.")
        return

    warnings = build_quality_warnings(data)
    statistics = descriptive_statistics(data)

    st.subheader("Dataset overview")
    metric_columns = st.columns(3)
    metric_columns[0].metric("Rows", f"{len(data):,}")
    metric_columns[1].metric("Columns", f"{len(data.columns):,}")
    metric_columns[2].metric("Quality checks", f"{len(warnings)} warning{'s' if len(warnings) != 1 else ''}")

    overview_tab, quality_tab, stats_tab, charts_tab = st.tabs(
        ["Preview", "Data quality", "Statistics", "Charts"]
    )
    with overview_tab:
        st.dataframe(data.head(100), use_container_width=True, hide_index=True)
        if len(data) > 100:
            st.caption("Showing the first 100 rows.")
        types = pd.DataFrame({"Column": data.columns, "Type": data.dtypes.astype(str).values})
        st.dataframe(types, use_container_width=True, hide_index=True)

    with quality_tab:
        if warnings:
            for warning in warnings:
                st.warning(warning)
        else:
            st.success("No basic data-quality issues found.")

    with stats_tab:
        if statistics.empty:
            st.info("No numeric columns were found. Statistics are available for numeric columns.")
        else:
            st.dataframe(statistics, use_container_width=True)

    numeric_columns = data.select_dtypes(include="number").columns.tolist()
    preferred_numeric = next(
        (column for column in numeric_columns if any(word in str(column).lower() for word in ["revenue", "sales", "amount", "total"])),
        numeric_columns[0] if numeric_columns else None,
    )
    chart = None
    chart_description = ""
    with charts_tab:
        st.caption("Charts include labels and a short explanation to help you interpret the result.")
        chart_kind = st.selectbox(
            "Choose a chart",
            ["Histogram", "Category counts", "Line chart", "Scatter plot"],
        )

        if chart_kind == "Histogram":
            if not numeric_columns:
                st.info("A histogram needs a numeric column, such as sales, age, or score.")
            else:
                x_column = st.selectbox(
                    "Numeric column", numeric_columns,
                    index=numeric_columns.index(preferred_numeric), key="histogram_column",
                )
                chart = make_chart(data, chart_kind, x_column)
        elif chart_kind == "Category counts":
            x_column = st.selectbox("Category column", data.columns.tolist(), key="category_column")
            chart = make_chart(data, chart_kind, x_column)
        elif chart_kind == "Line chart":
            if not numeric_columns:
                st.info("A line chart needs at least one numeric column for its values.")
            else:
                time_columns = date_columns(data)
                x_options = time_columns + [column for column in data.columns if column not in time_columns]
                default_x = time_columns[0] if time_columns else x_options[0]
                x_column = st.selectbox(
                    "Horizontal axis", x_options, index=x_options.index(default_x), key="line_x"
                )
                y_column = st.selectbox(
                    "Values to track", numeric_columns,
                    index=numeric_columns.index(preferred_numeric), key="line_y",
                )
                aggregation = st.radio(
                    "When several rows share the same horizontal value, show their",
                    ["Sum", "Mean"], horizontal=True, key="line_aggregation",
                )
                st.caption("For a time trend, choose a date column. Repeated dates are combined before plotting.")
                chart = make_chart(data, chart_kind, x_column, y_column, aggregation)
        elif chart_kind == "Scatter plot":
            if len(numeric_columns) < 2:
                st.info("A scatter plot needs two numeric columns to compare.")
            else:
                left, right = st.columns(2)
                x_column = left.selectbox("Horizontal axis", numeric_columns, key="scatter_x")
                y_options = [column for column in numeric_columns if column != x_column] or numeric_columns
                y_column = right.selectbox("Vertical axis", y_options, key="scatter_y")
                chart = make_chart(data, chart_kind, x_column, y_column)

        if chart is not None:
            st.pyplot(chart, use_container_width=True)
            if chart_kind == "Line chart":
                chart_description = chart_insight(data, chart_kind, x_column, y_column, aggregation)
            elif chart_kind in {"Histogram", "Category counts"}:
                chart_description = chart_insight(data, chart_kind, x_column)
            else:
                chart_description = chart_insight(data, chart_kind, x_column, y_column)
            if chart_description:
                st.info(chart_description)

    st.divider()
    st.subheader("Download your report")
    download_left, download_right = st.columns(2)
    download_left.download_button(
        "Download analyzed data (CSV)",
        data=data.to_csv(index=False).encode("utf-8-sig"),
        file_name="reportsmith_data.csv",
        mime="text/csv",
        use_container_width=True,
    )
    html_report = build_html_report(
        uploaded_file.name, data, warnings, statistics, chart, chart_description
    )
    download_right.download_button(
        "Download report (HTML)",
        data=html_report.encode("utf-8"),
        file_name="reportsmith_report.html",
        mime="text/html",
        use_container_width=True,
    )

    plt.close("all")


if __name__ == "__main__":
    main()
