"""
data_store.py — In-memory data management for the FastAPI backend.
Replaces Streamlit's @st.cache_data with a simple TTL-based singleton.
"""

import sys
import os
import time
import logging
from threading import Lock

import pandas as pd

# Add parent directory to path so we can import root-level modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import INMEMORY_TTL_SECONDS
from loader import (
    fetch_all_csvs,
    save_latest_cache,
    load_latest_cache,
    save_snapshot,
    cleanup_old_snapshots,
    get_cache_timestamp,
    load_all_snapshots,
)
from transform import (
    clean_tasks,
    build_site_summary,
    build_package_summary,
    build_district_summary,
    extract_package_metadata,
)

logger = logging.getLogger(__name__)


class DataStore:
    """Thread-safe singleton that holds the current data frames."""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._data_lock = Lock()
        self.df_tasks: pd.DataFrame = pd.DataFrame()
        self.df_site: pd.DataFrame = pd.DataFrame()
        self.df_pkg: pd.DataFrame = pd.DataFrame()
        self.df_dist: pd.DataFrame = pd.DataFrame()
        self.warnings: list[str] = []
        self._last_refresh: float = 0
        self._cache_ts: str | None = None

    @property
    def is_stale(self) -> bool:
        if self._last_refresh == 0:
            return True
        return (time.time() - self._last_refresh) > INMEMORY_TTL_SECONDS

    @property
    def cache_timestamp(self) -> str | None:
        return self._cache_ts

    def load(self, force_refresh: bool = False) -> list[str]:
        """Load data (from cache or fresh). Returns warnings list."""
        with self._data_lock:
            if not force_refresh and not self.is_stale and not self.df_tasks.empty:
                return self.warnings

            warnings: list[str] = []

            if not force_refresh:
                df_tasks, df_site = load_latest_cache()
                if df_tasks is not None and df_site is not None and not df_tasks.empty:
                    ts = get_cache_timestamp()
                    warnings.append(f"Loaded from cache ({ts})")
                    self._set_data(df_tasks, df_site, warnings)
                    return warnings

            # Fresh fetch
            df_tasks_raw, succeeded, failed = fetch_all_csvs()

            if failed:
                warnings.append(f"Failed to load: {', '.join(failed)}")

            if df_tasks_raw.empty:
                # Fallback to cache
                df_tasks, df_site = load_latest_cache()
                if df_tasks is not None and df_site is not None:
                    ts = get_cache_timestamp()
                    warnings.append(f"All sources unavailable — cached data from {ts}")
                    self._set_data(df_tasks, df_site, warnings)
                    return warnings
                else:
                    warnings.append("No data available — check network and try again")
                    self.warnings = warnings
                    return warnings

            # Clean and build
            df_tasks = clean_tasks(df_tasks_raw)
            df_site = build_site_summary(df_tasks)

            # Persist
            save_latest_cache(df_tasks, df_site)

            if force_refresh:
                save_snapshot(df_site)
                cleanup_old_snapshots()

            warnings.insert(0, f"Loaded {len(succeeded)}/{10} sources successfully")
            self._set_data(df_tasks, df_site, warnings)
            return warnings

    def _set_data(self, df_tasks: pd.DataFrame, df_site: pd.DataFrame, warnings: list[str]):
        self.df_tasks = df_tasks
        self.df_site = df_site
        
        # Extract package-level metadata
        df_pkg_meta = extract_package_metadata(df_tasks) if not df_tasks.empty else pd.DataFrame()
        
        # Build package summary with metadata
        self.df_pkg = build_package_summary(df_site, df_pkg_meta) if not df_site.empty else pd.DataFrame()
        self.df_dist = build_district_summary(df_site) if not df_site.empty else pd.DataFrame()
        
        self.warnings = warnings
        self._last_refresh = time.time()
        self._cache_ts = get_cache_timestamp()

    def get_snapshots(self) -> pd.DataFrame:
        return load_all_snapshots()


# Module-level singleton
store = DataStore()
