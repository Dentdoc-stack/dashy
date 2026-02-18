"""
loader.py — Fetch CSV data from Google Sheets, disk caching, snapshot versioning.
KP-HCIP Multi-Package Executive Dashboard
"""

import io
import os
import logging
from datetime import datetime, timedelta

import pandas as pd
import requests

from config import (
    CSV_SOURCES,
    COLUMN_RENAME_MAP,
    CACHE_DIR,
    CACHE_LATEST_DIR,
    CACHE_SNAPSHOTS_DIR,
    HTTP_TIMEOUT_SECONDS,
    INMEMORY_TTL_SECONDS,
    MAX_SNAPSHOT_RETENTION_DAYS,
    TIMEZONE,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Directory helpers
# ---------------------------------------------------------------------------

def _ensure_dirs():
    """Create cache directories if they don't exist."""
    for d in [CACHE_DIR, CACHE_LATEST_DIR, CACHE_SNAPSHOTS_DIR]:
        os.makedirs(d, exist_ok=True)


# ---------------------------------------------------------------------------
# Single CSV fetch
# ---------------------------------------------------------------------------

def _fetch_one_csv(name: str, url: str) -> pd.DataFrame | None:
    """
    Download a single CSV from a published Google Sheets URL.
    Returns DataFrame or None on failure.
    """
    try:
        resp = requests.get(url, timeout=HTTP_TIMEOUT_SECONDS)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
        # Strip whitespace from column headers
        df.columns = df.columns.str.strip()
        # Apply rename map
        df.rename(columns=COLUMN_RENAME_MAP, inplace=True)
        return df
    except Exception as exc:
        logger.warning("Failed to load %s: %s", name, exc)
        return None


# ---------------------------------------------------------------------------
# Fetch all CSVs and concatenate
# ---------------------------------------------------------------------------

def fetch_all_csvs() -> tuple[pd.DataFrame, list[str], list[str]]:
    """
    Fetch all 10 CSV sources, concatenate into a single DataFrame.
    Returns (df_tasks, succeeded_names, failed_names).
    """
    frames = []
    succeeded = []
    failed = []

    for name, url in CSV_SOURCES.items():
        df = _fetch_one_csv(name, url)
        if df is not None and not df.empty:
            frames.append(df)
            succeeded.append(name)
        else:
            failed.append(name)

    if frames:
        df_tasks = pd.concat(frames, ignore_index=True)
    else:
        df_tasks = pd.DataFrame()

    return df_tasks, succeeded, failed


# ---------------------------------------------------------------------------
# Disk cache: save / load latest
# ---------------------------------------------------------------------------

def save_latest_cache(df_tasks: pd.DataFrame, df_site: pd.DataFrame):
    """Persist latest df_tasks and df_site as Parquet files."""
    _ensure_dirs()
    df_tasks.to_parquet(os.path.join(CACHE_LATEST_DIR, "df_tasks.parquet"), index=False)
    df_site.to_parquet(os.path.join(CACHE_LATEST_DIR, "df_site.parquet"), index=False)


def load_latest_cache() -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """Load cached df_tasks and df_site from disk. Returns (None, None) if missing."""
    tasks_path = os.path.join(CACHE_LATEST_DIR, "df_tasks.parquet")
    site_path = os.path.join(CACHE_LATEST_DIR, "df_site.parquet")

    if os.path.exists(tasks_path) and os.path.exists(site_path):
        try:
            df_tasks = pd.read_parquet(tasks_path)
            df_site = pd.read_parquet(site_path)
            return df_tasks, df_site
        except Exception as exc:
            logger.warning("Failed to read cache: %s", exc)
    return None, None


def get_cache_timestamp() -> str | None:
    """Return the last modification time of the cached df_site file."""
    site_path = os.path.join(CACHE_LATEST_DIR, "df_site.parquet")
    if os.path.exists(site_path):
        mtime = os.path.getmtime(site_path)
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    return None


# ---------------------------------------------------------------------------
# Snapshot versioning (for trend charts)
# ---------------------------------------------------------------------------

def save_snapshot(df_site: pd.DataFrame):
    """Save a timestamped snapshot of df_site for trend analysis."""
    _ensure_dirs()
    now = datetime.now()
    filename = now.strftime("%Y-%m-%dT%H-%M-%S") + ".parquet"
    path = os.path.join(CACHE_SNAPSHOTS_DIR, filename)
    df_site_copy = df_site.copy()
    df_site_copy["_snapshot_ts"] = now
    df_site_copy.to_parquet(path, index=False)
    logger.info("Saved snapshot: %s", path)


def load_all_snapshots() -> pd.DataFrame:
    """Load and concatenate all historical snapshots. Returns empty DataFrame if none."""
    _ensure_dirs()
    snapshot_dir = CACHE_SNAPSHOTS_DIR
    files = sorted(
        [f for f in os.listdir(snapshot_dir) if f.endswith(".parquet")]
    )
    if not files:
        return pd.DataFrame()

    frames = []
    for f in files:
        try:
            df = pd.read_parquet(os.path.join(snapshot_dir, f))
            frames.append(df)
        except Exception as exc:
            logger.warning("Failed to load snapshot %s: %s", f, exc)

    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame()


def cleanup_old_snapshots():
    """Remove snapshots older than MAX_SNAPSHOT_RETENTION_DAYS."""
    _ensure_dirs()
    cutoff = datetime.now() - timedelta(days=MAX_SNAPSHOT_RETENTION_DAYS)
    snapshot_dir = CACHE_SNAPSHOTS_DIR

    for f in os.listdir(snapshot_dir):
        if not f.endswith(".parquet"):
            continue
        fpath = os.path.join(snapshot_dir, f)
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            if mtime < cutoff:
                os.remove(fpath)
                logger.info("Removed old snapshot: %s", fpath)
        except Exception as exc:
            logger.warning("Failed to remove snapshot %s: %s", f, exc)


# ---------------------------------------------------------------------------
# Main entry: get data (cached or fresh)
# ---------------------------------------------------------------------------

def get_data(force_refresh: bool = False):
    """
    Main data loading function. Uses layered caching:
    1. Disk cache (Parquet)
    2. Fresh fetch from Google Sheets

    Returns (df_tasks, df_site, warnings_list)
    """
    from transform import clean_tasks, build_site_summary

    warnings_list = []

    if not force_refresh:
        # Try disk cache first
        df_tasks, df_site = load_latest_cache()
        if df_tasks is not None and df_site is not None:
            ts = get_cache_timestamp()
            warnings_list.append(f"Loaded from cache ({ts})")
            return df_tasks, df_site, warnings_list

    # Fresh fetch
    df_tasks_raw, succeeded, failed = fetch_all_csvs()

    if failed:
        warnings_list.append(f"Failed to load: {', '.join(failed)}")

    if df_tasks_raw.empty:
        # Try fallback to cache
        df_tasks, df_site = load_latest_cache()
        if df_tasks is not None and df_site is not None:
            ts = get_cache_timestamp()
            warnings_list.append(
                f"All sources unavailable — showing cached data from {ts}"
            )
            return df_tasks, df_site, warnings_list
        else:
            warnings_list.append("No data available — check network and try again")
            return pd.DataFrame(), pd.DataFrame(), warnings_list

    # Clean and build
    df_tasks = clean_tasks(df_tasks_raw)
    df_site = build_site_summary(df_tasks)

    # Persist
    save_latest_cache(df_tasks, df_site)

    if force_refresh:
        save_snapshot(df_site)
        cleanup_old_snapshots()

    warnings_list.insert(
        0, f"Loaded {len(succeeded)}/{len(CSV_SOURCES)} sources successfully"
    )

    return df_tasks, df_site, warnings_list
