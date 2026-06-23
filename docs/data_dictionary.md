# Data Dictionary

## `fact_order_lines`

Real public transaction line table cleaned from UCI Online Retail II.

| Field | Type | Description |
|---|---|---|
| `transaction_line_id` | integer | generated unique transaction-line id |
| `invoice_no` | text | invoice/order number; values starting with `C` usually indicate cancellation |
| `stock_code` | text | product/SKU code |
| `description` | text | product description |
| `quantity` | integer | transaction quantity; returns may be negative |
| `invoice_datetime` | datetime | transaction timestamp |
| `invoice_date` | date | transaction date |
| `unit_price_gbp` | decimal | unit price in GBP |
| `line_revenue_gbp` | decimal | quantity × unit price; returns may be negative |
| `customer_id` | text | anonymized customer id; some records are missing |
| `country` | text | customer country |
| `is_cancellation` | boolean | invoice starts with `C` |
| `is_return_line` | boolean | negative quantity or cancellation |
| `is_valid_sale` | boolean | positive quantity, positive price, non-cancellation |
| `source_sheet` | text | source workbook sheet |

## `dim_product`

Synthetic product extension table derived from real SKU statistics.

| Field | Type | Description |
|---|---|---|
| `stock_code` | text | SKU code |
| `description` | text | most common product description |
| `category` | text | rule-based category assignment from description keywords |
| `sku_tier` | text | A/B/C/D tier by revenue percentile |
| `lifecycle_stage` | text | Core, Regular, New/Test, or Long Tail |
| `avg_unit_price_gbp` | decimal | average observed unit price |
| `unit_cost_gbp` | decimal | synthetic unit product cost |
| `active_months` | integer | number of months with sales |
| `total_quantity` | integer | total sold quantity |
| `total_revenue_gbp` | decimal | total valid sales revenue |

## `dim_market`

Synthetic market assumptions by country.

| Field | Type | Description |
|---|---|---|
| `country` | text | customer country |
| `market_region` | text | UK, Europe, North America, APAC, or Other |
| `shipping_zone` | text | logistics zone |
| `default_channel` | text | assumed primary channel: own_site, amazon, or shopify |
| `platform_fee_rate` | decimal | synthetic platform fee rate |
| `payment_fee_rate` | decimal | synthetic payment fee rate |
| `logistics_base_gbp_per_unit` | decimal | synthetic logistics cost per unit |

## `fact_order_profit`

Transaction-line profit table joining orders, product assumptions, and market assumptions.

| Field | Type | Description |
|---|---|---|
| `transaction_line_id` | integer | source line id |
| `invoice_no` | text | order/invoice number |
| `invoice_date` | date | transaction date |
| `invoice_month` | text | month in `YYYY-MM` format |
| `stock_code` | text | SKU code |
| `country` | text | customer country |
| `market_region` | text | market region |
| `default_channel` | text | assumed channel |
| `category` | text | product category |
| `sku_tier` | text | SKU tier |
| `quantity` | integer | transaction quantity |
| `unit_price_gbp` | decimal | unit price |
| `net_revenue_gbp` | decimal | valid sale revenue; zero for returns/cancellations |
| `refund_amount_gbp` | decimal | absolute return/cancellation amount |
| `product_cost_gbp` | decimal | synthetic product cost |
| `platform_fee_gbp` | decimal | synthetic platform fee |
| `payment_fee_gbp` | decimal | synthetic payment fee |
| `logistics_fee_gbp` | decimal | synthetic logistics fee |
| `gross_profit_gbp` | decimal | net revenue - product cost |
| `pre_ad_contribution_gbp` | decimal | gross profit - platform/payment/logistics fees |
| `is_valid_sale` | boolean | valid sale flag |
| `is_return_line` | boolean | return/cancellation flag |

## `fact_ad_spend_monthly`

Synthetic monthly ad-performance table.

| Field | Type | Description |
|---|---|---|
| `invoice_month` | text | month in `YYYY-MM` format |
| `market_region` | text | market region |
| `default_channel` | text | assumed advertising/sales channel |
| `category` | text | product category |
| `campaign_name` | text | generated campaign label |
| `ad_spend_gbp` | decimal | synthetic ad spend |
| `attributed_revenue_gbp` | decimal | revenue attributed to the campaign group |
| `attributed_order_lines` | integer | order-line count in the campaign group |
| `roas` | decimal | attributed revenue / ad spend |

## `fact_inventory_monthly`

Synthetic monthly SKU inventory snapshot.

| Field | Type | Description |
|---|---|---|
| `invoice_month` | text | month in `YYYY-MM` format |
| `stock_code` | text | SKU code |
| `category` | text | product category |
| `sku_tier` | text | SKU tier |
| `units_sold` | integer | units sold in the month |
| `cogs_gbp` | decimal | product cost of units sold |
| `revenue_gbp` | decimal | valid sales revenue |
| `opening_stock_units` | decimal | synthetic opening stock |
| `purchase_units` | decimal | synthetic replenishment quantity |
| `closing_stock_units` | decimal | synthetic closing stock |
| `avg_stock_units` | decimal | average of opening and closing stock |
| `inventory_value_gbp` | decimal | closing stock × unit cost |
| `turnover_days` | decimal | inventory turnover days |
| `stockout_flag` | boolean | likely stockout risk |
| `slow_moving_flag` | boolean | slow-moving stock risk |
| `replenishment_recommendation` | text | suggested inventory action |
