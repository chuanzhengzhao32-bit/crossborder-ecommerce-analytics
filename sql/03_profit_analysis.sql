-- Category and market profitability for the latest available month.

WITH latest_month AS (
  SELECT MAX(invoice_month) AS invoice_month
  FROM fact_order_profit
  WHERE is_valid_sale = 1
)
SELECT
  f.market_region,
  f.category,
  COUNT(DISTINCT f.invoice_no) AS valid_orders,
  ROUND(SUM(f.net_revenue_gbp), 2) AS revenue_gbp,
  ROUND(SUM(f.gross_profit_gbp), 2) AS gross_profit_gbp,
  ROUND(SUM(f.pre_ad_contribution_gbp), 2) AS pre_ad_contribution_gbp,
  ROUND(SUM(f.pre_ad_contribution_gbp) / NULLIF(SUM(f.net_revenue_gbp), 0), 4) AS pre_ad_contribution_margin
FROM fact_order_profit f
JOIN latest_month m ON f.invoice_month = m.invoice_month
WHERE f.is_valid_sale = 1
GROUP BY f.market_region, f.category
ORDER BY revenue_gbp DESC;
