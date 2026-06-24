"""Streamlit app for the Cross-Border E-commerce Analytics Hub."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics_hub.diagnostics import inventory_actions, low_margin_categories, low_roas_campaigns, recommendation_text
from analytics_hub.io import load_default_bundle, load_uploaded_bundle, validate_bundle
from analytics_hub.kpi_engine import available_reporting_months, category_profit, current_month_kpis, market_profit, monthly_scorecard
from analytics_hub.report_generator import generate_markdown_report


st.set_page_config(
    page_title="Cross-Border E-commerce Analytics Hub",
    page_icon="📊",
    layout="wide",
)


def money(value: float) -> str:
    value = float(value)
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}£{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{sign}£{value / 1_000:.1f}k"
    return f"{sign}£{value:.0f}"


def pct(value: float) -> str:
    return f"{float(value) * 100:.1f}%"


def format_display(df: pd.DataFrame) -> pd.DataFrame:
    display = df.copy()
    for col in display.columns:
        if col.endswith("_gbp"):
            display[col] = display[col].map(money)
        elif "margin" in col:
            display[col] = display[col].map(pct)
        elif col == "roas":
            display[col] = display[col].map(lambda x: f"{float(x):.1f}x")
    return display


st.title("Cross-Border E-commerce Analytics Hub")
st.caption("Prototype for automated operating reviews from platform exports, ERP cost data, ad spend, and inventory snapshots.")

with st.sidebar:
    st.header("Data Input")
    st.write("Use the built-in sample/full generated data, or upload CSV exports with the same schema.")
    use_uploads = st.toggle("Upload CSV files", value=False)
    if use_uploads:
        profit_file = st.file_uploader("Profit / order analysis table", type=["csv"])
        ads_file = st.file_uploader("Ad spend table", type=["csv"])
        inventory_file = st.file_uploader("Inventory table", type=["csv"])
        bundle = load_uploaded_bundle(profit_file, ads_file, inventory_file)
    else:
        bundle = load_default_bundle()
    st.info(f"Current source: {bundle.source_label}")
    st.subheader("Validation")
    for check in validate_bundle(bundle):
        st.write(f"- {check}")

scorecard = monthly_scorecard(bundle)
if scorecard.empty:
    st.error("No valid KPI data available.")
    st.stop()

months = available_reporting_months(bundle.profit)
if not months:
    months = list(scorecard["invoice_month"].astype(str))
selected_month = st.selectbox("Reporting month", options=months, index=len(months) - 1)
kpis = current_month_kpis(bundle, selected_month)

st.subheader("Executive KPI Snapshot")
cols = st.columns(6)
cols[0].metric("Revenue", money(kpis["revenue_gbp"]))
cols[1].metric("Gross Margin", pct(kpis["gross_margin"]))
cols[2].metric("Ad Spend", money(kpis["ad_spend_gbp"]))
cols[3].metric("Contribution Profit", money(kpis["contribution_profit_gbp"]))
cols[4].metric("Contribution Margin", pct(kpis["contribution_margin"]))
cols[5].metric("ROAS", f"{kpis['roas']:.1f}x")

cols = st.columns(3)
cols[0].metric("Valid Orders", f"{kpis['valid_orders']:,}")
cols[1].metric("Stockout SKUs", kpis["stockout_skus"])
cols[2].metric("Slow-Moving SKUs", kpis["slow_moving_skus"])

st.subheader("Monthly Trend")
trend_scorecard = scorecard.loc[scorecard["invoice_month"].astype(str).isin(months)]
trend = trend_scorecard.set_index("invoice_month")[["revenue_gbp", "gross_profit_gbp", "contribution_profit_gbp"]]
st.line_chart(trend)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Category Profit", "Market Profit", "Ad Efficiency", "Inventory Actions", "Auto Report"]
)

with tab1:
    st.write("Find high-sales but low-profit categories before scaling traffic.")
    category = category_profit(bundle, selected_month)
    st.dataframe(format_display(category), use_container_width=True)
    st.bar_chart(category.set_index("category")[["revenue_gbp", "pre_ad_contribution_gbp"]])
    st.write("Lowest contribution margin categories")
    st.dataframe(format_display(low_margin_categories(bundle, selected_month)), use_container_width=True)

with tab2:
    st.write("Compare markets by sales volume and contribution margin.")
    market = market_profit(bundle, selected_month)
    st.dataframe(format_display(market), use_container_width=True)
    if not market.empty:
        st.bar_chart(market.set_index("market_region")[["revenue_gbp", "pre_ad_contribution_gbp"]])

with tab3:
    st.write("Identify campaigns that need budget caps, creative tests, or margin checks.")
    low_roas = low_roas_campaigns(bundle, selected_month)
    st.dataframe(format_display(low_roas), use_container_width=True)

with tab4:
    st.write("Separate stockout risk from slow-moving inventory.")
    stock = inventory_actions(bundle, selected_month)
    st.dataframe(format_display(stock), use_container_width=True)

with tab5:
    report = generate_markdown_report(bundle, selected_month)
    st.download_button(
        "Download Markdown Business Review",
        data=report.encode("utf-8"),
        file_name=f"business_review_{selected_month}.md",
        mime="text/markdown",
    )
    st.markdown(report)

st.divider()
st.caption(
    "Portfolio boundary: public transaction data + synthetic cost/ad/inventory extensions. "
    "In a real deployment, CSV uploads can be replaced by Shopify, Amazon, TikTok Shop, ERP, WMS, and ad-platform APIs."
)
