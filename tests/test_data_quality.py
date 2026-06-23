"""Lightweight pytest checks for the generated analytics dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def test_profit_sample_identity() -> None:
    data = pd.read_csv(PROCESSED / "fact_order_profit.csv", nrows=50_000)
    diff = (data["gross_profit_gbp"] - (data["net_revenue_gbp"] - data["product_cost_gbp"])).abs().max()
    assert diff < 0.02


def test_ad_spend_positive() -> None:
    data = pd.read_csv(PROCESSED / "fact_ad_spend_monthly.csv")
    assert (data["ad_spend_gbp"] > 0).all()
    assert (data["roas"] > 0).all()


def test_inventory_flags_exist() -> None:
    data = pd.read_csv(PROCESSED / "fact_inventory_monthly.csv")
    assert data["stockout_flag"].sum() > 0
    assert data["slow_moving_flag"].sum() > 0
