"""Validate the cleaned UCI transaction layer before downstream modeling."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "fact_order_lines.csv"
PROFILE = ROOT / "docs" / "source_profile.json"

REQUIRED_COLUMNS = {
    "transaction_line_id",
    "invoice_no",
    "stock_code",
    "quantity",
    "invoice_datetime",
    "unit_price_gbp",
    "line_revenue_gbp",
    "country",
    "is_cancellation",
    "is_return_line",
    "is_valid_sale",
}


def main() -> None:
    if not DATA.exists() or not PROFILE.exists():
        raise FileNotFoundError("Run scripts/prepare_orders.py before validation.")

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    expected_rows = profile["usable_rows_written"]
    rows = 0
    previous_id = 0
    valid_sales = 0
    return_lines = 0
    invalid_revenue_rows = 0

    with DATA.open("r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        missing_columns = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing_columns:
            raise AssertionError(f"Missing columns: {sorted(missing_columns)}")

        for row in reader:
            rows += 1
            line_id = int(row["transaction_line_id"])
            if line_id != previous_id + 1:
                raise AssertionError(f"Non-sequential transaction_line_id at {line_id}")
            previous_id = line_id

            quantity = int(row["quantity"])
            price = float(row["unit_price_gbp"])
            revenue = float(row["line_revenue_gbp"])
            if abs(revenue - quantity * price) > 0.011:
                invalid_revenue_rows += 1

            valid_sales += int(row["is_valid_sale"])
            return_lines += int(row["is_return_line"])

    checks = {
        "row_count_matches_profile": rows == expected_rows,
        "line_ids_are_sequential": previous_id == rows,
        "line_revenue_matches_quantity_times_price": invalid_revenue_rows == 0,
        "valid_sale_count_matches_profile": valid_sales == profile["valid_sale_lines"],
        "return_line_count_matches_profile": return_lines == profile["return_lines"],
        "date_range_present": bool(profile["date_min"] and profile["date_max"]),
        "country_count_positive": profile["distinct_countries"] > 0,
        "stock_code_count_positive": profile["distinct_stock_codes"] > 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    print(json.dumps({"rows_checked": rows, "checks": checks}, indent=2))
    if failed:
        raise AssertionError(f"Validation failed: {failed}")
    print("Source data validation passed.")


if __name__ == "__main__":
    main()

