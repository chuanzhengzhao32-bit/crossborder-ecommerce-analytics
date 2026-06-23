"""Validate the full processed analytics dataset."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DB_PATH = PROCESSED / "ecommerce_analytics.sqlite"
OUTPUT = ROOT / "docs" / "validation_results.json"


def main() -> None:
    required_files = [
        "fact_order_lines.csv",
        "dim_product.csv",
        "dim_market.csv",
        "fact_order_profit.csv",
        "fact_ad_spend_monthly.csv",
        "fact_inventory_monthly.csv",
        "ecommerce_analytics.sqlite",
    ]
    checks: dict[str, bool | int | float | str] = {}
    checks["all_required_files_exist"] = all((PROCESSED / f).exists() for f in required_files[:-1]) and DB_PATH.exists()

    profit_sample = pd.read_csv(PROCESSED / "fact_order_profit.csv", nrows=100_000)
    checks["profit_has_no_negative_valid_revenue"] = bool(
        (profit_sample.loc[profit_sample["is_valid_sale"].eq(1), "net_revenue_gbp"] >= 0).all()
    )
    checks["profit_calculation_identity_sample"] = bool(
        (
            (
                profit_sample["gross_profit_gbp"]
                - (profit_sample["net_revenue_gbp"] - profit_sample["product_cost_gbp"])
            )
            .abs()
            .max()
            < 0.02
        )
    )

    ads = pd.read_csv(PROCESSED / "fact_ad_spend_monthly.csv")
    checks["ad_spend_positive"] = bool((ads["ad_spend_gbp"] > 0).all())
    checks["roas_positive"] = bool((ads["roas"] > 0).all())

    inventory = pd.read_csv(PROCESSED / "fact_inventory_monthly.csv")
    checks["inventory_non_negative"] = bool(
        (inventory[["opening_stock_units", "purchase_units", "closing_stock_units", "inventory_value_gbp"]] >= 0)
        .all()
        .all()
    )
    checks["inventory_has_action_flags"] = bool(
        inventory["stockout_flag"].sum() > 0 and inventory["slow_moving_flag"].sum() > 0
    )

    with sqlite3.connect(DB_PATH) as conn:
        table_counts = dict(
            conn.execute(
                """
                SELECT name, -1
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        )
        for table in list(table_counts):
            table_counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    checks["sqlite_table_count"] = len(table_counts)
    checks["sqlite_fact_order_profit_rows"] = table_counts.get("fact_order_profit", 0)
    checks["all_checks_passed"] = all(v for k, v in checks.items() if isinstance(v, bool))
    result = {"checks": checks, "sqlite_table_counts": table_counts}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not checks["all_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
