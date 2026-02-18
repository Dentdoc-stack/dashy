"""
package_router.py — Package-level endpoints.
Package summary table, district drill-down, per-package charts.
"""

from fastapi import APIRouter, Query
from backend.data_store import store
from backend.utils import df_to_records, filter_df

router = APIRouter()


@router.get("/")
def list_packages():
    """Package summary table with all aggregated metrics."""
    df = store.df_pkg
    if df.empty:
        return []
    return df_to_records(df)


@router.get("/{package_name}")
def package_detail(package_name: str):
    """Detailed data for a specific package."""
    df_pkg = store.df_pkg
    if df_pkg.empty:
        return {"package": None, "districts": [], "sites": []}

    pkg_row = df_pkg[df_pkg["package_name"] == package_name]
    pkg_data = df_to_records(pkg_row)[0] if not pkg_row.empty else None

    # District breakdown within this package
    df_dist = store.df_dist
    districts = df_to_records(
        df_dist[df_dist["package_name"] == package_name]
    ) if not df_dist.empty else []

    # Sites within this package
    sites = df_to_records(
        filter_df(store.df_site, package_name=package_name)
    )

    return {
        "package": pkg_data,
        "districts": districts,
        "sites": sites,
    }


@router.get("/{package_name}/districts")
def package_districts(package_name: str):
    """District-level summary within a package."""
    df = store.df_dist
    if df.empty:
        return []
    return df_to_records(df[df["package_name"] == package_name])


@router.get("/{package_name}/sites")
def package_sites(package_name: str, district: str | None = Query(None)):
    """All sites within a package, optionally filtered by district."""
    df = filter_df(store.df_site, package_name=package_name, district=district)
    return df_to_records(df)


@router.get("/{package_name}/delay-chart")
def package_delay_chart(package_name: str):
    """Delay distribution for a specific package."""
    df = store.df_site[store.df_site["package_name"] == package_name] if not store.df_site.empty else store.df_site
    if df.empty:
        return []
    counts = df["delay_bucket"].value_counts()
    order = ["On Track", "1-30", "31-60", ">60"]
    return [{"bucket": b, "count": int(counts.get(b, 0))} for b in order]
