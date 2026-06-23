# Cross-Border E-commerce Monthly Business Review

## Executive Summary

- **2011-11 revenue was £1.51M, 30.7% versus 2011-10.** Contribution profit after simulated ad spend was £88.4k, -60.7% versus the prior month.
- **The business remains revenue-concentrated by market and category.** UK and Europe are the main demand base, while category mix determines whether sales growth converts into contribution profit.
- **Ad efficiency needs budget discipline.** Campaigns with low ROAS should be capped or reallocated to higher-margin category/market combinations before scaling.
- **Inventory action should be SKU-specific.** Stockout-risk SKUs need replenishment, while slow-moving SKUs should be cleared or purchase orders reduced.

## Current KPI Scorecard

The KPI contract mirrors the job description: sales, gross profit, fee impact, ad efficiency, contribution profit, and inventory risk. The current readout compares the latest complete month (2011-11, 2011-11-01 to 2011-11-30) with the immediately previous month (2011-10). The raw source also contains a partial later month, but it is excluded from the headline comparison to avoid misleading month-over-month conclusions.

| invoice_month | valid_orders | revenue_gbp | gross_profit_gbp | gross_margin | ad_spend_gbp | contribution_profit_gbp | contribution_margin |
| ------------- | ------------ | ----------- | ---------------- | ------------ | ------------ | ----------------------- | ------------------- |
| 2011-10       | 2040         | £1.15M      | £462.2k          | 40.0%        | £26.1k       | £225.1k                 | 19.5%               |
| 2011-11       | 2769         | £1.51M      | £367.6k          | 24.4%        | £36.9k       | £88.4k                  | 5.9%                |

## Category profit determines whether growth is worth scaling

Revenue alone is not enough for operating decisions. The table below ranks categories by current-month revenue and adds pre-ad contribution margin, which shows how much margin remains before paid traffic.

| category            | revenue_gbp | gross_profit_gbp | pre_ad_contribution_gbp | pre_ad_contribution_margin |
| ------------------- | ----------- | ---------------- | ----------------------- | -------------------------- |
| General Merchandise | £639.7k     | -£145.8k         | -£243.3k                | -38.0%                     |
| Gift & Stationery   | £259.0k     | £180.2k          | £137.3k                 | 53.0%                      |
| Home Decor          | £234.0k     | £117.0k          | £80.7k                  | 34.5%                      |
| Kitchen & Dining    | £151.5k     | £81.3k           | £55.8k                  | 36.8%                      |
| Fashion Accessories | £116.9k     | £72.5k           | £53.9k                  | 46.1%                      |
| Seasonal            | £58.7k      | £33.7k           | £20.5k                  | 34.9%                      |
| Kids & Toys         | £49.7k      | £28.7k           | £20.6k                  | 41.3%                      |

**Implication:** scale categories that combine high revenue with acceptable contribution margin; discount or reprioritize categories that add revenue but consume margin after platform, payment, and logistics fees.

## Market mix changes the fee and logistics burden

Cross-border markets carry different platform and logistics assumptions. This cut helps explain why two markets with similar sales can produce different profit outcomes.

| market_region | valid_orders | revenue_gbp | pre_ad_contribution_gbp | pre_ad_contribution_margin |
| ------------- | ------------ | ----------- | ----------------------- | -------------------------- |
| UK            | 2490         | £1.33M      | £95.2k                  | 7.2%                       |
| Europe        | 265          | £165.6k     | £29.1k                  | 17.6%                      |
| APAC          | 9            | £16.0k      | £573                    | 3.6%                       |
| Other         | 5            | £2.5k       | £373                    | 15.0%                      |

**Implication:** UK/local traffic can usually tolerate lower order value, while long-haul markets need stricter minimum order value, bundle strategy, or ad-spend control to protect contribution profit.

## Advertising budget should be reallocated from low-ROAS combinations

The simulated ad table is built from revenue by month, market, channel, and category. It is suitable for demonstrating budget review logic, not for claiming true platform attribution.

Top spend campaigns:

| campaign_name                           | market_region | default_channel | category            | ad_spend_gbp | attributed_revenue_gbp | roas  |
| --------------------------------------- | ------------- | --------------- | ------------------- | ------------ | ---------------------- | ----- |
| UK \| General Merchandise \| own_site   | UK            | own_site        | General Merchandise | £12.5k       | £374.7k                | 29.9x |
| UK \| Gift & Stationery \| own_site     | UK            | own_site        | Gift & Stationery   | £5.1k        | £155.9k                | 30.7x |
| UK \| Home Decor \| own_site            | UK            | own_site        | Home Decor          | £4.0k        | £132.7k                | 32.8x |
| UK \| Fashion Accessories \| own_site   | UK            | own_site        | Fashion Accessories | £3.5k        | £94.0k                 | 26.8x |
| UK \| Kitchen & Dining \| own_site      | UK            | own_site        | Kitchen & Dining    | £3.0k        | £93.0k                 | 30.6x |
| Europe \| General Merchandise \| amazon | Europe        | amazon          | General Merchandise | £2.1k        | £50.4k                 | 24.2x |
| Europe \| Gift & Stationery \| amazon   | Europe        | amazon          | Gift & Stationery   | £1.6k        | £18.1k                 | 11.2x |
| Europe \| Kitchen & Dining \| amazon    | Europe        | amazon          | Kitchen & Dining    | £972         | £15.9k                 | 16.3x |
| APAC \| General Merchandise \| shopify  | APAC          | shopify         | General Merchandise | £815         | £9.8k                  | 12.0x |
| Europe \| Fashion Accessories \| amazon | Europe        | amazon          | Fashion Accessories | £678         | £7.5k                  | 11.1x |

Lowest ROAS campaigns with material spend:

| campaign_name                           | ad_spend_gbp | attributed_revenue_gbp | roas  |
| --------------------------------------- | ------------ | ---------------------- | ----- |
| Europe \| Fashion Accessories \| amazon | £678         | £7.5k                  | 11.1x |
| Europe \| Kids & Toys \| amazon         | £573         | £6.4k                  | 11.2x |
| Europe \| Gift & Stationery \| amazon   | £1.6k        | £18.1k                 | 11.2x |
| APAC \| General Merchandise \| shopify  | £815         | £9.8k                  | 12.0x |
| Other \| General Merchandise \| shopify | £92          | £1.2k                  | 12.8x |

**Implication:** cap or test down the lowest-ROAS campaigns for one review cycle, then move budget to combinations with stronger contribution margin and enough stock availability.

## Inventory risk is split between stockout and slow-moving SKUs

Inventory should not be managed only by total stock value. The useful question is which SKUs are likely to block sales and which SKUs are tying up cash.

| category            | active_skus | inventory_value_gbp | avg_turnover_days | stockout_skus | slow_moving_skus |
| ------------------- | ----------- | ------------------- | ----------------- | ------------- | ---------------- |
| General Merchandise | 399         | £782.0k             | 46.8              | 0             | 1                |
| Home Decor          | 129         | £120.1k             | 42.7              | 0             | 0                |
| Gift & Stationery   | 100         | £98.7k              | 47.3              | 0             | 0                |
| Kitchen & Dining    | 137         | £91.0k              | 44.7              | 1             | 0                |
| Fashion Accessories | 62          | £65.1k              | 50.9              | 0             | 0                |
| Kids & Toys         | 40          | £26.2k              | 43.9              | 0             | 0                |
| Seasonal            | 32          | £24.9k              | 39.6              | 0             | 0                |

Priority SKU actions:

| stock_code | category            | sku_tier | units_sold | closing_stock_units | turnover_days | stockout_flag | slow_moving_flag | replenishment_recommendation  |
| ---------- | ------------------- | -------- | ---------- | ------------------- | ------------- | ------------- | ---------------- | ----------------------------- |
| 37450      | Kitchen & Dining    | B        | 55         | 0.0                 | 10.91         | 1             | 0                | Replenish urgently            |
| 22174      | General Merchandise | A        | 421        | 1427.0              | 92.1          | 0             | 1                | Reduce purchase / clear stock |

**Implication:** replenish stockout-risk A/B-tier SKUs first; slow-moving SKUs should enter clearance, bundle, or purchase-suspension workflows.

## Recommended Next Steps

1. Reallocate 10-20% of ad budget away from the lowest-ROAS campaigns and review revenue plus contribution profit next month.
2. Create a replenishment list for stockout-risk A/B-tier SKUs and add expected lead time before final purchase decisions.
3. Build a Power BI dashboard with four pages: business overview, store/SKU profit, ad efficiency, and inventory action list.
4. Replace synthetic cost/ad/inventory assumptions with ERP, ad-platform, and warehouse exports if this project is adapted to a real company.

## Further Questions

- Can actual platform ad attribution be joined by campaign, SKU, and order date?
- Are purchase lead time and in-transit inventory available from ERP?
- Should returns be modeled by reason code, logistics carrier, or product quality issue?

## Caveats and Assumptions

- Transaction lines come from the public UCI Online Retail II dataset.
- Product cost, platform fees, payment fees, logistics fees, ad spend, and inventory are deterministic synthetic extensions.
- Results demonstrate analytical workflow and business interpretation; they are not real company operating results.
