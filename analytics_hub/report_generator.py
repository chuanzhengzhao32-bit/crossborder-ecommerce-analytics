"""Generate a compact Markdown business review from analytics outputs."""

from __future__ import annotations

import pandas as pd

from analytics_hub.diagnostics import inventory_actions, low_margin_categories, low_roas_campaigns, recommendation_text
from analytics_hub.io import DataBundle
from analytics_hub.kpi_engine import available_reporting_months, current_month_kpis, monthly_scorecard


def money(value: float) -> str:
    value = float(value)
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}£{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{sign}£{value / 1_000:.1f}k"
    return f"{sign}£{value:.0f}"


def percent(value: float) -> str:
    return f"{float(value) * 100:.1f}%"


def _markdown_table(df: pd.DataFrame, max_rows: int = 8) -> str:
    if df.empty:
        return "_No rows._"
    display = df.head(max_rows).copy()
    for col in display.columns:
        if col.endswith("_gbp"):
            display[col] = display[col].map(money)
        elif "margin" in col:
            display[col] = display[col].map(percent)
        elif col == "roas":
            display[col] = display[col].map(lambda x: f"{float(x):.1f}x")
    text = display.fillna("").astype(str).map(lambda x: x.replace("|", "\\|"))
    headers = list(text.columns)
    rows = text.values.tolist()
    widths = [max(len(str(h)), *(len(str(row[i])) for row in rows)) for i, h in enumerate(headers)]
    header = "| " + " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    sep = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    body = ["| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def generate_markdown_report(bundle: DataBundle, month: str) -> str:
    kpis = current_month_kpis(bundle, month)
    reporting_months = available_reporting_months(bundle.profit)
    scorecard = monthly_scorecard(bundle)
    if reporting_months:
        scorecard = scorecard.loc[scorecard["invoice_month"].astype(str).isin(reporting_months)]
    scorecard = scorecard.tail(3)
    low_margin = low_margin_categories(bundle, month)
    low_roas = low_roas_campaigns(bundle, month)
    stock = inventory_actions(bundle, month)
    recommendations = recommendation_text(bundle, month)
    rec_md = "\n".join([f"{idx + 1}. {item}" for idx, item in enumerate(recommendations)])
    return f"""# Cross-Border E-commerce Operating Review

## Executive Summary

- Reporting month: **{month}**
- Revenue: **{money(kpis.get("revenue_gbp", 0))}**
- Gross margin: **{percent(kpis.get("gross_margin", 0))}**
- Contribution profit: **{money(kpis.get("contribution_profit_gbp", 0))}**
- Contribution margin: **{percent(kpis.get("contribution_margin", 0))}**
- Stockout SKUs: **{kpis.get("stockout_skus", 0)}**
- Slow-moving SKUs: **{kpis.get("slow_moving_skus", 0)}**

## KPI Scorecard

{_markdown_table(scorecard)}

## Low-Margin Categories

{_markdown_table(low_margin)}

## Low-ROAS Campaigns

{_markdown_table(low_roas)}

## Inventory Action List

{_markdown_table(stock)}

## Recommended Actions

{rec_md}

## Data Boundary

Transaction lines come from public UCI Online Retail II data. Cost, fee, ad, and inventory fields are synthetic operating extensions for portfolio demonstration.
"""
