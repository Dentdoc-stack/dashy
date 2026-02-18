"""
risk_router.py — Risk & Recovery endpoints.
Risk score distribution, recovery recommendations, trends.
"""

import numpy as np
import pandas as pd
from fastapi import APIRouter, Query
from backend.data_store import store
from backend.utils import df_to_records, filter_df

router = APIRouter()


@router.get("/scores")
def risk_scores(
    package_name: str | None = Query(None),
    district: str | None = Query(None),
):
    """All sites with risk score breakdown."""
    df = filter_df(store.df_site, package_name=package_name, district=district)
    if df.empty:
        return []
    cols = [
        "package_name", "district", "site_name",
        "site_progress", "site_delay_days", "delay_bucket",
        "risk_score", "delay_score", "progress_score",
        "site_status",
    ]
    available = [c for c in cols if c in df.columns]
    return df_to_records(df[available].sort_values("risk_score", ascending=False))


@router.get("/distribution")
def risk_distribution(package_name: str | None = Query(None)):
    """Risk score histogram/bracket counts."""
    df = store.df_site
    if package_name:
        df = df[df["package_name"] == package_name]
    if df.empty:
        return []

    brackets = [
        (0, 20, "Low (0-20)"),
        (20, 40, "Medium-Low (20-40)"),
        (40, 60, "Medium (40-60)"),
        (60, 80, "Medium-High (60-80)"),
        (80, 200, "High (80+)"),
    ]
    result = []
    for lo, hi, label in brackets:
        count = int(((df["risk_score"] >= lo) & (df["risk_score"] < hi)).sum())
        result.append({"bracket": label, "min": lo, "max": hi, "count": count})
    return result


@router.get("/recovery-candidates")
def recovery_candidates(
    package_name: str | None = Query(None),
    limit: int = Query(20),
):
    """High-risk sites that can still be recovered (Active + risk > 40)."""
    df = store.df_site
    if package_name:
        df = df[df["package_name"] == package_name]
    if df.empty:
        return []

    mask = (df["site_status"] == "Active") & (df["risk_score"] >= 40)
    candidates = df[mask].sort_values("risk_score", ascending=False).head(limit)

    cols = [
        "package_name", "district", "site_name",
        "site_progress", "site_delay_days", "delay_bucket",
        "risk_score",
    ]
    available = [c for c in cols if c in candidates.columns]
    return df_to_records(candidates[available])


@router.get("/trends")
def risk_trends():
    """Historical risk score trends from snapshots."""
    snapshots = store.get_snapshots()
    if snapshots.empty:
        return []

    if "_snapshot_ts" not in snapshots.columns:
        return []

    # Aggregate by snapshot timestamp
    grp = snapshots.groupby("_snapshot_ts")
    result = []
    for ts, group in grp:
        result.append({
            "timestamp": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
            "avg_progress": round(float(group["site_progress"].mean()), 1) if "site_progress" in group.columns else 0,
            "avg_risk_score": round(float(group["risk_score"].mean()), 1) if "risk_score" in group.columns else 0,
            "total_sites": len(group),
        })
    return sorted(result, key=lambda x: x["timestamp"])


@router.get("/actual-vs-planned")
def actual_vs_planned(package_name: str | None = Query(None)):
    """
    Per-package actual progress vs planned (schedule-based) progress.

    planned_progress = avg of ((today - planned_start) / (planned_finish - planned_start) * 100)
                       across all tasks with valid dates, clipped to [0, 100].
    actual_progress  = avg site_progress across all sites in the package.
    """
    df_tasks = store.df_tasks
    df_site = store.df_site

    if df_tasks.empty or df_site.empty:
        return []

    if package_name:
        df_tasks = df_tasks[df_tasks["package_name"] == package_name]
        df_site = df_site[df_site["package_name"] == package_name]

    today = pd.Timestamp.now().normalize()

    # Compute per-task planned progress (schedule elapsed %)
    ps = df_tasks.get("planned_start")
    pf = df_tasks.get("planned_finish")

    result = []

    for pkg in df_site["package_name"].unique():
        pkg_tasks = df_tasks[df_tasks["package_name"] == pkg]
        pkg_sites = df_site[df_site["package_name"] == pkg]

        # Actual progress
        actual = round(float(pkg_sites["site_progress"].mean()), 1) if not pkg_sites.empty else 0.0

        # Planned (schedule-elapsed) progress
        planned = 0.0
        if "planned_start" in pkg_tasks.columns and "planned_finish" in pkg_tasks.columns:
            ps_col = pkg_tasks["planned_start"]
            pf_col = pkg_tasks["planned_finish"]
            valid = ps_col.notna() & pf_col.notna() & (pf_col > ps_col)
            if valid.any():
                total_dur = (pf_col[valid] - ps_col[valid]).dt.days
                elapsed = (today - ps_col[valid]).dt.days
                pct = (elapsed / total_dur * 100).clip(0, 100)
                planned = round(float(pct.mean()), 1)

        result.append({
            "package_name": pkg,
            "actual_progress": actual,
            "planned_progress": planned,
            "variance": round(actual - planned, 1),
        })

    result.sort(key=lambda x: x["package_name"])
    return result
