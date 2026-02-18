"""
site_router.py — Site Command Center endpoints.
Site-level detail, tasks, IPC status, photos.
"""

from fastapi import APIRouter, Query
from backend.data_store import store
from backend.utils import df_to_records

router = APIRouter()


@router.get("/detail")
def site_detail(
    package_name: str = Query(...),
    district: str = Query(...),
    site_name: str = Query(...),
):
    """Full site detail by composite key."""
    df = store.df_site
    if df.empty:
        return None

    mask = (
        (df["package_name"] == package_name)
        & (df["district"] == district)
        & (df["site_name"] == site_name)
    )
    row = df[mask]
    if row.empty:
        return None

    return df_to_records(row)[0]


@router.get("/tasks")
def site_tasks(
    package_name: str = Query(...),
    district: str = Query(...),
    site_name: str = Query(...),
):
    """All tasks for a specific site."""
    df = store.df_tasks
    if df.empty:
        return []

    mask = (
        (df["package_name"] == package_name)
        & (df["district"] == district)
        & (df["site_name"] == site_name)
    )
    tasks = df[mask]

    cols = [
        "discipline", "task_name", "planned_start", "planned_finish",
        "actual_start", "actual_finish", "planned_duration_days",
        "progress_pct", "task_delay_days", "task_status",
        "delay_flag_calc", "remarks",
    ]
    available = [c for c in cols if c in tasks.columns]
    return df_to_records(tasks[available])


@router.get("/ipc")
def site_ipc(
    package_name: str = Query(...),
    district: str = Query(...),
    site_name: str = Query(...),
):
    """IPC status for a specific site."""
    df = store.df_site
    if df.empty:
        return {}

    mask = (
        (df["package_name"] == package_name)
        & (df["district"] == district)
        & (df["site_name"] == site_name)
    )
    row = df[mask]
    if row.empty:
        return {}

    ipc_cols = ["ipc_1", "ipc_2", "ipc_3", "ipc_4", "ipc_5", "ipc_6", "ipc_best_stage"]
    result = {}
    for col in ipc_cols:
        if col in row.columns:
            val = row.iloc[0][col]
            result[col] = val if isinstance(val, str) else str(val) if val else "Not Submitted"
    return result


@router.get("/photos")
def site_photos(
    package_name: str = Query(...),
    district: str = Query(...),
    site_name: str = Query(...),
):
    """Before/after photo URLs for tasks at a specific site."""
    df = store.df_tasks
    if df.empty:
        return []

    mask = (
        (df["package_name"] == package_name)
        & (df["district"] == district)
        & (df["site_name"] == site_name)
    )
    tasks = df[mask]

    photo_cols = [
        "before_photo_share_url", "before_photo_direct_url",
        "after_photo_share_url", "after_photo_direct_url",
    ]

    result = []
    for _, row in tasks.iterrows():
        entry = {"task_name": row.get("task_name", ""), "discipline": row.get("discipline", "")}
        has_photo = False
        for col in photo_cols:
            val = row.get(col)
            if val and str(val).strip() and str(val).lower() != "nan":
                entry[col] = str(val).strip()
                has_photo = True
            else:
                entry[col] = None
        if has_photo:
            result.append(entry)
    return result
