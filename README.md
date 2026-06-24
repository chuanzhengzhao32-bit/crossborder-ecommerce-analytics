# Cross-Border E-commerce Analytics Hub

[中文说明](README.zh-CN.md) | English

This project is a hiring-oriented prototype of an integrated cross-border e-commerce analytics tool. It shows how platform exports or future APIs can be standardized into a reusable operating-review workflow: KPI calculation, profit analysis, ad-spend diagnostics, inventory risk detection, and downloadable business reviews.

The project is not positioned as a code tutorial. It is positioned as an analyst-built solution that business teams could reuse.

## Solution Concept

```text
Platform backend / CSV export / future API
  -> standardized order, cost, ad, and inventory tables
  -> automated data validation
  -> KPI and profit engine
  -> ad and inventory diagnostics
  -> Streamlit operating dashboard
  -> monthly business review export
```

The current MVP supports CSV/sample data. Connector stubs are included for future Shopify, Amazon, ERP, WMS, and ad-platform integrations.

> Data disclosure: transaction data is real public UCI Online Retail II data. Cost, advertising, and inventory fields are synthetic operating extensions for portfolio demonstration.

## What the Tool Demonstrates

| Business need | Tool capability |
|---|---|
| Recurring weekly/monthly reporting | Auto-generated KPI scorecard and monthly review |
| Sales, gross margin, fees, and contribution profit | Standard profit engine covering revenue, costs, fees, ads, and contribution profit |
| Market, channel, category, and SKU analysis | Segment-level profitability tables and visual review |
| Advertising efficiency review | Low-ROAS campaign diagnostics and budget-control suggestions |
| Inventory action management | Stockout-risk and slow-moving SKU detection |
| Multi-source integration mindset | CSV connector plus API connector stubs for future platform integration |
| BI/data-model readiness | SQL scripts, data dictionary, metric dictionary, model notes, and DAX measures |

## Dashboard Prototype

The Streamlit app provides:

- data-source selection using generated data, sample data, or uploaded CSV files;
- required-field validation;
- executive KPI snapshot;
- monthly revenue/profit trend;
- category and market profit views;
- low-ROAS campaign list;
- inventory action list;
- one-click Markdown business review export.

## Business Findings Example

The latest complete reporting month in the project is 2011-11, compared with 2011-10.

| Month | Valid orders | Revenue | Gross margin | Ad spend | Contribution profit | Contribution margin |
|---|---:|---:|---:|---:|---:|---:|
| 2011-10 | 2,040 | £1.15M | 40.0% | £26.1k | £225.1k | 19.5% |
| 2011-11 | 2,769 | £1.51M | 24.4% | £36.9k | £88.4k | 5.9% |

Key interpretation:

- Revenue increased, but contribution profit declined, so growth quality weakened.
- High-revenue categories are not necessarily high-profit categories.
- Ad budget should be reviewed together with contribution margin and inventory availability.
- Inventory actions should separate stockout-risk SKUs from slow-moving SKUs.

## Main Deliverables

- [Analytics Hub Streamlit App](app/streamlit_app.py)
- [System Design](docs/system_design.md)
- [Monthly Business Review](reports/monthly_business_review.md)
- [Interview Guide](docs/interview_guide.md)
- [Metric Dictionary](docs/metric_dictionary.md)
- [Data Dictionary](docs/data_dictionary.md)
- [Data Model Notes](docs/data_model.md)
- [Power BI DAX Measures](powerbi/dax_measures.dax)
- [Sample Data Preview](data/sample)

Technical setup and run notes are kept separately in [docs/reproducibility.md](docs/reproducibility.md), so the homepage remains focused on hiring review.

## Interview Pitch

I built a cross-border e-commerce analytics tool prototype that can standardize platform exports into operating metrics and business actions. It supports KPI reporting, contribution-profit analysis, ad-spend diagnostics, inventory risk detection, and downloadable business reviews. The current MVP uses CSV/sample data, while connector stubs show where Shopify, Amazon, ERP, WMS, or ad-platform APIs would be integrated in a real deployment.

## Source

UCI Machine Learning Repository: Online Retail II  
DOI: <https://doi.org/10.24432/C5CG6D>  
License: CC BY 4.0
