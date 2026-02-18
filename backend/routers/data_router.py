"""
data_router.py — Core data endpoints: refresh, summary stats, raw data.
"""

from fastapi import APIRouter, Query
from backend.data_store import store
from backend.utils import df_to_records, filter_df

router = APIRouter()


@router.post("/refresh")
def refresh_data():
    """Force a fresh data load from Google Sheets."""
    warnings = store.load(force_refresh=True)
    return {
        "status": "refreshed",
        "warnings": warnings,
        "rows_tasks": len(store.df_tasks),
        "rows_sites": len(store.df_site),
    }


@router.get("/summary")
def global_summary():
    """High-level KPIs across all packages."""
    df = store.df_site
    if df.empty:
        return {"total_sites": 0, "total_tasks": 0}

    return {
        "total_sites": len(df),
        "total_tasks": len(store.df_tasks),
        "active_sites": int((df["site_status"] == "Active").sum()),
        "completed_sites": int((df["site_status"] == "Completed").sum()),
        "inactive_sites": int((df["site_status"] == "Inactive").sum()),
        "avg_progress": round(float(df["site_progress"].mean()), 1),
        "sites_gt30_delayed": int((df["site_delay_days"] > 30).sum()),
        "sites_gt60_delayed": int((df["site_delay_days"] > 60).sum()),
        "cache_timestamp": store.cache_timestamp,
        "warnings": store.warnings,
    }


@router.get("/sites")
def get_sites(
    package_name: str | None = Query(None),
    district: str | None = Query(None),
    status: str | None = Query(None),
):
    """Return site-level data with optional filters."""
    df = filter_df(store.df_site, package_name=package_name, district=district, status=status)
    return df_to_records(df)


@router.get("/tasks")
def get_tasks(
    package_name: str | None = Query(None),
    district: str | None = Query(None),
    site_name: str | None = Query(None),
):
    """Return task-level data with optional filters."""
    df = store.df_tasks.copy()
    if package_name:
        df = df[df["package_name"] == package_name]
    if district:
        df = df[df["district"] == district]
    if site_name:
        df = df[df["site_name"] == site_name]
    return df_to_records(df)
