"""KPI calculation engine for cross-border e-commerce operating reviews."""

from __future__ import annotations

import pandas as pd

from analytics_hub.io import DataBundle


def available_reporting_months(profit: pd.DataFrame, min_active_dates: int = 25) -> list[str]:
    valid = profit.loc[profit["is_valid_sale"].eq(1)].copy()
    if valid.empty:
        return []
    if "invoice_date" not in valid.columns:
        return list(valid["invoice_month"].astype(str).dropna().sort_values().unique())
    month_profile = (
        valid.groupby("invoice_month", dropna=False)
        .agg(active_dates=("invoice_date", "nunique"))
        .reset_index()
    )
    complete = month_profile.loc[month_profile["active_dates"] >= min_active_dates, "invoice_month"]
    if complete.empty:
        complete = month_profile["invoice_month"]
    return list(complete.astype(str).sort_values().unique())


def latest_complete_month(profit: pd.DataFrame) -> str:
    months = available_reporting_months(profit)
    if not months:
        return ""
    return months[-1]


def monthly_scorecard(bundle: DataBundle) -> pd.DataFrame:
    valid = bundle.profit.loc[bundle.profit["is_valid_sale"].eq(1)].copy()
    profit_monthly = (
        valid.groupby("invoice_month", dropna=False)
        .agg(
            valid_orders=("invoice_no", "nunique"),
            revenue_gbp=("net_revenue_gbp", "sum"),
            gross_profit_gbp=("gross_profit_gbp", "sum"),
            pre_ad_contribution_gbp=("pre_ad_contribution_gbp", "sum"),
        )
        .reset_index()
    )
    ads_monthly = (
        bundle.ads.groupby("invoice_month", dropna=False)
        .agg(ad_spend_gbp=("ad_spend_gbp", "sum"))
        .reset_index()
    )
    scorecard = profit_monthly.merge(ads_monthly, on="invoice_month", how="left")
    scorecard["ad_spend_gbp"] = scorecard["ad_spend_gbp"].fillna(0)
    scorecard["gross_margin"] = scorecard["gross_profit_gbp"] / scorecard["revenue_gbp"].replace(0, pd.NA)
    scorecard["contribution_profit_gbp"] = (
        scorecard["pre_ad_contribution_gbp"] - scorecard["ad_spend_gbp"]
    )
    scorecard["contribution_margin"] = (
        scorecard["contribution_profit_gbp"] / scorecard["revenue_gbp"].replace(0, pd.NA)
    )
    return scorecard.sort_values("invoice_month")


def current_month_kpis(bundle: DataBundle, month: str | None = None) -> dict[str, float | int | str]:
    scorecard = monthly_scorecard(bundle)
    if scorecard.empty:
        return {}
    selected_month = month or str(scorecard.iloc[-1]["invoice_month"])
    current = scorecard.loc[scorecard["invoice_month"].eq(selected_month)].iloc[0]
    inventory = bundle.inventory.loc[bundle.inventory["invoice_month"].astype(str).eq(selected_month)]
    ads = bundle.ads.loc[bundle.ads["invoice_month"].astype(str).eq(selected_month)]
    ad_spend = float(current["ad_spend_gbp"])
    attributed_revenue = float(ads["attributed_revenue_gbp"].sum()) if not ads.empty else 0.0
    return {
        "invoice_month": selected_month,
        "valid_orders": int(current["valid_orders"]),
        "revenue_gbp": float(current["revenue_gbp"]),
        "gross_margin": float(current["gross_margin"]),
        "ad_spend_gbp": ad_spend,
        "contribution_profit_gbp": float(current["contribution_profit_gbp"]),
        "contribution_margin": float(current["contribution_margin"]),
        "roas": attributed_revenue / ad_spend if ad_spend else 0.0,
        "inventory_value_gbp": float(inventory["inventory_value_gbp"].sum()) if not inventory.empty else 0.0,
        "stockout_skus": int(inventory["stockout_flag"].sum()) if not inventory.empty else 0,
        "slow_moving_skus": int(inventory["slow_moving_flag"].sum()) if not inventory.empty else 0,
    }


def category_profit(bundle: DataBundle, month: str) -> pd.DataFrame:
    valid = bundle.profit.loc[
        bundle.profit["is_valid_sale"].eq(1) & bundle.profit["invoice_month"].astype(str).eq(month)
    ]
    result = (
        valid.groupby("category", dropna=False)
        .agg(
            revenue_gbp=("net_revenue_gbp", "sum"),
            gross_profit_gbp=("gross_profit_gbp", "sum"),
            pre_ad_contribution_gbp=("pre_ad_contribution_gbp", "sum"),
        )
        .reset_index()
    )
    result["pre_ad_contribution_margin"] = (
        result["pre_ad_contribution_gbp"] / result["revenue_gbp"].replace(0, pd.NA)
    )
    return result.sort_values("revenue_gbp", ascending=False)


def market_profit(bundle: DataBundle, month: str) -> pd.DataFrame:
    valid = bundle.profit.loc[
        bundle.profit["is_valid_sale"].eq(1) & bundle.profit["invoice_month"].astype(str).eq(month)
    ]
    result = (
        valid.groupby("market_region", dropna=False)
        .agg(
            valid_orders=("invoice_no", "nunique"),
            revenue_gbp=("net_revenue_gbp", "sum"),
            pre_ad_contribution_gbp=("pre_ad_contribution_gbp", "sum"),
        )
        .reset_index()
    )
    result["pre_ad_contribution_margin"] = (
        result["pre_ad_contribution_gbp"] / result["revenue_gbp"].replace(0, pd.NA)
    )
    return result.sort_values("revenue_gbp", ascending=False)
