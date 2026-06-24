"""Generate a compact Chinese Markdown business review from analytics outputs."""

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
        return f"{sign}GBP {value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{sign}GBP {value / 1_000:.1f}k"
    return f"{sign}GBP {value:.0f}"


def percent(value: float) -> str:
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


def _markdown_table(df: pd.DataFrame, max_rows: int = 8) -> str:
    if df.empty:
        return "_没有数据。_"
    display = df.head(max_rows).copy()
    for col in display.columns:
        if col.endswith("_gbp"):
            display[col] = display[col].map(money)
        elif "margin" in col:
            display[col] = display[col].map(percent)
        elif col == "roas":
            display[col] = display[col].map(lambda x: f"{float(x):.1f}x")
    display = display.rename(columns=COLUMN_LABELS)
    text = display.fillna("").astype(str).map(lambda x: x.replace("|", "\\|"))
    headers = list(text.columns)
    rows = text.values.tolist()
    widths = [max(len(str(h)), *(len(str(row[i])) for row in rows)) for i, h in enumerate(headers)]
    header = "| " + " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    sep = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    body = ["| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def _translate_recommendations(recommendations: list[str]) -> list[str]:
    translated = []
    for item in recommendations:
        item = item.replace(
            "Review pricing, cost, and traffic allocation for low-margin category:",
            "复盘低利润品类的定价、成本和流量分配：",
        )
        item = item.replace("Cap or test down low-ROAS campaign:", "降低或测试下调低 ROAS 广告组合：")
        item = item.replace(
            "Prioritize replenishment for stockout-risk SKUs before scaling ads.",
            "在扩大广告投放前，优先补货有缺货风险的 SKU。",
        )
        item = item.replace(
            "Reduce purchasing or create clearance bundles for slow-moving SKUs.",
            "对滞销 SKU 减少采购，或通过组合/促销清库存。",
        )
        item = item.replace(
            "No critical exception was detected in the selected period; continue monitoring next month.",
            "本期未发现明显异常，下月继续监控。",
        )
        translated.append(item)
    return translated


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
    recommendations = _translate_recommendations(recommendation_text(bundle, month))
    rec_md = "\n".join([f"{idx + 1}. {item}" for idx, item in enumerate(recommendations)])
    return f"""# 跨境电商月度经营复盘

## 经营摘要

- 分析月份：**{month}**
- 销售收入：**{money(kpis.get("revenue_gbp", 0))}**
- 毛利率：**{percent(kpis.get("gross_margin", 0))}**
- 贡献利润：**{money(kpis.get("contribution_profit_gbp", 0))}**
- 贡献利润率：**{percent(kpis.get("contribution_margin", 0))}**
- 缺货 SKU：**{kpis.get("stockout_skus", 0)}**
- 滞销 SKU：**{kpis.get("slow_moving_skus", 0)}**

## KPI 总览

{_markdown_table(scorecard)}

## 低利润品类

{_markdown_table(low_margin)}

## 低 ROAS 广告组合

{_markdown_table(low_roas)}

## 库存动作清单

{_markdown_table(stock)}

## 建议动作

{rec_md}

## 数据边界

订单交易数据来自 UCI Online Retail II 公开数据。成本、费用、广告和库存字段为作品集演示用的模拟经营扩展数据。
"""
