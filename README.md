# Cross-Border E-commerce Analytics Portfolio

[中文说明](README.zh-CN.md) | English

This portfolio project demonstrates how a cross-border e-commerce data analyst can turn order, cost, advertising, and inventory data into business decisions. It is designed for hiring review: the focus is not on tool usage, but on analytical thinking, metric design, KPI reporting, and action recommendations.

## Project Summary

The project uses the public UCI Online Retail II transaction dataset as the real order layer, then adds clearly labeled synthetic operating data for product cost, platform fees, payment fees, logistics, ad spend, and inventory snapshots.

The goal is to reproduce a realistic e-commerce operating review:

- sales and order performance;
- gross margin and contribution profit;
- advertising spend and ROAS;
- category, market, and SKU profitability;
- inventory turnover, stockout risk, and slow-moving SKUs;
- monthly business review with next-step recommendations.

> Data disclosure: transaction data is real public data. Cost, advertising, and inventory data are simulated for portfolio demonstration and should not be interpreted as real company performance.

## Role Fit

| Hiring requirement | Portfolio evidence |
|---|---|
| Weekly/monthly business reporting | Monthly business review with KPI scorecard and recommendations |
| Sales, gross margin, fees, and contribution profit | Profit model covering revenue, product cost, platform/payment/logistics fees, ad spend, and contribution profit |
| Channel, market, category, and SKU analysis | Segment analysis by market, channel, category, and SKU tier |
| Advertising cost and profit analysis | ROAS and ad-spend efficiency review |
| Inventory turnover, stockout, and slow-moving analysis | Inventory action list and replenishment/clearance recommendations |
| Data dictionary and metric consistency | Data dictionary, metric dictionary, and model notes |
| SQL and BI readiness | SQL analysis scripts, Power BI model notes, and DAX measures |

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

## Deliverables

- [Monthly Business Review](reports/monthly_business_review.md)
- [Interview Guide](docs/interview_guide.md)
- [Metric Dictionary](docs/metric_dictionary.md)
- [Data Dictionary](docs/data_dictionary.md)
- [Data Model Notes](docs/data_model.md)
- [Power BI DAX Measures](powerbi/dax_measures.dax)
- [Sample Data Preview](data/sample)

Technical reproducibility notes are kept separately in [docs/reproducibility.md](docs/reproducibility.md) so the portfolio homepage stays focused on hiring review.

## Interview Pitch

I built a cross-border e-commerce analytics portfolio using real public order data and clearly labeled synthetic operating data. The project covers order cleaning, metric definition, SQL analysis, profit modeling, ad-spend review, inventory risk analysis, and a monthly business review. The main value is showing how I translate sales, cost, advertising, and inventory data into business actions such as budget reallocation, replenishment, and slow-moving stock control.

## Source

UCI Machine Learning Repository: Online Retail II  
DOI: <https://doi.org/10.24432/C5CG6D>  
License: CC BY 4.0
