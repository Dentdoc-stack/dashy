"""
filters_router.py — Endpoints for populating filter dropdowns.
"""

from fastapi import APIRouter, Query
from backend.data_store import store

router = APIRouter()


@router.get("/packages")
def list_packages():
    """Return distinct package names."""
    if store.df_site.empty:
        return []
    return sorted(store.df_site["package_name"].dropna().unique().tolist())


@router.get("/districts")
def list_districts(package_name: str | None = Query(None)):
    """Return distinct districts, optionally filtered by package."""
    df = store.df_site
    if df.empty:
        return []
    if package_name:
        df = df[df["package_name"] == package_name]
    return sorted(df["district"].dropna().unique().tolist())


@router.get("/sites")
def list_sites(
    package_name: str | None = Query(None),
    district: str | None = Query(None),
):
    """Return distinct site names, optionally filtered."""
    df = store.df_site
    if df.empty:
        return []
    if package_name:
        df = df[df["package_name"] == package_name]
    if district:
        df = df[df["district"] == district]
    return sorted(df["site_name"].dropna().unique().tolist())


@router.get("/statuses")
def list_statuses():
    """Return distinct site statuses."""
    if store.df_site.empty:
        return []
    return sorted(store.df_site["site_status"].dropna().unique().tolist())
