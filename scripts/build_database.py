"""Build a local SQLite database from processed project CSV files."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DB_PATH = PROCESSED / "ecommerce_analytics.sqlite"

TABLE_FILES = {
    "fact_order_lines": "fact_order_lines.csv",
    "dim_product": "dim_product.csv",
    "dim_market": "dim_market.csv",
    "fact_order_profit": "fact_order_profit.csv",
    "fact_ad_spend_monthly": "fact_ad_spend_monthly.csv",
    "fact_inventory_monthly": "fact_inventory_monthly.csv",
}


def main() -> None:
    missing = [name for name in TABLE_FILES.values() if not (PROCESSED / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing processed CSV files: {missing}")

    with sqlite3.connect(DB_PATH) as conn:
        for table, filename in TABLE_FILES.items():
            csv_path = PROCESSED / filename
            conn.execute(f'DROP TABLE IF EXISTS "{table}"')
            first_chunk = True
            for chunk in pd.read_csv(csv_path, chunksize=200_000):
                chunk.to_sql(table, conn, if_exists="replace" if first_chunk else "append", index=False)
                first_chunk = False
            print(f"Loaded {table} from {csv_path.name}")

        conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_order_profit_month ON fact_order_profit(invoice_month);
            CREATE INDEX IF NOT EXISTS idx_order_profit_sku ON fact_order_profit(stock_code);
            CREATE INDEX IF NOT EXISTS idx_order_profit_country ON fact_order_profit(country);
            CREATE INDEX IF NOT EXISTS idx_ads_month ON fact_ad_spend_monthly(invoice_month);
            CREATE INDEX IF NOT EXISTS idx_inventory_month_sku ON fact_inventory_monthly(invoice_month, stock_code);
            """
        )

    print(f"Wrote {DB_PATH}")


if __name__ == "__main__":
    main()
