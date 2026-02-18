"""
situation_room_router.py — Situation Room page endpoints.
Executive overview: KPIs, delay distribution, status breakdown, compliance.
"""

from fastapi import APIRouter, Query
from backend.data_store import store
from backend.utils import df_to_records, filter_df

router = APIRouter()


@router.get("/kpis")
def situation_kpis(package_name: str | None = Query(None)):
    """Core KPIs for the situation room."""
    df = store.df_site
    if package_name:
        df = df[df["package_name"] == package_name]
    if df.empty:
        return {
            "total_sites": 0,
            "avg_progress": 0,
            "active": 0,
            "completed": 0,
            "inactive": 0,
            "delayed_gt30": 0,
            "delayed_gt60": 0,
        }
    return {
        "total_sites": len(df),
        "avg_progress": round(float(df["site_progress"].mean()), 1),
        "active": int((df["site_status"] == "Active").sum()),
        "completed": int((df["site_status"] == "Completed").sum()),
        "inactive": int((df["site_status"] == "Inactive").sum()),
        "delayed_gt30": int((df["site_delay_days"] > 30).sum()),
        "delayed_gt60": int((df["site_delay_days"] > 60).sum()),
    }


@router.get("/delay-distribution")
def delay_distribution(package_name: str | None = Query(None)):
    """Delay bucket counts for bar/pie charts."""
    df = store.df_site
    if package_name:
        df = df[df["package_name"] == package_name]
    if df.empty:
        return []

    counts = df["delay_bucket"].value_counts()
    order = ["On Track", "1-30", "31-60", ">60"]
    result = []
    for bucket in order:
        result.append({
            "bucket": bucket,
            "count": int(counts.get(bucket, 0)),
        })
    return result


@router.get("/status-breakdown")
def status_breakdown(package_name: str | None = Query(None)):
    """Site status counts for donut/pie chart."""
    df = store.df_site
    if package_name:
        df = df[df["package_name"] == package_name]
    if df.empty:
        return []

    counts = df["site_status"].value_counts()
    return [{"status": k, "count": int(v)} for k, v in counts.items()]


@router.get("/compliance")
def compliance_summary(package_name: str | None = Query(None)):
    """Compliance rates for CESMPS, OHS, RFB (package-level)."""
    df = store.df_pkg
    if package_name:
        df = df[df["package_name"] == package_name]
    if df.empty:
        return {"cesmps": 0, "ohs": 0, "rfb": 0}

    n = max(len(df), 1)

    def pct_yes(col):
        if col not in df.columns:
            return 0
        return round(float((df[col] == "Yes").sum()) / n * 100, 1)

    return {
        "cesmps": pct_yes("cesmps"),
        "ohs": pct_yes("ohs_yesno"),
        "rfb": pct_yes("rfb_staff_yesno"),
    }


@router.get("/progress-by-package")
def progress_by_package():
    """Average progress per package for the overview bar chart."""
    df = store.df_pkg
    if df.empty:
        return []
    return df_to_records(df[["package_name", "avg_progress", "total_sites",
                             "active_sites", "completed_sites", "inactive_sites"]].copy())


@router.get("/red-list")
def red_list(package_name: str | None = Query(None), limit: int = Query(20)):
    """Sites needing immediate attention (high risk score)."""
    df = store.df_site
    if package_name:
        df = df[df["package_name"] == package_name]
    if df.empty:
        return []

    cols = ["package_name", "district", "site_name", "site_progress",
            "site_delay_days", "delay_bucket", "risk_score", "site_status"]
    available = [c for c in cols if c in df.columns]
    result = df[available].sort_values("risk_score", ascending=False).head(limit)
    return df_to_records(result)
