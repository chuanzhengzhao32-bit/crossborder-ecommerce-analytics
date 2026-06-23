"""Run KPI queries and write an executive monthly business review."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "processed" / "ecommerce_analytics.sqlite"
REPORT = ROOT / "reports" / "monthly_business_review.md"
SUMMARY_JSON = ROOT / "reports" / "analysis_summary.json"


def q(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)


def gbp(value: float) -> str:
    sign = "-" if value < 0 else ""
    value = abs(float(value))
    if value >= 1_000_000:
        return f"{sign}£{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{sign}£{value / 1_000:.1f}k"
    return f"{sign}£{value:.0f}"


def pct(value: float) -> str:
    return f"{float(value) * 100:.1f}%"


def table_md(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    text_df = df.fillna("").astype(str).map(lambda value: value.replace("|", "\\|"))
    headers = list(text_df.columns)
    rows = text_df.values.tolist()
    widths = [
        max(len(str(header)), *(len(str(row[i])) for row in rows))
        for i, header in enumerate(headers)
    ]
    header_line = "| " + " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    body = [
        "| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))) + " |"
        for row in rows
    ]
    return "\n".join([header_line, sep_line, *body])


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError("Run scripts/build_database.py first.")

    with sqlite3.connect(DB_PATH) as conn:
        full_months = q(
            conn,
            """
            SELECT
              invoice_month,
              COUNT(DISTINCT invoice_date) AS active_dates,
              MIN(invoice_date) AS min_date,
              MAX(invoice_date) AS max_date
            FROM fact_order_profit
            WHERE is_valid_sale = 1
            GROUP BY invoice_month
            HAVING active_dates >= 25
            ORDER BY invoice_month DESC
            """,
        )
        current_month = full_months.iloc[0]["invoice_month"]
        current_min_date = full_months.iloc[0]["min_date"]
        current_max_date = full_months.iloc[0]["max_date"]
        previous_month = q(
            conn,
            """
            SELECT invoice_month
            FROM fact_order_profit
            WHERE is_valid_sale = 1 AND invoice_month < ?
            GROUP BY invoice_month
            ORDER BY invoice_month DESC
            LIMIT 1
            """,
            (current_month,),
        ).iloc[0, 0]

        monthly = q(
            conn,
            """
            WITH profit AS (
              SELECT
                invoice_month,
                COUNT(DISTINCT invoice_no) AS valid_orders,
                SUM(net_revenue_gbp) AS revenue_gbp,
                SUM(gross_profit_gbp) AS gross_profit_gbp,
                SUM(pre_ad_contribution_gbp) AS pre_ad_contribution_gbp,
                SUM(refund_amount_gbp) AS refund_amount_gbp
              FROM fact_order_profit
              WHERE is_valid_sale = 1
              GROUP BY invoice_month
            ),
            ads AS (
              SELECT invoice_month, SUM(ad_spend_gbp) AS ad_spend_gbp
              FROM fact_ad_spend_monthly
              GROUP BY invoice_month
            )
            SELECT
              p.invoice_month,
              valid_orders,
              revenue_gbp,
              gross_profit_gbp,
              gross_profit_gbp / NULLIF(revenue_gbp, 0) AS gross_margin,
              ad_spend_gbp,
              pre_ad_contribution_gbp - COALESCE(ad_spend_gbp, 0) AS contribution_profit_gbp,
              (pre_ad_contribution_gbp - COALESCE(ad_spend_gbp, 0)) / NULLIF(revenue_gbp, 0) AS contribution_margin
            FROM profit p
            LEFT JOIN ads a ON p.invoice_month = a.invoice_month
            WHERE p.invoice_month IN (?, ?)
            ORDER BY p.invoice_month
            """,
            (previous_month, current_month),
        )

        current = monthly[monthly["invoice_month"].eq(current_month)].iloc[0]
        previous = monthly[monthly["invoice_month"].eq(previous_month)].iloc[0]
        revenue_change = current["revenue_gbp"] / previous["revenue_gbp"] - 1
        cp_change = current["contribution_profit_gbp"] / previous["contribution_profit_gbp"] - 1

        category = q(
            conn,
            """
            SELECT
              category,
              SUM(net_revenue_gbp) AS revenue_gbp,
              SUM(gross_profit_gbp) AS gross_profit_gbp,
              SUM(pre_ad_contribution_gbp) AS pre_ad_contribution_gbp,
              SUM(pre_ad_contribution_gbp) / NULLIF(SUM(net_revenue_gbp), 0) AS pre_ad_contribution_margin
            FROM fact_order_profit
            WHERE is_valid_sale = 1 AND invoice_month = ?
            GROUP BY category
            ORDER BY revenue_gbp DESC
            LIMIT 8
            """,
            (current_month,),
        )

        market = q(
            conn,
            """
            SELECT
              market_region,
              COUNT(DISTINCT invoice_no) AS valid_orders,
              SUM(net_revenue_gbp) AS revenue_gbp,
              SUM(pre_ad_contribution_gbp) AS pre_ad_contribution_gbp,
              SUM(pre_ad_contribution_gbp) / NULLIF(SUM(net_revenue_gbp), 0) AS pre_ad_contribution_margin
            FROM fact_order_profit
            WHERE is_valid_sale = 1 AND invoice_month = ?
            GROUP BY market_region
            ORDER BY revenue_gbp DESC
            """,
            (current_month,),
        )

        ads = q(
            conn,
            """
            SELECT
              campaign_name,
              market_region,
              default_channel,
              category,
              ad_spend_gbp,
              attributed_revenue_gbp,
              roas
            FROM fact_ad_spend_monthly
            WHERE invoice_month = ?
            ORDER BY ad_spend_gbp DESC
            LIMIT 10
            """,
            (current_month,),
        )

        low_roas = q(
            conn,
            """
            SELECT
              campaign_name,
              ad_spend_gbp,
              attributed_revenue_gbp,
              roas
            FROM fact_ad_spend_monthly
            WHERE invoice_month = ? AND ad_spend_gbp >= 50
            ORDER BY roas ASC
            LIMIT 5
            """,
            (current_month,),
        )

        inventory = q(
            conn,
            """
            SELECT
              category,
              COUNT(*) AS active_skus,
              SUM(inventory_value_gbp) AS inventory_value_gbp,
              AVG(turnover_days) AS avg_turnover_days,
              SUM(stockout_flag) AS stockout_skus,
              SUM(slow_moving_flag) AS slow_moving_skus
            FROM fact_inventory_monthly
            WHERE invoice_month = ?
            GROUP BY category
            ORDER BY inventory_value_gbp DESC
            """,
            (current_month,),
        )

        stock_actions = q(
            conn,
            """
            SELECT
              i.stock_code,
              i.category,
              i.sku_tier,
              i.units_sold,
              i.closing_stock_units,
              i.turnover_days,
              i.stockout_flag,
              i.slow_moving_flag,
              i.replenishment_recommendation
            FROM fact_inventory_monthly i
            WHERE i.invoice_month = ?
              AND (i.stockout_flag = 1 OR i.slow_moving_flag = 1)
            ORDER BY i.stockout_flag DESC, i.slow_moving_flag DESC, i.units_sold DESC
            LIMIT 12
            """,
            (current_month,),
        )

    display_monthly = monthly.copy()
    for col in ["revenue_gbp", "gross_profit_gbp", "ad_spend_gbp", "contribution_profit_gbp"]:
        display_monthly[col] = display_monthly[col].map(gbp)
    for col in ["gross_margin", "contribution_margin"]:
        display_monthly[col] = display_monthly[col].map(pct)

    display_category = category.copy()
    for col in ["revenue_gbp", "gross_profit_gbp", "pre_ad_contribution_gbp"]:
        display_category[col] = display_category[col].map(gbp)
    display_category["pre_ad_contribution_margin"] = display_category["pre_ad_contribution_margin"].map(pct)

    display_market = market.copy()
    for col in ["revenue_gbp", "pre_ad_contribution_gbp"]:
        display_market[col] = display_market[col].map(gbp)
    display_market["pre_ad_contribution_margin"] = display_market["pre_ad_contribution_margin"].map(pct)

    display_ads = ads.copy()
    for col in ["ad_spend_gbp", "attributed_revenue_gbp"]:
        display_ads[col] = display_ads[col].map(gbp)
    display_ads["roas"] = display_ads["roas"].map(lambda x: f"{x:.1f}x")

    display_low_roas = low_roas.copy()
    for col in ["ad_spend_gbp", "attributed_revenue_gbp"]:
        display_low_roas[col] = display_low_roas[col].map(gbp)
    display_low_roas["roas"] = display_low_roas["roas"].map(lambda x: f"{x:.1f}x")

    display_inventory = inventory.copy()
    display_inventory["inventory_value_gbp"] = display_inventory["inventory_value_gbp"].map(gbp)
    display_inventory["avg_turnover_days"] = display_inventory["avg_turnover_days"].map(lambda x: f"{x:.1f}")

    report = f"""# Cross-Border E-commerce Monthly Business Review

## Executive Summary

- **{current_month} revenue was {gbp(current['revenue_gbp'])}, {pct(revenue_change)} versus {previous_month}.** Contribution profit after simulated ad spend was {gbp(current['contribution_profit_gbp'])}, {pct(cp_change)} versus the prior month.
- **The business remains revenue-concentrated by market and category.** UK and Europe are the main demand base, while category mix determines whether sales growth converts into contribution profit.
- **Ad efficiency needs budget discipline.** Campaigns with low ROAS should be capped or reallocated to higher-margin category/market combinations before scaling.
- **Inventory action should be SKU-specific.** Stockout-risk SKUs need replenishment, while slow-moving SKUs should be cleared or purchase orders reduced.

## Current KPI Scorecard

The KPI contract mirrors the job description: sales, gross profit, fee impact, ad efficiency, contribution profit, and inventory risk. The current readout compares the latest complete month ({current_month}, {current_min_date} to {current_max_date}) with the immediately previous month ({previous_month}). The raw source also contains a partial later month, but it is excluded from the headline comparison to avoid misleading month-over-month conclusions.

{table_md(display_monthly)}

## Category profit determines whether growth is worth scaling

Revenue alone is not enough for operating decisions. The table below ranks categories by current-month revenue and adds pre-ad contribution margin, which shows how much margin remains before paid traffic.

{table_md(display_category)}

**Implication:** scale categories that combine high revenue with acceptable contribution margin; discount or reprioritize categories that add revenue but consume margin after platform, payment, and logistics fees.

## Market mix changes the fee and logistics burden

Cross-border markets carry different platform and logistics assumptions. This cut helps explain why two markets with similar sales can produce different profit outcomes.

{table_md(display_market)}

**Implication:** UK/local traffic can usually tolerate lower order value, while long-haul markets need stricter minimum order value, bundle strategy, or ad-spend control to protect contribution profit.

## Advertising budget should be reallocated from low-ROAS combinations

The simulated ad table is built from revenue by month, market, channel, and category. It is suitable for demonstrating budget review logic, not for claiming true platform attribution.

Top spend campaigns:

{table_md(display_ads)}

Lowest ROAS campaigns with material spend:

{table_md(display_low_roas)}

**Implication:** cap or test down the lowest-ROAS campaigns for one review cycle, then move budget to combinations with stronger contribution margin and enough stock availability.

## Inventory risk is split between stockout and slow-moving SKUs

Inventory should not be managed only by total stock value. The useful question is which SKUs are likely to block sales and which SKUs are tying up cash.

{table_md(display_inventory)}

Priority SKU actions:

{table_md(stock_actions)}

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
"""

    REPORT.write_text(report, encoding="utf-8")
    SUMMARY_JSON.write_text(
        json.dumps(
            {
                "current_month": current_month,
                "previous_month": previous_month,
                "current_min_date": current_min_date,
                "current_max_date": current_max_date,
                "revenue_gbp": float(current["revenue_gbp"]),
                "revenue_change": float(revenue_change),
                "contribution_profit_gbp": float(current["contribution_profit_gbp"]),
                "contribution_profit_change": float(cp_change),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {REPORT}")
    print(f"Wrote {SUMMARY_JSON}")


if __name__ == "__main__":
    main()
