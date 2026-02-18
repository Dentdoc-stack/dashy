"""
transform.py — Data cleaning (§8) and site summary / risk scoring (§9).
KP-HCIP Multi-Package Executive Dashboard
"""

import logging
from datetime import datetime

import numpy as np
import pandas as pd
from dateutil import tz

from config import (
    SITE_KEY,
    DATE_COLUMNS,
    IPC_COLUMNS,
    IPC_STATUS_PRIORITY,
    IPC_BLANK_DEFAULT,
    COMPLETION_THRESHOLD,
    LOW_PROGRESS_THRESHOLD,
    DELAY_BUCKET_CUTOFFS,
    DELAY_SCORE_MAP,
    PROGRESS_SCORE_BRACKETS,
    MOBILIZATION_PENALTY,
    TIMEZONE,
)

logger = logging.getLogger(__name__)

# ===================================================================
# §8  CLEANING & NORMALIZATION
# ===================================================================

def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """§8.1 — Parse DD/MM/YYYY date columns with dayfirst=True."""
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
    # Validation warnings
    if "actual_start" in df.columns and "actual_finish" in df.columns:
        mask = (df["actual_start"].notna() & df["actual_finish"].notna() &
                (df["actual_start"] > df["actual_finish"]))
        if mask.any():
            logger.warning(
                "%d rows have actual_start > actual_finish", mask.sum()
            )
    if "planned_start" in df.columns and "planned_finish" in df.columns:
        mask = (df["planned_start"].notna() & df["planned_finish"].notna() &
                (df["planned_start"] > df["planned_finish"]))
        if mask.any():
            logger.warning(
                "%d rows have planned_start > planned_finish", mask.sum()
            )
    return df


def _normalize_yes_no(series: pd.Series) -> pd.Series:
    """§8.2 — Normalize Yes/No fields."""
    s = series.astype(str).str.strip().str.lower()
    return s.map(lambda x: "Yes" if x == "yes" else ("No" if x == "no" else "Unknown"))


def _parse_monthly_field(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    """
    §8.3 — Split 'January - No' format into (month, yesno).
    Returns two Series: month_series, yesno_series.
    """
    month_vals = []
    yesno_vals = []
    for val in series.fillna(""):
        val = str(val).strip()
        if " - " in val:
            parts = val.split(" - ", 1)
            month_vals.append(parts[0].strip())
            yn = parts[1].strip().lower()
            yesno_vals.append("Yes" if yn == "yes" else ("No" if yn == "no" else "Unknown"))
        else:
            month_vals.append("")
            yesno_vals.append("Unknown" if val == "" or val.lower() == "nan" else "Unknown")
    return pd.Series(month_vals, index=series.index), pd.Series(yesno_vals, index=series.index)


def _normalize_ipc(series: pd.Series) -> pd.Series:
    """§8.5 — Normalize IPC status columns."""
    valid = {"not submitted", "submitted", "in process", "released"}
    canonical = {
        "not submitted": "Not Submitted",
        "submitted": "Submitted",
        "in process": "In Process",
        "released": "Released",
    }

    def _norm(val):
        v = str(val).strip().lower()
        if v in canonical:
            return canonical[v]
        return IPC_BLANK_DEFAULT

    return series.map(_norm)


def _clean_progress(series: pd.Series) -> pd.Series:
    """§8.6 — Clean progress_pct: strip %, cast to float, clamp [0, 100]."""
    s = series.astype(str).str.replace("%", "", regex=False).str.strip()
    numeric = pd.to_numeric(s, errors="coerce").fillna(0.0)
    out_of_range = (numeric < 0) | (numeric > 100)
    if out_of_range.any():
        logger.warning(
            "%d rows have progress_pct outside [0, 100]", out_of_range.sum()
        )
    return numeric.clip(0, 100)


# ---------------------------------------------------------------------------
# Master cleaning pipeline
# ---------------------------------------------------------------------------

def clean_tasks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline (§8.0 through §8.6).
    Expects column renaming already done by loader.
    """
    df = df.copy()

    # §8.1 — Parse dates
    df = _parse_dates(df)

    # §8.2 — Normalize mobilization_taken (Yes/No)
    if "mobilization_taken" in df.columns:
        df["mobilization_taken"] = _normalize_yes_no(df["mobilization_taken"])

    # §8.3 — Monthly fields: ohs, rfb_staff
    if "ohs" in df.columns:
        df["ohs_month"], df["ohs_yesno"] = _parse_monthly_field(df["ohs"])
    if "rfb_staff" in df.columns:
        df["rfb_staff_month"], df["rfb_staff_yesno"] = _parse_monthly_field(df["rfb_staff"])

    # §8.4 — CESMPS (plain Yes/No)
    if "cesmps" in df.columns:
        df["cesmps"] = _normalize_yes_no(df["cesmps"])

    # §8.5 — IPC 1-6
    for col in IPC_COLUMNS:
        if col in df.columns:
            df[col] = _normalize_ipc(df[col])

    # §8.6 — Progress
    if "progress_pct" in df.columns:
        df["progress_pct"] = _clean_progress(df["progress_pct"])

    # §9.1 — Task-level delay
    df = _compute_task_delay(df)

    # Task-level status (§9.5 precursor)
    df = _compute_task_status(df)

    return df


# ===================================================================
# §9  CALCULATIONS
# ===================================================================

def _get_today():
    """Current date in Asia/Karachi timezone, as a Timestamp."""
    return pd.Timestamp.now(tz=tz.gettz(TIMEZONE)).normalize().tz_localize(None)


def _compute_task_delay(df: pd.DataFrame) -> pd.DataFrame:
    """§9.1 — Task-level delay (date-based).

    task_delay_days:    days overdue (clipped to 0; NaN if no planned_finish).
    task_duration_days: planned duration in days, used as weight in site-level
                        weighted-average delay aggregation (min 1 day).
    """
    today = _get_today()

    pf = df.get("planned_finish")
    af = df.get("actual_finish")
    ps = df.get("planned_start")

    if pf is None:
        df["task_delay_days"] = np.nan
        df["task_duration_days"] = np.nan
        return df

    effective_finish = af.copy() if af is not None else pd.Series(pd.NaT, index=df.index)
    effective_finish = effective_finish.fillna(today)

    raw_delay = (effective_finish - pf).dt.days
    df["task_delay_days"] = raw_delay.clip(lower=0)
    # Where planned_finish is missing → NaN
    df.loc[pf.isna(), "task_delay_days"] = np.nan

    # Task duration (planned_finish − planned_start), minimum 1 day to avoid zero weights
    if ps is not None:
        duration = (pf - ps).dt.days.clip(lower=1)
        df["task_duration_days"] = duration.where(pf.notna() & ps.notna(), other=np.nan)
    else:
        df["task_duration_days"] = np.nan

    return df


def _compute_task_status(df: pd.DataFrame) -> pd.DataFrame:
    """§9.5 — Task-level status derivation."""
    conditions = [
        (df["progress_pct"] >= 100) | (df.get("actual_finish", pd.Series(dtype="object")).notna()),
        (df["progress_pct"] > 0) | (df.get("actual_start", pd.Series(dtype="object")).notna()),
    ]
    choices = ["Completed", "In Progress"]
    df["task_status"] = np.select(conditions, choices, default="Not Started")
    return df


# ---------------------------------------------------------------------------
# Build df_site (Layer B)
# ---------------------------------------------------------------------------

def _delay_bucket(delay_days):
    """§9.3 — Map delay days to bucket label."""
    if pd.isna(delay_days) or delay_days == 0:
        return "On Track"
    if delay_days <= DELAY_BUCKET_CUTOFFS[1]:
        return "1-30"
    if delay_days <= DELAY_BUCKET_CUTOFFS[2]:
        return "31-60"
    return ">60"


def _delay_score(bucket: str) -> int:
    """§9.7 — Delay component of risk score."""
    return DELAY_SCORE_MAP.get(bucket, 0)


def _progress_score(pct: float) -> int:
    """§9.7 — Progress component of risk score."""
    for lo, hi, score in PROGRESS_SCORE_BRACKETS:
        if lo <= pct < hi:
            return score
    # pct >= 100
    return 0


def _best_ipc_status(row, ipc_cols):
    """§9.8 — Best IPC status across IPC 1–6."""
    best = "Not Submitted"
    best_priority = 0
    for col in ipc_cols:
        val = row.get(col, IPC_BLANK_DEFAULT)
        p = IPC_STATUS_PRIORITY.get(val, 0)
        if p > best_priority:
            best_priority = p
            best = val
    return best


def extract_package_metadata(df_tasks: pd.DataFrame) -> pd.DataFrame:
    """
    Extract package-level metadata (CESMPS, OHS, RFB, IPC, mobilization).
    These are package attributes, not site attributes - take first value per package.
    """
    if df_tasks.empty:
        return pd.DataFrame()
    
    pkg_grp = df_tasks.groupby("package_name", dropna=False)
    
    metadata = {"package_name": pkg_grp.size().index.tolist()}
    
    # Mobilization (package-level)
    if "mobilization_taken" in df_tasks.columns:
        metadata["mobilization_taken"] = pkg_grp["mobilization_taken"].first().values
    
    # CESMPS (package-level)
    if "cesmps" in df_tasks.columns:
        metadata["cesmps"] = pkg_grp["cesmps"].first().values
    
    # OHS (package-level)
    if "ohs_yesno" in df_tasks.columns:
        metadata["ohs_yesno"] = pkg_grp["ohs_yesno"].first().values
    if "ohs_month" in df_tasks.columns:
        metadata["ohs_month"] = pkg_grp["ohs_month"].first().values
    
    # RFB Staff (package-level)
    if "rfb_staff_yesno" in df_tasks.columns:
        metadata["rfb_staff_yesno"] = pkg_grp["rfb_staff_yesno"].first().values
    if "rfb_staff_month" in df_tasks.columns:
        metadata["rfb_staff_month"] = pkg_grp["rfb_staff_month"].first().values
    
    # IPC stages (package-level)
    for col in IPC_COLUMNS:
        if col in df_tasks.columns:
            metadata[col] = pkg_grp[col].first().values
    
    df_pkg_meta = pd.DataFrame(metadata)
    
    # Calculate best IPC stage
    ipc_cols_in_meta = [c for c in IPC_COLUMNS if c in df_pkg_meta.columns]
    if ipc_cols_in_meta:
        df_pkg_meta["ipc_best_stage"] = df_pkg_meta.apply(
            lambda row: _best_ipc_status(row, ipc_cols_in_meta),
            axis=1
        )
    
    return df_pkg_meta


def build_site_summary(df_tasks: pd.DataFrame) -> pd.DataFrame:
    """
    Build df_site (Layer B) — one row per (package_name, district, site_name).
    Implements §9.2 through §9.8.
    """
    if df_tasks.empty:
        return pd.DataFrame()

    grp = df_tasks.groupby(SITE_KEY, dropna=False)

    # §9.2 — Site-level delay (duration-weighted average, split by task status)
    #
    # active_delay_days     — weighted avg delay of In Progress tasks (current problems)
    # historical_delay_days — weighted avg delay of Completed tasks (past performance)
    # site_delay_days       — active delay when In Progress tasks are delayed;
    #                         falls back to historical delay; 0 when both are NaN

    def _weighted_avg_delay(sub_df, status_filter):
        """Duration-weighted average of task_delay_days for tasks matching status_filter."""
        mask = sub_df["task_status"].isin(status_filter) & sub_df["task_delay_days"].notna()
        filtered = sub_df[mask]
        if filtered.empty:
            return np.nan
        weights = filtered["task_duration_days"].fillna(1.0)
        return float(np.average(filtered["task_delay_days"], weights=weights))

    active_delay = grp.apply(
        lambda s: _weighted_avg_delay(s, ["In Progress"]),
        include_groups=False,
    ).rename("active_delay_days")

    historical_delay = grp.apply(
        lambda s: _weighted_avg_delay(s, ["Completed"]),
        include_groups=False,
    ).rename("historical_delay_days")

    # site_delay_days: prioritise active; fall back to historical; 0 if neither exists
    site_delay = active_delay.combine_first(historical_delay).fillna(0).rename("site_delay_days")

    # §9.4 — Discipline-balanced site progress
    disc_key = SITE_KEY + ["discipline"]
    disc_progress = (
        df_tasks.groupby(disc_key, dropna=False)["progress_pct"]
        .mean()
        .reset_index()
        .rename(columns={"progress_pct": "discipline_progress"})
    )
    site_progress = (
        disc_progress.groupby(SITE_KEY, dropna=False)["discipline_progress"]
        .mean()
        .rename("site_progress")
    )

    # §9.5 — Site status
    def _site_status_agg(sub):
        statuses = set(sub["task_status"])
        progress = site_progress.get(tuple(sub.name) if isinstance(sub.name, tuple) else sub.name, 0)
        if statuses == {"Not Started"}:
            return "Inactive"
        if progress >= COMPLETION_THRESHOLD:
            return "Completed"
        return "Active"

    site_status = grp.apply(_site_status_agg, include_groups=False).rename("site_status")

    # NOTE: Mobilization, CESMPS, OHS, RFB, and IPC are package-level attributes
    # They are extracted via extract_package_metadata() and merged at package level
    # Do NOT aggregate them from tasks to sites as they're package-wide, not site-specific

    # Informational columns: package_id, site_id (first non-null)
    info_cols = {}
    for col in ["package_id", "site_id"]:
        if col in df_tasks.columns:
            info_cols[col] = grp[col].first()

    # Earliest planned_start for the site (used in red-list logic)
    if "planned_start" in df_tasks.columns:
        earliest_start = grp["planned_start"].min().rename("earliest_planned_start")
    else:
        earliest_start = pd.Series(pd.NaT, index=site_delay.index, name="earliest_planned_start")

    # Last updated
    if "last_updated" in df_tasks.columns:
        last_upd = grp["last_updated"].max().rename("last_updated")
    else:
        last_upd = pd.Series(pd.NaT, index=site_delay.index, name="last_updated")

    # Task count
    task_count = grp.size().rename("task_count")

    # Assemble df_site
    df_site = pd.DataFrame({
        "site_delay_days": site_delay,
        "active_delay_days": active_delay,
        "historical_delay_days": historical_delay,
        "site_progress": site_progress,
        "site_status": site_status,
        "earliest_planned_start": earliest_start,
        "last_updated": last_upd,
        "task_count": task_count,
    })

    # Add info columns
    for col, series in info_cols.items():
        df_site[col] = series

    df_site = df_site.reset_index()

    # --- Derived fields ---

    # §9.3 — Delay bucket
    df_site["delay_bucket"] = df_site["site_delay_days"].apply(_delay_bucket)

    # §9.7 — Risk score (without mobilization component for now)
    df_site["delay_score"] = df_site["delay_bucket"].map(_delay_score)
    df_site["progress_score"] = df_site["site_progress"].apply(_progress_score)
    df_site["risk_score"] = (
        df_site["delay_score"] +
        df_site["progress_score"]
    )

    return df_site


# ---------------------------------------------------------------------------
# Layer C — Package and District aggregates
# ---------------------------------------------------------------------------

def build_package_summary(df_site: pd.DataFrame, df_pkg_meta: pd.DataFrame = None) -> pd.DataFrame:
    """Aggregate df_site to package level and merge package metadata."""
    if df_site.empty:
        return pd.DataFrame()

    grp = df_site.groupby("package_name", dropna=False)

    df_pkg = pd.DataFrame({
        "total_sites": grp.size(),
        "avg_progress": grp["site_progress"].mean(),
        "active_sites": grp["site_status"].apply(lambda s: (s == "Active").sum()),
        "inactive_sites": grp["site_status"].apply(lambda s: (s == "Inactive").sum()),
        "completed_sites": grp["site_status"].apply(lambda s: (s == "Completed").sum()),
        "sites_gt30_delayed": grp["site_delay_days"].apply(lambda s: (s > 30).sum()),
        "sites_gt60_delayed": grp["site_delay_days"].apply(lambda s: (s > 60).sum()),
    }).reset_index()

    # Merge package-level metadata (CESMPS, OHS, RFB, IPC, mobilization)
    if df_pkg_meta is not None and not df_pkg_meta.empty:
        df_pkg = df_pkg.merge(df_pkg_meta, on="package_name", how="left")

    return df_pkg


def build_district_summary(df_site: pd.DataFrame) -> pd.DataFrame:
    """Aggregate df_site to district level (within selected packages)."""
    if df_site.empty:
        return pd.DataFrame()

    grp = df_site.groupby(["package_name", "district"], dropna=False)

    df_dist = pd.DataFrame({
        "total_sites": grp.size(),
        "avg_progress": grp["site_progress"].mean().round(1),
        "sites_gt60_delayed": grp["site_delay_days"].apply(lambda s: (s > 60).sum()),
        "inactive_sites": grp["site_status"].apply(lambda s: (s == "Inactive").sum()),
    }).reset_index()

    return df_dist
