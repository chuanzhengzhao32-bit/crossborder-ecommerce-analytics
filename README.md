# Cross-Border E-commerce Profit & Inventory Analytics

This is a portfolio project for a cross-border e-commerce data analyst role. It demonstrates the full workflow from public transaction data to KPI reporting, SQL analysis, BI modeling, and management-level business review.

> Data disclosure: the transaction layer uses the real public UCI Online Retail II dataset. Product cost, platform/payment/logistics fees, ad spend, and inventory snapshots are deterministic synthetic extensions. The synthetic results demonstrate analytics methods and should not be presented as real company performance.

## Business Questions

The project answers the operating questions that commonly appear in cross-border e-commerce analytics work:

1. Which markets, channels, categories, and SKUs drive sales?
2. Does sales growth convert into gross profit and contribution profit?
3. Which ad combinations have low ROAS and should be capped or reallocated?
4. Which SKUs are at stockout risk, and which SKUs are slow-moving?
5. What actions should operations, marketing, purchasing, and finance take next month?

## Current Deliverables

- Reproducible download and cleaning workflow for UCI Online Retail II.
- Source profile and data-quality validation.
- Synthetic operating extension tables for cost, fees, ad spend, and inventory.
- SQLite database for SQL analysis.
- SQL scripts for KPI, profit, and inventory analysis.
- Power BI model notes and DAX measure definitions.
- Monthly business review report with executive summary and action recommendations.
- Interview guide explaining how to present the project honestly.

## Data Pipeline

```text
UCI Online Retail II workbook
  -> fact_order_lines.csv
  -> product / market / profit / ads / inventory extension tables
  -> ecommerce_analytics.sqlite
  -> SQL analysis + monthly business review + Power BI model
```

## Repository Structure

```text
crossborder-ecommerce-analytics/
├─ README.md
├─ requirements.txt
├─ data/
│  ├─ raw/              # ignored; source workbook is downloaded here
│  ├─ processed/        # ignored; generated CSV/SQLite files are written here
│  └─ sample/           # committed small CSV previews for GitHub reviewers
├─ scripts/
│  ├─ download_source_data.py
│  ├─ prepare_orders.py
│  ├─ generate_extensions.py
│  ├─ build_database.py
│  ├─ run_analysis.py
│  ├─ export_samples.py
│  ├─ validate_source_data.py
│  └─ validate_data.py
├─ sql/
│  ├─ 01_schema.sql
│  ├─ 02_kpi_analysis.sql
│  ├─ 03_profit_analysis.sql
│  └─ 04_inventory_analysis.sql
├─ docs/
│  ├─ source_and_license.md
│  ├─ source_profile.json
│  ├─ extension_profile.json
│  ├─ validation_results.json
│  ├─ data_dictionary.md
│  ├─ metric_dictionary.md
│  ├─ data_model.md
│  └─ interview_guide.md
├─ powerbi/
│  ├─ README.md
│  └─ dax_measures.dax
├─ reports/
│  ├─ monthly_business_review.md
│  └─ analysis_summary.json
└─ tests/
   └─ test_data_quality.py
```

## How to Run

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

The generated raw and processed datasets are intentionally ignored by Git because the workbook and full CSV outputs are large. Anyone can rebuild them by running the scripts above.

Small table previews are committed under [data/sample](data/sample).

## Generated Tables

After the full pipeline runs, the local SQLite database contains:

| Table | Grain | Purpose |
|---|---|---|
| `fact_order_lines` | transaction line | cleaned public order data |
| `dim_product` | SKU | category, SKU tier, synthetic unit cost |
| `dim_market` | country | market region, channel, fee/logistics assumptions |
| `fact_order_profit` | transaction line | revenue, cost, fees, gross profit, pre-ad contribution |
| `fact_ad_spend_monthly` | month-market-channel-category | synthetic ad spend, attributed revenue, ROAS |
| `fact_inventory_monthly` | month-SKU | stock, turnover days, stockout and slow-moving flags |

## KPI Framework

| KPI | Definition |
|---|---|
| Revenue | valid sale line revenue |
| Gross Profit | revenue - product cost |
| Gross Margin | gross profit / revenue |
| Pre-Ad Contribution | gross profit - platform fee - payment fee - logistics fee |
| Contribution Profit | pre-ad contribution - ad spend |
| Contribution Margin | contribution profit / revenue |
| ROAS | attributed revenue / ad spend |
| Inventory Turnover Days | average inventory cost / COGS × days |
| Stockout Flag | closing stock below short-term demand threshold |
| Slow-Moving Flag | high turnover days with material stock balance |

Full definitions are in [docs/metric_dictionary.md](docs/metric_dictionary.md).

## Latest Local Run

The latest generated profile contains:

- 1,067,371 order lines.
- 4,916 product dimension rows.
- 43 country/market rows.
- 1,067,371 profit fact rows.
- 700 monthly ad-spend rows.
- 19,314 monthly inventory rows.
- All validation checks passed.

The business review uses 2011-11 as the latest complete month and compares it with 2011-10. The partial 2011-12 source period is excluded from headline month-over-month interpretation.

## Power BI Dashboard Plan

1. Business Overview: revenue, orders, gross margin, contribution profit, trend.
2. Store/SKU Profit: category, SKU tier, market, and channel profitability.
3. Ad Efficiency: spend, attributed revenue, ROAS, low-efficiency campaigns.
4. Inventory Action List: stockout risk, slow-moving SKUs, turnover days, replenishment recommendation.

## Interview Positioning

Use this project as a realistic analyst portfolio project:

- Say clearly which data is public and which data is synthetic.
- Emphasize the business logic: cost model, fee model, ROAS, contribution profit, inventory actions.
- Explain that in a real company the synthetic tables would be replaced by ERP, finance, ad-platform, platform backend, and warehouse exports.
- Do not claim the synthetic profit or inventory numbers as real company performance.

## Source

UCI Machine Learning Repository: Online Retail II  
Dataset DOI: <https://doi.org/10.24432/C5CG6D>  
License: CC BY 4.0
