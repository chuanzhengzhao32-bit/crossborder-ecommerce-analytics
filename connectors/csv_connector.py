"""CSV connector contract for platform exports.

In a real company, this layer can be replaced with Shopify, Amazon, TikTok Shop,
ERP, WMS, or ad-platform APIs. The MVP keeps CSV import because interview
reviewers can run it without private credentials.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_platform_export(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)

