-- Inventory risk list for the latest available month.

WITH latest_month AS (
  SELECT MAX(invoice_month) AS invoice_month
  FROM fact_inventory_monthly
)
SELECT
  i.stock_code,
  i.category,
  i.sku_tier,
  i.units_sold,
  i.closing_stock_units,
  ROUND(i.turnover_days, 1) AS turnover_days,
  i.stockout_flag,
  i.slow_moving_flag,
  i.replenishment_recommendation
FROM fact_inventory_monthly i
JOIN latest_month m ON i.invoice_month = m.invoice_month
WHERE i.stockout_flag = 1 OR i.slow_moving_flag = 1
ORDER BY i.stockout_flag DESC, i.slow_moving_flag DESC, i.units_sold DESC;
