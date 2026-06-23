"""Generate reproducible business extension tables for the UCI order data.

The UCI Online Retail II dataset provides real transaction lines but does not
include product cost, platform fees, ad spend, or inventory snapshots. This
script adds deterministic synthetic operating data so the project can
demonstrate the analysis required by a cross-border e-commerce analyst role.

Important: generated costs, fees, ads, and inventory are simulated. They are
for analytics-method demonstration only.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
ORDERS = PROCESSED / "fact_order_lines.csv"
PROFILE_DOC = ROOT / "docs" / "extension_profile.json"

SEED = 20260623
GBP_TO_CNY = 9.15
TOP_SKU_COUNT = 600


def assign_category(description: str, stock_code: str) -> str:
    text = f"{description} {stock_code}".upper()
    rules = [
        ("Home Decor", ["HEART", "CANDLE", "LANTERN", "HOLDER", "FRAME", "WREATH"]),
        ("Kitchen & Dining", ["CUP", "MUG", "PLATE", "BOWL", "TEA", "CAKE", "NAPKIN"]),
        ("Gift & Stationery", ["CARD", "PAPER", "TAG", "WRAP", "NOTEBOOK", "PENCIL"]),
        ("Fashion Accessories", ["BAG", "SCARF", "NECKLACE", "BRACELET", "PURSE"]),
        ("Kids & Toys", ["TOY", "DOLL", "GAME", "CHILD", "BABY", "SPACEBOY"]),
        ("Seasonal", ["CHRISTMAS", "EASTER", "HALLOWEEN", "VALENTINE", "PARTY"]),
    ]
    for category, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return category
    return "General Merchandise"


def assign_market(country: str) -> tuple[str, str, str]:
    europe = {
        "EIRE",
        "Germany",
        "France",
        "Netherlands",
        "Spain",
        "Switzerland",
        "Belgium",
        "Portugal",
        "Italy",
        "Norway",
        "Sweden",
        "Cyprus",
        "Austria",
        "Denmark",
        "Finland",
        "Greece",
        "Iceland",
        "Malta",
        "Poland",
        "Lithuania",
        "Czech Republic",
    }
    if country == "United Kingdom":
        return "UK", "UK Local", "own_site"
    if country in europe:
        return "Europe", "EU Cross-border", "amazon"
    if country in {"USA", "Canada"}:
        return "North America", "Long-haul", "amazon"
    if country in {"Australia", "Singapore", "Japan", "Hong Kong", "Bahrain", "United Arab Emirates"}:
        return "APAC", "Long-haul", "shopify"
    return "Other", "Rest of World", "shopify"


def load_orders() -> pd.DataFrame:
    if not ORDERS.exists():
        raise FileNotFoundError("Run scripts/prepare_orders.py before generating extensions.")

    orders = pd.read_csv(
        ORDERS,
        dtype={
            "invoice_no": "string",
            "stock_code": "string",
            "description": "string",
            "customer_id": "string",
            "country": "string",
            "source_sheet": "string",
        },
        parse_dates=["invoice_date"],
    )
    orders["invoice_month"] = orders["invoice_date"].dt.to_period("M").astype(str)
    return orders


def build_product_dimension(valid_orders: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    sku_stats = (
        valid_orders.groupby("stock_code", dropna=False)
        .agg(
            description=("description", lambda x: x.dropna().mode().iloc[0] if not x.dropna().empty else ""),
            total_quantity=("quantity", "sum"),
            total_revenue_gbp=("line_revenue_gbp", "sum"),
            avg_unit_price_gbp=("unit_price_gbp", "mean"),
            active_months=("invoice_month", "nunique"),
        )
        .reset_index()
    )
    sku_stats["category"] = [
        assign_category(desc, code) for desc, code in zip(sku_stats["description"], sku_stats["stock_code"])
    ]
    category_cost_ratio = {
        "Home Decor": 0.43,
        "Kitchen & Dining": 0.39,
        "Gift & Stationery": 0.32,
        "Fashion Accessories": 0.36,
        "Kids & Toys": 0.41,
        "Seasonal": 0.35,
        "General Merchandise": 0.38,
    }
    noise = rng.normal(1.0, 0.07, len(sku_stats)).clip(0.78, 1.22)
    sku_stats["unit_cost_gbp"] = [
        max(0.03, price * category_cost_ratio[cat] * factor)
        for price, cat, factor in zip(
            sku_stats["avg_unit_price_gbp"].fillna(0),
            sku_stats["category"],
            noise,
        )
    ]
    sku_stats["unit_cost_gbp"] = sku_stats["unit_cost_gbp"].round(4)
    revenue_rank = sku_stats["total_revenue_gbp"].rank(pct=True)
    sku_stats["sku_tier"] = np.select(
        [revenue_rank >= 0.9, revenue_rank >= 0.6, revenue_rank >= 0.25],
        ["A", "B", "C"],
        default="D",
    )
    sku_stats["lifecycle_stage"] = np.select(
        [sku_stats["active_months"] <= 3, sku_stats["sku_tier"].eq("A"), sku_stats["total_quantity"] <= 10],
        ["New/Test", "Core", "Long Tail"],
        default="Regular",
    )
    return sku_stats[
        [
            "stock_code",
            "description",
            "category",
            "sku_tier",
            "lifecycle_stage",
            "avg_unit_price_gbp",
            "unit_cost_gbp",
            "active_months",
            "total_quantity",
            "total_revenue_gbp",
        ]
    ]


def build_market_dimension(orders: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for country in sorted(orders["country"].dropna().unique()):
        region, shipping_zone, default_channel = assign_market(country)
        platform_fee_rate = {"own_site": 0.025, "amazon": 0.115, "shopify": 0.045}[default_channel]
        payment_fee_rate = {"own_site": 0.018, "amazon": 0.012, "shopify": 0.024}[default_channel]
        logistics_base_gbp = {
            "UK Local": 0.18,
            "EU Cross-border": 0.42,
            "Long-haul": 0.78,
            "Rest of World": 0.65,
        }[shipping_zone]
        rows.append(
            {
                "country": country,
                "market_region": region,
                "shipping_zone": shipping_zone,
                "default_channel": default_channel,
                "platform_fee_rate": platform_fee_rate,
                "payment_fee_rate": payment_fee_rate,
                "logistics_base_gbp_per_unit": logistics_base_gbp,
            }
        )
    return pd.DataFrame(rows)


def build_profit_fact(orders: pd.DataFrame, products: pd.DataFrame, markets: pd.DataFrame) -> pd.DataFrame:
    fact = orders.merge(
        products[["stock_code", "category", "sku_tier", "unit_cost_gbp"]],
        on="stock_code",
        how="left",
    ).merge(markets, on="country", how="left")
    fact["quantity_abs"] = fact["quantity"].abs()
    fact["net_revenue_gbp"] = np.where(fact["is_valid_sale"].eq(1), fact["line_revenue_gbp"], 0.0)
    fact["refund_amount_gbp"] = np.where(fact["is_return_line"].eq(1), fact["line_revenue_gbp"].abs(), 0.0)
    fact["product_cost_gbp"] = np.where(
        fact["is_valid_sale"].eq(1),
        fact["quantity_abs"] * fact["unit_cost_gbp"].fillna(fact["unit_price_gbp"] * 0.38),
        0.0,
    )
    fact["platform_fee_gbp"] = fact["net_revenue_gbp"] * fact["platform_fee_rate"].fillna(0.06)
    fact["payment_fee_gbp"] = fact["net_revenue_gbp"] * fact["payment_fee_rate"].fillna(0.02)
    fact["logistics_fee_gbp"] = np.where(
        fact["is_valid_sale"].eq(1),
        fact["quantity_abs"] * fact["logistics_base_gbp_per_unit"].fillna(0.5),
        0.0,
    )
    fact["gross_profit_gbp"] = fact["net_revenue_gbp"] - fact["product_cost_gbp"]
    fact["pre_ad_contribution_gbp"] = (
        fact["gross_profit_gbp"]
        - fact["platform_fee_gbp"]
        - fact["payment_fee_gbp"]
        - fact["logistics_fee_gbp"]
    )
    money_cols = [
        "net_revenue_gbp",
        "refund_amount_gbp",
        "product_cost_gbp",
        "platform_fee_gbp",
        "payment_fee_gbp",
        "logistics_fee_gbp",
        "gross_profit_gbp",
        "pre_ad_contribution_gbp",
    ]
    fact[money_cols] = fact[money_cols].round(4)
    return fact[
        [
            "transaction_line_id",
            "invoice_no",
            "invoice_date",
            "invoice_month",
            "stock_code",
            "country",
            "market_region",
            "default_channel",
            "category",
            "sku_tier",
            "quantity",
            "unit_price_gbp",
            "net_revenue_gbp",
            "refund_amount_gbp",
            "product_cost_gbp",
            "platform_fee_gbp",
            "payment_fee_gbp",
            "logistics_fee_gbp",
            "gross_profit_gbp",
            "pre_ad_contribution_gbp",
            "is_valid_sale",
            "is_return_line",
        ]
    ]


def build_ad_spend(valid_profit: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    top_skus = (
        valid_profit.groupby("stock_code")["net_revenue_gbp"]
        .sum()
        .sort_values(ascending=False)
        .head(TOP_SKU_COUNT)
        .index
    )
    ad_base = valid_profit[valid_profit["stock_code"].isin(top_skus)].copy()
    grouped = (
        ad_base.groupby(["invoice_month", "market_region", "default_channel", "category"], dropna=False)
        .agg(
            attributed_revenue_gbp=("net_revenue_gbp", "sum"),
            attributed_order_lines=("transaction_line_id", "count"),
        )
        .reset_index()
    )
    grouped = grouped[grouped["attributed_revenue_gbp"] > 0].copy()
    channel_rate = {"own_site": 0.035, "amazon": 0.075, "shopify": 0.06}
    market_multiplier = {"UK": 0.85, "Europe": 1.0, "North America": 1.18, "APAC": 1.12, "Other": 1.05}
    noise = rng.normal(1.0, 0.18, len(grouped)).clip(0.55, 1.75)
    grouped["ad_spend_gbp"] = [
        revenue * channel_rate.get(channel, 0.06) * market_multiplier.get(region, 1.0) * factor
        for revenue, channel, region, factor in zip(
            grouped["attributed_revenue_gbp"],
            grouped["default_channel"],
            grouped["market_region"],
            noise,
        )
    ]
    grouped["campaign_name"] = (
        grouped["market_region"].astype(str)
        + " | "
        + grouped["category"].astype(str)
        + " | "
        + grouped["default_channel"].astype(str)
    )
    grouped["roas"] = grouped["attributed_revenue_gbp"] / grouped["ad_spend_gbp"].replace(0, np.nan)
    grouped["ad_spend_gbp"] = grouped["ad_spend_gbp"].round(4)
    grouped["attributed_revenue_gbp"] = grouped["attributed_revenue_gbp"].round(4)
    grouped["roas"] = grouped["roas"].round(4)
    return grouped[
        [
            "invoice_month",
            "market_region",
            "default_channel",
            "category",
            "campaign_name",
            "ad_spend_gbp",
            "attributed_revenue_gbp",
            "attributed_order_lines",
            "roas",
        ]
    ]


def build_inventory(valid_profit: pd.DataFrame, products: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    sku_month = (
        valid_profit.groupby(["invoice_month", "stock_code"], dropna=False)
        .agg(
            units_sold=("quantity", "sum"),
            cogs_gbp=("product_cost_gbp", "sum"),
            revenue_gbp=("net_revenue_gbp", "sum"),
        )
        .reset_index()
    )
    top_skus = (
        valid_profit.groupby("stock_code")["net_revenue_gbp"]
        .sum()
        .sort_values(ascending=False)
        .head(1000)
        .index
    )
    sku_month = sku_month[sku_month["stock_code"].isin(top_skus)].copy()
    sku_month = sku_month.merge(
        products[["stock_code", "category", "sku_tier", "unit_cost_gbp"]],
        on="stock_code",
        how="left",
    )
    safety_days = {"A": 45, "B": 35, "C": 28, "D": 21}
    sku_month["daily_sales_units"] = sku_month["units_sold"] / 30.0
    sku_month["target_stock_units"] = [
        daily * safety_days.get(tier, 25) for daily, tier in zip(sku_month["daily_sales_units"], sku_month["sku_tier"])
    ]
    variation = rng.normal(1.0, 0.28, len(sku_month)).clip(0.15, 2.2)
    sku_month["opening_stock_units"] = np.ceil(sku_month["target_stock_units"] * variation + rng.integers(0, 12, len(sku_month)))
    sku_month["purchase_units"] = np.maximum(
        0,
        np.ceil(sku_month["units_sold"] * rng.normal(1.08, 0.32, len(sku_month))),
    )
    sku_month["closing_stock_units"] = np.maximum(
        0,
        sku_month["opening_stock_units"] + sku_month["purchase_units"] - sku_month["units_sold"],
    )
    sku_month["avg_stock_units"] = (sku_month["opening_stock_units"] + sku_month["closing_stock_units"]) / 2
    sku_month["inventory_value_gbp"] = sku_month["closing_stock_units"] * sku_month["unit_cost_gbp"]
    sku_month["turnover_days"] = np.where(
        sku_month["cogs_gbp"] > 0,
        (sku_month["avg_stock_units"] * sku_month["unit_cost_gbp"] / sku_month["cogs_gbp"]) * 30,
        np.nan,
    )
    sku_month["stockout_flag"] = (
        (sku_month["closing_stock_units"] <= sku_month["daily_sales_units"] * 3)
        & (sku_month["units_sold"] > 0)
    ).astype(int)
    sku_month["slow_moving_flag"] = (
        (sku_month["turnover_days"] > 90)
        & (sku_month["closing_stock_units"] > 20)
    ).astype(int)
    sku_month["replenishment_recommendation"] = np.select(
        [
            sku_month["stockout_flag"].eq(1),
            sku_month["slow_moving_flag"].eq(1),
            sku_month["sku_tier"].isin(["A", "B"]) & (sku_month["turnover_days"] < 25),
        ],
        ["Replenish urgently", "Reduce purchase / clear stock", "Increase safety stock"],
        default="Maintain",
    )
    numeric_cols = [
        "opening_stock_units",
        "purchase_units",
        "closing_stock_units",
        "avg_stock_units",
        "inventory_value_gbp",
        "turnover_days",
    ]
    sku_month[numeric_cols] = sku_month[numeric_cols].round(2)
    return sku_month[
        [
            "invoice_month",
            "stock_code",
            "category",
            "sku_tier",
            "units_sold",
            "cogs_gbp",
            "revenue_gbp",
            "opening_stock_units",
            "purchase_units",
            "closing_stock_units",
            "avg_stock_units",
            "inventory_value_gbp",
            "turnover_days",
            "stockout_flag",
            "slow_moving_flag",
            "replenishment_recommendation",
        ]
    ]


def main() -> None:
    rng = np.random.default_rng(SEED)
    orders = load_orders()
    valid_orders = orders[orders["is_valid_sale"].eq(1)].copy()

    products = build_product_dimension(valid_orders, rng)
    markets = build_market_dimension(orders)
    profit = build_profit_fact(orders, products, markets)
    valid_profit = profit[profit["is_valid_sale"].eq(1)].copy()
    ad_spend = build_ad_spend(valid_profit, rng)
    inventory = build_inventory(valid_profit, products, rng)

    products.to_csv(PROCESSED / "dim_product.csv", index=False, encoding="utf-8-sig")
    markets.to_csv(PROCESSED / "dim_market.csv", index=False, encoding="utf-8-sig")
    profit.to_csv(PROCESSED / "fact_order_profit.csv", index=False, encoding="utf-8-sig")
    ad_spend.to_csv(PROCESSED / "fact_ad_spend_monthly.csv", index=False, encoding="utf-8-sig")
    inventory.to_csv(PROCESSED / "fact_inventory_monthly.csv", index=False, encoding="utf-8-sig")

    profile = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "random_seed": SEED,
        "gbp_to_cny": GBP_TO_CNY,
        "tables": {
            "dim_product": int(len(products)),
            "dim_market": int(len(markets)),
            "fact_order_profit": int(len(profit)),
            "fact_ad_spend_monthly": int(len(ad_spend)),
            "fact_inventory_monthly": int(len(inventory)),
        },
        "disclosure": "Product cost, fees, ad spend, and inventory snapshots are deterministic synthetic extensions built on the public UCI transaction dataset.",
    }
    PROFILE_DOC.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(profile, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
