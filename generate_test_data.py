"""Regenerate deterministic synthetic datasets for trying ReportSmith."""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


OUTPUT_DIR = Path(__file__).parent / "test_data"
RNG = random.Random(20261029)


def write_csv(filename: str, rows: list[dict[str, object]]) -> None:
    path = OUTPUT_DIR / filename
    with path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_sales_data() -> list[dict[str, object]]:
    regions = ["North", "South", "East", "West", "Central"]
    products = {
        "Electronics": [("Wireless headphones", 79.99), ("USB-C hub", 42.50), ("Webcam", 64.00)],
        "Home": [("Desk lamp", 35.00), ("Storage set", 28.75), ("Coffee grinder", 54.90)],
        "Outdoor": [("Daypack", 68.00), ("Water bottle", 22.00), ("Camp lantern", 47.25)],
        "Books": [("Python handbook", 39.50), ("Data stories", 31.00), ("Design notes", 26.75)],
    }
    rows: list[dict[str, object]] = []
    start = date(2025, 1, 1)
    for index in range(240):
        order_day = start + timedelta(days=RNG.randrange(365))
        category = RNG.choice(list(products))
        product, base_price = RNG.choice(products[category])
        units = RNG.randint(1, 8)
        price = round(base_price * RNG.uniform(0.92, 1.08), 2)
        discount = RNG.choice([0, 0, 0, 5, 10, 15, 20])
        revenue = round(units * price * (1 - discount / 100), 2)
        rows.append(
            {
                "order_id": f"ORD-{index + 1:04d}",
                "order_date": order_day.isoformat(),
                "region": RNG.choice(regions),
                "category": category,
                "product": product,
                "units": units,
                "unit_price": price,
                "discount_pct": discount,
                "revenue": revenue,
                "customer_type": RNG.choice(["New", "Returning", "Business"]),
                "satisfaction": RNG.randint(1, 5),
                "returned": RNG.choice(["No", "No", "No", "Yes"]),
                "sales_channel": RNG.choice(["Web", "Mobile app", "Retail partner"]),
            }
        )

    # Add realistic issues that should appear in ReportSmith's quality checks.
    rows[7]["region"] = ""
    rows[31]["satisfaction"] = ""
    rows[66]["product"] = ""
    rows[102]["revenue"] = 9999.99  # intentional high outlier
    rows[150]["region"] = "North"
    rows.append(rows[12].copy())  # intentional exact duplicate
    rows.append(rows[12].copy())
    return rows


def make_messy_customer_data() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(120):
        age: object = str(RNG.randint(18, 78))
        income: object = f"${RNG.randrange(24, 160) * 1000:,}"
        if index % 17 == 0:
            age = "unknown"
        if index % 13 == 0:
            income = "not provided"
        signup: object = (date(2023, 1, 1) + timedelta(days=RNG.randrange(900))).isoformat()
        if index % 19 == 0:
            signup = "not-a-date"
        rows.append(
            {
                "customer_id": f"C{index + 1:04d}",
                "age_text": age,
                "annual_income_text": income,
                "signup_date_text": signup,
                "segment": RNG.choice(["Starter", "Growth", "Enterprise", "Student"]),
                "country": RNG.choice(["India", "United States", "日本", "Deutschland", "Brazil"]),
                "marketing_opt_in": RNG.choice(["Yes", "No", "yes", "NO", "Unknown"]),
                "feedback": RNG.choice(["Quick delivery", "Needs follow-up", "😊", "", "Very helpful"]),
                "source_system": "legacy-import",  # intentional constant column
            }
        )

    rows[9]["country"] = ""
    rows[42]["feedback"] = ""
    rows[80]["annual_income_text"] = "$999,999,999"  # intentional outlier-like text
    rows.append(rows[5].copy())  # intentional exact duplicate
    return rows


def make_category_data() -> list[dict[str, object]]:
    departments = ["Support", "Engineering", "Finance", "People", "Operations", "Research"]
    priorities = ["Low", "Normal", "High", "Urgent"]
    countries = ["India", "Canada", "Japan", "Kenya", "Brazil", "Norway", "Chile"]
    rows: list[dict[str, object]] = []
    for index in range(120):
        rows.append(
            {
                "department": "" if index in {3, 17, 48} else RNG.choice(departments),
                "priority": RNG.choice(priorities),
                "status": RNG.choice(["Open", "In progress", "Blocked", "Closed"]),
                "country": RNG.choice(countries),
                "request_type": RNG.choice([f"Type {n:02d}" for n in range(1, 19)]),
            }
        )
    rows.append(rows[22].copy())  # intentional exact duplicate
    return rows


def make_excel_data() -> pd.DataFrame:
    rows = []
    for month_index in range(24):
        year = 2024 + (month_index + 1) // 12
        month = (month_index % 12) + 1
        for region_index, region in enumerate(["North", "South", "East", "West"]):
            trend = 8000 + month_index * 175 + region_index * 720
            seasonal = [0, 250, -150, 400, 650, 120, -300, 350, 100, 800, 1250, 1800][month - 1]
            rows.append(
                {
                    "month": date(year, month, 1),
                    "region": region,
                    "revenue": round(trend + seasonal + RNG.randrange(-600, 601), 2),
                    "orders": max(10, int((trend + seasonal) / 110 + RNG.randrange(-8, 9))),
                    "average_rating": round(RNG.uniform(3.2, 5.0), 1),
                }
            )
    frame = pd.DataFrame(rows)
    frame.loc[8, "average_rating"] = None
    frame.loc[51, "revenue"] = 75000  # intentional high outlier
    return frame


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    write_csv("sales_performance.csv", make_sales_data())
    write_csv("messy_customer_records.csv", make_messy_customer_data())
    write_csv("category_only.csv", make_category_data())
    make_excel_data().to_excel(OUTPUT_DIR / "regional_metrics.xlsx", index=False)
    print(f"Generated test files in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
