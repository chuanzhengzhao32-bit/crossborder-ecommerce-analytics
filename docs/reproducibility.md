# Technical Reproducibility Notes

This file keeps technical setup details outside the portfolio homepage.

## How to rebuild the project locally

```powershell
python -m pip install -r requirements.txt
python scripts/download_source_data.py
python scripts/prepare_orders.py
python scripts/validate_source_data.py
python scripts/generate_extensions.py
python scripts/build_database.py
python scripts/run_analysis.py
python scripts/validate_data.py
python scripts/export_samples.py
```

## Data policy

- `data/raw/` is not committed. It contains the downloaded source workbook.
- `data/processed/` is not committed. It contains generated full-size CSV and SQLite outputs.
- `data/sample/` is committed. It contains small preview CSVs for repository reviewers.

## Generated local tables

| Table | Grain | Purpose |
|---|---|---|
| `fact_order_lines` | transaction line | cleaned public order data |
| `dim_product` | SKU | category, SKU tier, synthetic unit cost |
| `dim_market` | country | market region, channel, fee/logistics assumptions |
| `fact_order_profit` | transaction line | revenue, cost, fees, gross profit, pre-ad contribution |
| `fact_ad_spend_monthly` | month-market-channel-category | synthetic ad spend, attributed revenue, ROAS |
| `fact_inventory_monthly` | month-SKU | stock, turnover days, stockout and slow-moving flags |

## Latest validation profile

- Order lines: 1,067,371.
- Product dimension rows: 4,916.
- Market rows: 43.
- Profit fact rows: 1,067,371.
- Monthly ad rows: 700.
- Monthly inventory rows: 19,314.
- Validation checks passed.
