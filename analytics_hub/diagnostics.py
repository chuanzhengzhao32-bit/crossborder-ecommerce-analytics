"""Automated diagnostic tables for operating reviews."""

from __future__ import annotations

import pandas as pd

from analytics_hub.io import DataBundle
from analytics_hub.kpi_engine import category_profit


def low_margin_categories(bundle: DataBundle, month: str, limit: int = 5) -> pd.DataFrame:
    data = category_profit(bundle, month)
    data = data.loc[data["revenue_gbp"] > 0].copy()
    return data.sort_values("pre_ad_contribution_margin").head(limit)


def low_roas_campaigns(bundle: DataBundle, month: str, limit: int = 8) -> pd.DataFrame:
    ads = bundle.ads.loc[bundle.ads["invoice_month"].astype(str).eq(month)].copy()
    if ads.empty:
        return ads
    spend_threshold = max(50, ads["ad_spend_gbp"].quantile(0.25))
    return (
        ads.loc[ads["ad_spend_gbp"] >= spend_threshold]
        .sort_values("roas")
        .head(limit)
    )


def inventory_actions(bundle: DataBundle, month: str, limit: int = 12) -> pd.DataFrame:
    inventory = bundle.inventory.loc[bundle.inventory["invoice_month"].astype(str).eq(month)].copy()
    if inventory.empty:
        return inventory
    flagged = inventory.loc[
        inventory["stockout_flag"].eq(1) | inventory["slow_moving_flag"].eq(1)
    ].copy()
    if flagged.empty:
        return flagged
    sort_cols = [col for col in ["stockout_flag", "slow_moving_flag", "units_sold"] if col in flagged.columns]
    return flagged.sort_values(sort_cols, ascending=False).head(limit)


def recommendation_text(bundle: DataBundle, month: str) -> list[str]:
    low_margin = low_margin_categories(bundle, month, limit=3)
    low_roas = low_roas_campaigns(bundle, month, limit=3)
    stock = inventory_actions(bundle, month, limit=3)
    recommendations = []
    if not low_margin.empty:
        category = str(low_margin.iloc[0]["category"])
        recommendations.append(f"Review pricing, cost, and traffic allocation for low-margin category: {category}.")
    if not low_roas.empty:
        campaign = str(low_roas.iloc[0]["campaign_name"])
        recommendations.append(f"Cap or test down low-ROAS campaign: {campaign}.")
    if not stock.empty:
        stockout = stock.loc[stock["stockout_flag"].eq(1)]
        if not stockout.empty:
            recommendations.append("Prioritize replenishment for stockout-risk SKUs before scaling ads.")
        slow = stock.loc[stock["slow_moving_flag"].eq(1)]
        if not slow.empty:
            recommendations.append("Reduce purchasing or create clearance bundles for slow-moving SKUs.")
    if not recommendations:
        recommendations.append("No critical exception was detected in the selected period; continue monitoring next month.")
    return recommendations
