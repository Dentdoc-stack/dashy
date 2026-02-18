"""
utils.py — Shared helper functions for the FastAPI backend.
"""

import math
import pandas as pd
import numpy as np
from datetime import datetime


def safe_json(obj):
    """Convert pandas/numpy types to JSON-safe Python types."""
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat() if pd.notna(obj) else None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return None if math.isnan(v) else v
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if pd.isna(obj):
        return None
    return obj


def df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert a DataFrame to a list of JSON-safe dicts."""
    if df.empty:
        return []
    records = df.to_dict(orient="records")
    cleaned = []
    for row in records:
        cleaned.append({k: safe_json(v) for k, v in row.items()})
    return cleaned


def filter_df(
    df: pd.DataFrame,
    package_name: str | None = None,
    district: str | None = None,
    site_name: str | None = None,
    status: str | None = None,
) -> pd.DataFrame:
    """Apply optional filters to a DataFrame."""
    if df.empty:
        return df
    if package_name:
        df = df[df["package_name"] == package_name]
    if district and "district" in df.columns:
        df = df[df["district"] == district]
    if site_name and "site_name" in df.columns:
        df = df[df["site_name"] == site_name]
    if status and "site_status" in df.columns:
        df = df[df["site_status"] == status]
    return df
