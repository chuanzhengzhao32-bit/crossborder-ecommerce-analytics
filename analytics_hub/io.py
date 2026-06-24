"""Data loading helpers for the analytics hub.

The hub can work with either generated full-size processed tables or the
committed sample tables. Uploaded files from Streamlit use the same schema.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
SAMPLE_DIR = ROOT / "data" / "sample"


@dataclass(frozen=True)
class DataBundle:
    profit: pd.DataFrame
    ads: pd.DataFrame
    inventory: pd.DataFrame
    source_label: str


def _read_csv(path_or_buffer: str | Path | BinaryIO) -> pd.DataFrame:
    return pd.read_csv(path_or_buffer)


def _default_dir() -> tuple[Path, str]:
    required = [
        PROCESSED_DIR / "fact_order_profit.csv",
        PROCESSED_DIR / "fact_ad_spend_monthly.csv",
        PROCESSED_DIR / "fact_inventory_monthly.csv",
    ]
    if all(path.exists() for path in required):
        return PROCESSED_DIR, "generated full dataset"
    return SAMPLE_DIR, "committed sample dataset"


def load_default_bundle() -> DataBundle:
    data_dir, label = _default_dir()
    return DataBundle(
        profit=_read_csv(data_dir / "fact_order_profit.csv"),
        ads=_read_csv(data_dir / "fact_ad_spend_monthly.csv"),
        inventory=_read_csv(data_dir / "fact_inventory_monthly.csv"),
        source_label=label,
    )


def load_uploaded_bundle(
    profit_file: BinaryIO | None,
    ads_file: BinaryIO | None,
    inventory_file: BinaryIO | None,
) -> DataBundle:
    default = load_default_bundle()
    return DataBundle(
        profit=_read_csv(profit_file) if profit_file else default.profit,
        ads=_read_csv(ads_file) if ads_file else default.ads,
        inventory=_read_csv(inventory_file) if inventory_file else default.inventory,
        source_label="uploaded files + default fallback",
    )


def validate_bundle(bundle: DataBundle) -> list[str]:
    checks = []
    required_profit = {
        "invoice_month",
        "invoice_no",
        "stock_code",
        "category",
        "market_region",
        "net_revenue_gbp",
        "gross_profit_gbp",
        "pre_ad_contribution_gbp",
        "is_valid_sale",
    }
    required_ads = {
        "invoice_month",
        "campaign_name",
        "ad_spend_gbp",
        "attributed_revenue_gbp",
        "roas",
    }
    required_inventory = {
        "invoice_month",
        "stock_code",
        "category",
        "inventory_value_gbp",
        "turnover_days",
        "stockout_flag",
        "slow_moving_flag",
    }
    tables = [
        ("profit table", bundle.profit, required_profit),
        ("ad table", bundle.ads, required_ads),
        ("inventory table", bundle.inventory, required_inventory),
    ]
    for label, df, required in tables:
        missing = sorted(required - set(df.columns))
        if missing:
            checks.append(f"{label}: missing columns {missing}")
        if df.empty:
            checks.append(f"{label}: no rows")
    if not checks:
        checks.append("All required tables and columns are available.")
    return checks
