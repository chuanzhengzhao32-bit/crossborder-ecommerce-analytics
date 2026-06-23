"""Export small GitHub-friendly sample CSVs from generated processed tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
SAMPLE = ROOT / "data" / "sample"

SAMPLE_TABLES = {
    "fact_order_profit.csv": 200,
    "dim_product.csv": 100,
    "dim_market.csv": 100,
    "fact_ad_spend_monthly.csv": 120,
    "fact_inventory_monthly.csv": 200,
}


def main() -> None:
    SAMPLE.mkdir(parents=True, exist_ok=True)
    for filename, rows in SAMPLE_TABLES.items():
        source = PROCESSED / filename
        if not source.exists():
            raise FileNotFoundError(f"Missing {source}. Run the pipeline first.")
        target = SAMPLE / filename
        pd.read_csv(source, nrows=rows).to_csv(target, index=False, encoding="utf-8-sig")
        print(f"Wrote sample {target}")


if __name__ == "__main__":
    main()
