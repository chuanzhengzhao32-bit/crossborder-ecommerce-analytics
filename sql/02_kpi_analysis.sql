-- Monthly KPI scorecard: revenue, gross margin, ad spend, contribution profit.

WITH profit AS (
  SELECT
    invoice_month,
    COUNT(DISTINCT invoice_no) AS valid_orders,
    SUM(net_revenue_gbp) AS revenue_gbp,
    SUM(gross_profit_gbp) AS gross_profit_gbp,
    SUM(pre_ad_contribution_gbp) AS pre_ad_contribution_gbp
  FROM fact_order_profit
  WHERE is_valid_sale = 1
  GROUP BY invoice_month
),
ads AS (
  SELECT
    invoice_month,
    SUM(ad_spend_gbp) AS ad_spend_gbp
  FROM fact_ad_spend_monthly
  GROUP BY invoice_month
)
SELECT
  p.invoice_month,
  p.valid_orders,
  ROUND(p.revenue_gbp, 2) AS revenue_gbp,
  ROUND(p.gross_profit_gbp, 2) AS gross_profit_gbp,
  ROUND(p.gross_profit_gbp / NULLIF(p.revenue_gbp, 0), 4) AS gross_margin,
  ROUND(COALESCE(a.ad_spend_gbp, 0), 2) AS ad_spend_gbp,
  ROUND(p.pre_ad_contribution_gbp - COALESCE(a.ad_spend_gbp, 0), 2) AS contribution_profit_gbp,
  ROUND((p.pre_ad_contribution_gbp - COALESCE(a.ad_spend_gbp, 0)) / NULLIF(p.revenue_gbp, 0), 4) AS contribution_margin
FROM profit p
LEFT JOIN ads a ON p.invoice_month = a.invoice_month
ORDER BY p.invoice_month;
