# Data Model

## Grain

- `fact_order_lines`: one row per source transaction line.
- `fact_order_profit`: one row per transaction line with synthetic fee and cost fields.
- `fact_ad_spend_monthly`: one row per month, market, channel, and category.
- `fact_inventory_monthly`: one row per month and SKU.
- `dim_product`: one row per SKU.
- `dim_market`: one row per country.

## Recommended Power BI relationships

```text
dim_product[stock_code] 1 -> * fact_order_profit[stock_code]
dim_product[stock_code] 1 -> * fact_inventory_monthly[stock_code]
dim_market[country]     1 -> * fact_order_profit[country]
```

`fact_ad_spend_monthly` can be related through a composite semantic key in Power BI:

- `invoice_month`
- `market_region`
- `default_channel`
- `category`

For a beginner-friendly demo, it is acceptable to keep ad spend as a separate table and use visuals filtered by month, market, channel, and category.

## Analyst talking point

The source order table is real public data. The operating layer is synthetic because the public dataset does not include ERP cost, ad-platform spend, warehouse inventory, or platform fee exports. This separation is intentional: it proves the data modeling workflow without misrepresenting the source.
