"""SKU-region promotion opportunity scoring model."""

from __future__ import annotations

import numpy as np
import pandas as pd

from analytics_hub.io import DataBundle


def _score_percentile(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    if series.empty:
        return series
    rank = series.rank(pct=True, ascending=higher_is_better)
    return (rank * 100).round(1)


def sku_region_opportunity_score(
    bundle: DataBundle,
    min_orders: int = 10,
    min_active_periods: int = 3,
    region_col: str = "market_region",
) -> pd.DataFrame:
    """Score SKU-region combinations for promotion priority.

    The original business framing is SKU + province. This portfolio dataset is
    cross-border, so the default region is market_region. If country is desired,
    pass region_col="country".
    """

    data = bundle.profit.copy()
    if region_col not in data.columns:
        region_col = "country" if "country" in data.columns else "market_region"
    required = {"stock_code", region_col, "invoice_no", "quantity", "net_revenue_gbp", "is_valid_sale"}
    if not required.issubset(data.columns):
        return pd.DataFrame()

    data["invoice_date"] = pd.to_datetime(data.get("invoice_date"), errors="coerce")
    if data["invoice_date"].notna().any():
        data["period"] = data["invoice_date"].dt.to_period("W-MON").astype(str)
    else:
        data["period"] = data["invoice_month"].astype(str)

    total_units = data.loc[data["is_valid_sale"].eq(1), "quantity"].sum()
    total_gmv = data.loc[data["is_valid_sale"].eq(1), "net_revenue_gbp"].sum()

    grouped = (
        data.groupby(["stock_code", region_col], dropna=False)
        .agg(
            total_orders=("invoice_no", "nunique"),
            valid_order_lines=("is_valid_sale", "sum"),
            total_lines=("invoice_no", "count"),
            active_periods=("period", "nunique"),
            units_sold=("quantity", lambda x: x[data.loc[x.index, "is_valid_sale"].eq(1)].sum()),
            gmv_gbp=("net_revenue_gbp", lambda x: x[data.loc[x.index, "is_valid_sale"].eq(1)].sum()),
        )
        .reset_index()
        .rename(columns={region_col: "region"})
    )

    grouped = grouped.loc[
        (grouped["total_orders"] >= min_orders) & (grouped["active_periods"] >= min_active_periods)
    ].copy()
    if grouped.empty:
        return grouped

    weekly = (
        data.loc[data["is_valid_sale"].eq(1)]
        .groupby(["stock_code", region_col, "period"], dropna=False)
        .agg(units=("quantity", "sum"))
        .reset_index()
        .rename(columns={region_col: "region"})
    )

    slopes = []
    for (sku, region), part in weekly.groupby(["stock_code", "region"], dropna=False):
        part = part.sort_values("period")
        y = part["units"].to_numpy(dtype=float)
        if len(y) < 2:
            slope = 0.0
        else:
            x = np.arange(len(y), dtype=float)
            slope = float(np.polyfit(x, y, 1)[0])
        slopes.append({"stock_code": sku, "region": region, "sales_momentum": slope})

    grouped = grouped.merge(pd.DataFrame(slopes), on=["stock_code", "region"], how="left")
    grouped["sales_share"] = grouped["units_sold"] / total_units if total_units else 0
    grouped["gmv_share"] = grouped["gmv_gbp"] / total_gmv if total_gmv else 0
    grouped["valid_order_rate"] = grouped["valid_order_lines"] / grouped["total_lines"].replace(0, pd.NA)
    grouped["sales_share_score"] = _score_percentile(grouped["sales_share"])
    grouped["gmv_share_score"] = _score_percentile(grouped["gmv_share"])
    grouped["momentum_score"] = _score_percentile(grouped["sales_momentum"])
    grouped["valid_order_rate_score"] = _score_percentile(grouped["valid_order_rate"])
    grouped["opportunity_score"] = (
        grouped["sales_share_score"] * 0.30
        + grouped["gmv_share_score"] * 0.25
        + grouped["momentum_score"] * 0.20
        + grouped["valid_order_rate_score"] * 0.25
    ).round(1)
    grouped["investment_tier"] = pd.cut(
        grouped["opportunity_score"],
        bins=[-1, 40, 60, 75, 100],
        labels=["缩减测试", "观察优化", "稳定投入", "重点加码"],
    ).astype(str)

    return grouped.sort_values("opportunity_score", ascending=False)[
        [
            "stock_code",
            "region",
            "total_orders",
            "active_periods",
            "units_sold",
            "gmv_gbp",
            "sales_share",
            "gmv_share",
            "sales_momentum",
            "valid_order_rate",
            "opportunity_score",
            "investment_tier",
        ]
    ]
