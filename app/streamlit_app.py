"""中文 Streamlit app for the Cross-Border E-commerce Analytics Hub."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics_hub.diagnostics import inventory_actions, low_margin_categories, low_roas_campaigns
from analytics_hub.io import load_default_bundle, load_uploaded_bundle, validate_bundle
from analytics_hub.kpi_engine import available_reporting_months, category_profit, current_month_kpis, market_profit, monthly_scorecard
from analytics_hub.report_generator import generate_markdown_report


st.set_page_config(
    page_title="跨境电商经营分析工具",
    page_icon="📊",
    layout="wide",
)


def money(value: float) -> str:
    value = float(value)
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}GBP {value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{sign}GBP {value / 1_000:.1f}k"
    return f"{sign}GBP {value:.0f}"


def pct(value: float) -> str:
    return f"{float(value) * 100:.1f}%"


COLUMN_LABELS = {
    "invoice_month": "月份",
    "valid_orders": "有效订单",
    "revenue_gbp": "销售收入",
    "gross_profit_gbp": "毛利",
    "gross_margin": "毛利率",
    "pre_ad_contribution_gbp": "广告前贡献利润",
    "ad_spend_gbp": "广告花费",
    "contribution_profit_gbp": "贡献利润",
    "contribution_margin": "贡献利润率",
    "category": "品类",
    "market_region": "市场区域",
    "campaign_name": "广告组合",
    "default_channel": "渠道",
    "attributed_revenue_gbp": "归因收入",
    "roas": "ROAS",
    "stock_code": "SKU",
    "sku_tier": "SKU分层",
    "units_sold": "销量",
    "closing_stock_units": "期末库存",
    "turnover_days": "周转天数",
    "stockout_flag": "缺货标记",
    "slow_moving_flag": "滞销标记",
    "replenishment_recommendation": "建议动作",
    "inventory_value_gbp": "库存金额",
}


def format_display(df: pd.DataFrame) -> pd.DataFrame:
    display = df.copy()
    for col in display.columns:
        if col.endswith("_gbp"):
            display[col] = display[col].map(money)
        elif "margin" in col:
            display[col] = display[col].map(pct)
        elif col == "roas":
            display[col] = display[col].map(lambda x: f"{float(x):.1f}x")
    return display.rename(columns=COLUMN_LABELS)


st.title("跨境电商经营分析工具")
st.caption("自动生成销售、利润、广告和库存经营复盘的分析工具原型。")

with st.sidebar:
    st.header("数据来源")
    st.write("默认使用内置样例/本地完整数据；也可以上传同字段结构的 CSV。")
    use_uploads = st.toggle("上传 CSV 文件", value=False)
    if use_uploads:
        profit_file = st.file_uploader("订单/利润分析表", type=["csv"])
        ads_file = st.file_uploader("广告投放表", type=["csv"])
        inventory_file = st.file_uploader("库存表", type=["csv"])
        bundle = load_uploaded_bundle(profit_file, ads_file, inventory_file)
    else:
        bundle = load_default_bundle()

    source_label = {
        "generated full dataset": "本地完整数据",
        "committed sample dataset": "GitHub 样例数据",
        "uploaded files + default fallback": "上传文件 + 默认数据补齐",
    }.get(bundle.source_label, bundle.source_label)
    st.info(f"当前数据源：{source_label}")

    st.subheader("数据校验")
    for check in validate_bundle(bundle):
        check_cn = "关键表和字段齐全，可以分析。" if check == "All required tables and columns are available." else check
        st.write(f"- {check_cn}")

scorecard = monthly_scorecard(bundle)
if scorecard.empty:
    st.error("没有可用的 KPI 数据。")
    st.stop()

months = available_reporting_months(bundle.profit)
if not months:
    months = list(scorecard["invoice_month"].astype(str))
selected_month = st.selectbox("分析月份", options=months, index=len(months) - 1)
kpis = current_month_kpis(bundle, selected_month)

st.subheader("经营 KPI 总览")
cols = st.columns(6)
cols[0].metric("销售收入", money(kpis["revenue_gbp"]))
cols[1].metric("毛利率", pct(kpis["gross_margin"]))
cols[2].metric("广告花费", money(kpis["ad_spend_gbp"]))
cols[3].metric("贡献利润", money(kpis["contribution_profit_gbp"]))
cols[4].metric("贡献利润率", pct(kpis["contribution_margin"]))
cols[5].metric("ROAS", f"{kpis['roas']:.1f}x")

cols = st.columns(3)
cols[0].metric("有效订单", f"{kpis['valid_orders']:,}")
cols[1].metric("缺货 SKU", kpis["stockout_skus"])
cols[2].metric("滞销 SKU", kpis["slow_moving_skus"])

st.subheader("月度趋势")
trend_scorecard = scorecard.loc[scorecard["invoice_month"].astype(str).isin(months)]
trend = trend_scorecard.rename(
    columns={
        "invoice_month": "月份",
        "revenue_gbp": "销售收入",
        "gross_profit_gbp": "毛利",
        "contribution_profit_gbp": "贡献利润",
    }
).set_index("月份")[["销售收入", "毛利", "贡献利润"]]
st.line_chart(trend)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["品类利润", "市场利润", "广告效率", "库存动作", "自动报告"])

with tab1:
    st.write("用于识别“销售高但利润差”的品类，避免盲目扩大投放。")
    category = category_profit(bundle, selected_month)
    st.dataframe(format_display(category), use_container_width=True)
    chart_category = category.rename(
        columns={"category": "品类", "revenue_gbp": "销售收入", "pre_ad_contribution_gbp": "广告前贡献利润"}
    )
    st.bar_chart(chart_category.set_index("品类")[["销售收入", "广告前贡献利润"]])
    st.write("贡献利润率最低的品类")
    st.dataframe(format_display(low_margin_categories(bundle, selected_month)), use_container_width=True)

with tab2:
    st.write("比较不同市场的销售规模和贡献利润率。")
    market = market_profit(bundle, selected_month)
    st.dataframe(format_display(market), use_container_width=True)
    if not market.empty:
        chart_market = market.rename(
            columns={"market_region": "市场区域", "revenue_gbp": "销售收入", "pre_ad_contribution_gbp": "广告前贡献利润"}
        )
        st.bar_chart(chart_market.set_index("市场区域")[["销售收入", "广告前贡献利润"]])

with tab3:
    st.write("识别需要降预算、换素材或重新评估利润的低 ROAS 广告组合。")
    low_roas = low_roas_campaigns(bundle, selected_month)
    st.dataframe(format_display(low_roas), use_container_width=True)

with tab4:
    st.write("区分缺货风险 SKU 和滞销 SKU，分别做补货或清库存动作。")
    stock = inventory_actions(bundle, selected_month)
    st.dataframe(format_display(stock), use_container_width=True)

with tab5:
    report = generate_markdown_report(bundle, selected_month)
    st.download_button(
        "下载月度经营复盘",
        data=report.encode("utf-8"),
        file_name=f"经营复盘_{selected_month}.md",
        mime="text/markdown",
    )
    st.markdown(report)

st.divider()
st.caption(
    "数据边界：订单数据来自公开数据；成本、广告、库存是模拟经营扩展数据。真实落地时，可替换为 Shopify、Amazon、TikTok Shop、ERP、WMS 和广告平台 API。"
)
