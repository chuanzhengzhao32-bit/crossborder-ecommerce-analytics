# Interview Guide

## 60-second project pitch

I built a cross-border e-commerce analytics project around public UCI transaction data. The original dataset only contains order lines, so I kept the real transaction layer separate and added clearly labeled synthetic operating tables for product cost, platform fees, ad spend, and inventory snapshots. The goal is to reproduce the work of a cross-border e-commerce data analyst: monthly sales and profit reporting, SKU/channel profitability, ROAS review, inventory turnover, stockout risk, and action recommendations.

## What this project demonstrates

- I can clean real order data and keep a data-quality profile.
- I can define business metrics such as gross margin, contribution profit, ROAS, inventory turnover days, stockout flags, and slow-moving stock.
- I can build a simple star-model structure for BI reporting.
- I can write SQL for monthly KPI reporting, profit analysis, and inventory action lists.
- I can translate analysis into business actions instead of only showing charts.

## How to answer the synthetic-data question

The order data is real public transaction data from UCI Online Retail II. Cost, ad spend, and inventory are simulated because the public source does not include company ERP, ad-platform, or warehouse exports. I used deterministic assumptions and disclosed them in the project. In a real company, I would replace those synthetic tables with ERP, platform backend, finance, ad account, and WMS exports.

## Questions the interviewer may ask

### Why use contribution profit instead of only gross profit?

Gross profit only subtracts product cost. Cross-border e-commerce also has platform fees, payment fees, logistics, and advertising. Contribution profit is closer to the operating question: after variable costs and traffic cost, which market/SKU/channel is still worth scaling?

### How would you improve this in a real company?

I would connect ERP product cost, ad-platform spend, warehouse inventory snapshots, and finance settlement data. Then I would validate joins by order ID/SKU/date, reconcile monthly totals against finance, and build a Power BI dashboard for weekly and monthly reviews.

### What should the business do with the report?

Use it to reallocate ad budget, replenish high-sales stockout-risk SKUs, reduce purchase orders for slow-moving SKUs, and monitor whether revenue growth converts into contribution profit.
