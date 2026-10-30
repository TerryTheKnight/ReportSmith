"""Data reading, checks, summaries, charts, and HTML report generation."""

from __future__ import annotations

import base64
from html import escape
from io import BytesIO

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def read_uploaded_data(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Read a supported upload into a DataFrame, with a friendly error message."""
    suffix = filename.lower().rsplit(".", maxsplit=1)[-1] if "." in filename else ""
    try:
        if suffix == "csv":
            return pd.read_csv(BytesIO(file_bytes))
        if suffix == "xlsx":
            return pd.read_excel(BytesIO(file_bytes), engine="openpyxl")
    except ImportError as error:
        raise ImportError("Excel support needs openpyxl. Install the project dependencies and try again.") from error
    except (ValueError, OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Could not read '{filename}'. Check that it is a valid CSV or Excel file.") from error
    raise ValueError("Unsupported file type. Please upload a CSV or Excel (.xlsx) file.")


def build_quality_warnings(data: pd.DataFrame) -> list[str]:
    """Return plain-language warnings for common data-quality issues."""
    warnings: list[str] = []
    if data.empty:
        warnings.append("The dataset has no data rows.")
    if data.columns.empty:
        warnings.append("The dataset has no columns.")

    duplicate_rows = int(data.duplicated().sum()) if not data.empty else 0
    if duplicate_rows:
        warnings.append(f"{duplicate_rows:,} duplicate row(s) found.")

    for column in data.columns:
        missing = int(data[column].isna().sum())
        if missing:
            percent = missing / max(len(data), 1) * 100
            warnings.append(f"'{column}' has {missing:,} missing value(s) ({percent:.1f}% of rows).")
        if not data.empty and data[column].nunique(dropna=True) <= 1:
            warnings.append(f"'{column}' has only one distinct value (or none).")
    return warnings


def descriptive_statistics(data: pd.DataFrame) -> pd.DataFrame:
    """Summarize numeric columns with count, mean, spread, and range."""
    numeric = data.select_dtypes(include="number")
    if numeric.empty:
        return pd.DataFrame()
    summary = numeric.describe().T
    summary = summary.rename(
        columns={"count": "Count", "mean": "Mean", "std": "Std. dev.", "min": "Min", "max": "Max"}
    )
    summary.index.name = "Column"
    return summary.round(2)


def date_columns(data: pd.DataFrame) -> list[str]:
    """Find date or date-like columns so trend charts can suggest them first."""
    candidates: list[str] = []
    for column in data.columns:
        values = data[column].dropna()
        if values.empty:
            continue
        if pd.api.types.is_datetime64_any_dtype(values):
            candidates.append(column)
        elif not pd.api.types.is_numeric_dtype(values):
            parsed = pd.to_datetime(values, errors="coerce", utc=True)
            if parsed.notna().mean() >= 0.8:
                candidates.append(column)
    return candidates


def _line_data(
    data: pd.DataFrame, x_column: str, y_column: str, aggregation: str
) -> tuple[pd.DataFrame, bool]:
    """Clean and aggregate repeated x values for a less cluttered trend line."""
    plot_data = data[[x_column, y_column]].dropna().copy()
    x_values = plot_data[x_column]
    is_date_axis = pd.api.types.is_datetime64_any_dtype(x_values)
    if is_date_axis:
        plot_data[x_column] = pd.to_datetime(x_values, errors="coerce", utc=True).dt.tz_convert(None)
    elif not pd.api.types.is_numeric_dtype(x_values):
        parsed_dates = pd.to_datetime(x_values, errors="coerce", utc=True)
        if len(parsed_dates) and parsed_dates.notna().mean() >= 0.8:
            plot_data[x_column] = parsed_dates.dt.tz_convert(None)
            is_date_axis = True
        else:
            plot_data[x_column] = x_values.astype(str)

    aggregate_name = "sum" if aggregation == "Sum" else "mean"
    grouped = plot_data.groupby(x_column, as_index=False, sort=is_date_axis or pd.api.types.is_numeric_dtype(plot_data[x_column]))[y_column].agg(aggregate_name)
    if is_date_axis:
        grouped = grouped.sort_values(x_column)
    return grouped, is_date_axis


def make_chart(
    data: pd.DataFrame,
    chart_kind: str,
    x_column: str,
    y_column: str | None = None,
    aggregation: str = "Mean",
) -> plt.Figure:
    """Create a chart using the selected columns."""
    figure, axis = plt.subplots(figsize=(9, 5.2), layout="constrained")
    figure.patch.set_facecolor("#ffffff")
    axis.set_facecolor("#ffffff")
    axis.spines[["top", "right"]].set_visible(False)
    if chart_kind == "Histogram":
        values = pd.to_numeric(data[x_column], errors="coerce").dropna()
        if values.empty:
            axis.text(0.5, 0.5, "No numeric values to chart", ha="center", va="center", transform=axis.transAxes)
            axis.set_axis_off()
            return figure
        axis.hist(values, bins="auto", color="#496fbd", edgecolor="white", alpha=0.9)
        axis.axvline(values.mean(), color="#e07a32", linewidth=2, linestyle="--", label=f"Mean: {values.mean():,.2f}")
        axis.axvline(values.median(), color="#198a7a", linewidth=2, linestyle=":", label=f"Median: {values.median():,.2f}")
        axis.legend(frameon=False)
        axis.set_xlabel(x_column)
        axis.set_ylabel("Number of rows")
        axis.set_title(f"How {x_column} values are distributed", loc="left", weight="bold", pad=14)
    elif chart_kind == "Category counts":
        categories = data[x_column].fillna("(missing)").astype(str)
        counts = categories.value_counts().head(15).sort_values()
        bars = axis.barh(counts.index, counts.values, color="#496fbd", height=0.7)
        total = max(len(categories), 1)
        labels = [f"{count:,}  ·  {count / total:.0%}" for count in counts.values]
        axis.bar_label(bars, labels=labels, padding=5, fontsize=9, color="#364152")
        axis.set_xlim(0, max(counts.values, default=1) * 1.35)
        axis.set_xlabel("Number of rows  ·  share of dataset shown on bars")
        axis.set_ylabel(x_column)
        axis.set_title(f"Most common {x_column} values", loc="left", weight="bold", pad=14)
    elif chart_kind == "Line chart":
        if y_column is None:
            raise ValueError("A line chart needs a numeric values column.")
        plot_data, is_date_axis = _line_data(data, x_column, y_column, aggregation)
        axis.plot(plot_data[x_column], plot_data[y_column], color="#3157a4", linewidth=2.4, marker="o", markersize=4)
        axis.set_xlabel(x_column)
        axis.set_ylabel(f"{aggregation} {y_column.lower()}")
        axis.set_title(f"{aggregation} {y_column} over {x_column}", loc="left", weight="bold", pad=14)
        if is_date_axis:
            figure.autofmt_xdate(rotation=25, ha="right")
        elif not pd.api.types.is_numeric_dtype(plot_data[x_column]):
            axis.tick_params(axis="x", labelrotation=35)
    elif chart_kind == "Scatter plot":
        if y_column is None:
            raise ValueError("A scatter plot needs two numeric columns.")
        points = data[[x_column, y_column]].apply(pd.to_numeric, errors="coerce").dropna()
        axis.scatter(points[x_column], points[y_column], color="#496fbd", alpha=0.55, edgecolors="white", linewidths=0.4)
        if len(points) >= 2 and points[x_column].nunique() > 1:
            slope, intercept = np.polyfit(points[x_column], points[y_column], 1)
            x_line = pd.Series([points[x_column].min(), points[x_column].max()])
            axis.plot(x_line, slope * x_line + intercept, color="#e07a32", linewidth=2, linestyle="--", label="Linear trend")
            axis.legend(frameon=False)
        axis.set_xlabel(x_column)
        axis.set_ylabel(y_column)
        axis.set_title(f"Is there a relationship? {y_column} vs. {x_column}", loc="left", weight="bold", pad=14)
    else:
        raise ValueError(f"Unknown chart type: {chart_kind}")

    if chart_kind == "Category counts":
        axis.grid(axis="x", alpha=0.2)
    elif chart_kind == "Scatter plot":
        axis.grid(True, alpha=0.2)
    else:
        axis.grid(axis="y", alpha=0.2)
    axis.set_axisbelow(True)
    return figure


def chart_insight(
    data: pd.DataFrame,
    chart_kind: str,
    x_column: str,
    y_column: str | None = None,
    aggregation: str = "Mean",
) -> str:
    """Return a short plain-language reading of the current chart."""
    if chart_kind == "Histogram":
        values = pd.to_numeric(data[x_column], errors="coerce").dropna()
        if values.empty:
            return "No usable numeric values were found in this column."
        return (
            f"{len(values):,} usable values. The average is {values.mean():,.2f}; "
            f"the middle value is {values.median():,.2f}."
        )
    if chart_kind == "Category counts":
        categories = data[x_column].fillna("(missing)").astype(str)
        counts = categories.value_counts()
        if counts.empty:
            return "No category values were found."
        return f"Most common: {counts.index[0]} ({counts.iloc[0]:,} rows, {counts.iloc[0] / max(len(categories), 1):.0%} of the dataset)."
    if chart_kind == "Line chart" and y_column is not None:
        grouped, _ = _line_data(data, x_column, y_column, aggregation)
        if grouped.empty:
            return "No complete x and y values were found for this trend."
        if len(grouped) == 1:
            return f"Only one {x_column} group has a usable value. Add more time points or groups to see a trend."
        first = float(grouped[y_column].iloc[0])
        last = float(grouped[y_column].iloc[-1])
        delta = last - first
        direction = "rose" if delta > 0 else "fell" if delta < 0 else "stayed level"
        return f"Using {aggregation.lower()} values by {x_column}, the measure {direction} from {first:,.2f} to {last:,.2f}."
    if chart_kind == "Scatter plot" and y_column is not None:
        points = data[[x_column, y_column]].apply(pd.to_numeric, errors="coerce").dropna()
        if len(points) < 2 or points[x_column].nunique() < 2 or points[y_column].nunique() < 2:
            return "There are not enough varied numeric points to estimate a relationship."
        correlation = points[x_column].corr(points[y_column])
        strength = "strong" if abs(correlation) >= 0.7 else "moderate" if abs(correlation) >= 0.4 else "weak"
        direction = "positive" if correlation > 0 else "negative" if correlation < 0 else "none"
        return f"The values show a {strength} {direction} association (correlation {correlation:.2f}). Association does not prove cause and effect."
    return ""


def build_html_report(
    filename: str,
    data: pd.DataFrame,
    warnings: list[str],
    statistics: pd.DataFrame,
    chart: plt.Figure | None,
    chart_description: str = "",
) -> str:
    """Build a self-contained HTML report with an embedded chart."""
    safe_name = escape(filename)
    warning_markup = (
        "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in warnings) + "</ul>"
        if warnings
        else "<p class='good'>No basic data-quality issues found.</p>"
    )
    stats_markup = statistics.to_html(classes="data-table", border=0, float_format=lambda value: f"{value:,.2f}") if not statistics.empty else "<p>No numeric columns found.</p>"
    preview_markup = data.head(20).to_html(index=False, classes="data-table", border=0, escape=True)
    chart_markup = "<p>No chart was selected or available.</p>"
    if chart is not None:
        image_buffer = BytesIO()
        chart.savefig(image_buffer, format="png", dpi=140, bbox_inches="tight")
        encoded = base64.b64encode(image_buffer.getvalue()).decode("ascii")
        chart_markup = f'<img class="chart" alt="Data chart" src="data:image/png;base64,{encoded}">'
    if chart_description:
        chart_markup += f"<p class='chart-description'>{escape(chart_description)}</p>"

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ReportSmith report — {safe_name}</title>
<style>
body{{font:16px/1.55 Arial,sans-serif;color:#192338;background:#f5f7fb;margin:0;padding:32px}}
main{{max-width:1000px;margin:auto;background:white;padding:36px;border-radius:16px;box-shadow:0 8px 32px #15264a12}}
h1,h2{{color:#163b78}}h2{{margin-top:32px}}.metrics{{display:flex;gap:16px;flex-wrap:wrap}}
.metric{{padding:16px 22px;background:#eef3ff;border-radius:10px;min-width:120px}}
.metric strong{{display:block;font-size:24px}}.good{{color:#087443}}li{{margin:8px 0}}
.data-table{{border-collapse:collapse;width:100%;font-size:14px;display:block;overflow-x:auto}}
.data-table th,.data-table td{{padding:9px 12px;border-bottom:1px solid #e3e8f0;text-align:left;white-space:nowrap}}
.data-table th{{background:#eef3ff}}.chart{{max-width:100%;height:auto}}
.note{{color:#65718a;font-size:13px}}
.chart-description{{padding:12px 16px;background:#eef3ff;border-radius:8px}}
</style></head><body><main>
<h1>ReportSmith data report</h1><p>Source file: <strong>{safe_name}</strong></p>
<div class="metrics"><div class="metric"><strong>{len(data):,}</strong>rows</div><div class="metric"><strong>{len(data.columns):,}</strong>columns</div><div class="metric"><strong>{len(warnings):,}</strong>quality warnings</div></div>
<h2>Data-quality checks</h2>{warning_markup}
<h2>Descriptive statistics</h2>{stats_markup}
<h2>Chart</h2>{chart_markup}
<h2>Data preview</h2>{preview_markup}<p class="note">Preview limited to the first 20 rows. Generated by ReportSmith.</p>
</main></body></html>"""
