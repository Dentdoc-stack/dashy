"""
config.py — CSV links, constants, column rename map, and all configurable parameters.
KP-HCIP Multi-Package Executive Dashboard
"""

# ---------------------------------------------------------------------------
# CSV Data Sources (Published Google Sheets)
# ---------------------------------------------------------------------------
CSV_SOURCES = {
    "Flood Package-1": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQUvCNby9_znIiirFF8TFvaxJZOShZBlUpojKTpdEnQHxeyk6OMZxjN21r8dsBZOUNRc_cHFbcql7--/pub?output=csv",
    "Flood Package-2": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv5GK2QLH1avgzt1ZPVESAFL-lXV5S3QuldW8fsmBYM5fxv6UmLC2Wrww3Pv7lqkBhdKdUZRzWsfeP/pub?output=csv",
    "Flood Package-3": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRuPg-9VWBqev1bs_AZYKqQV6-9C8wlVyo2y6ewjNMxwLuEzm1OXURKZrLDb6O2dTsdpJ9iIYKIlnyo/pub?output=csv",
    "Flood Package-4": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQlUGmqa0SjavAOLnVML_IMAIvnVw5Jtza3z7Tr-norg6yIZYv4GPR6BVGnj7ox7Tshwz6ZrFSxhJTr/pub?output=csv",
    "Flood Package-5": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS8lttkvWeCBNiQwY9N1yuuQqVLuKUi809JkBh9wD15ko31JlqNwvFrHpAMDf3kxrz63-Acul7jM3es/pub?output=csv",
    "BEmONC New Construction Package-6": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTX2fHyqqmdrtemmhVh0pDi3WOH0zOXWk6blv--r9PVzm1Mz0Gr6jqE4IxDI66FC-42FLw4X3ye5hEz/pub?output=csv",
    "BEmONC Rehab Package-7": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRBwi3MLqWQC5SPJsFBS6DHS1SCMlNyxDlVceblbIe3yf4RGYzTueN7T9JKpN1HERVy2qAKKa6ziLvB/pub?output=csv",
    "BEmONC Prefab Package-8": "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8ioVcUUv9VXS48-z6-gWirSNDjDZFx9CW0lhlJqF4W7XFBaRGZXrvtmh9OCnLtQOVjiJ5t9dooMXV/pub?output=csv",
    "CEmONC Package-9": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRg6nKPwYTF4HvWzFnEp4hyqmyt9mMMjbE0LKVQPwWQ_cB5y1F3BhjelizGcvJzVzEvnnHtMv58dvQc/pub?output=csv",
    "Warehouses Package-10": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTrpyYcmR_1-9Apkn0l3O7NQHLcrx2hDe52NDxjO4KwofiAG1EWaKfYJPESyNjb8SjP2fWScshd6zMP/pub?output=csv",
}

# ---------------------------------------------------------------------------
# Column Rename Map  (raw CSV header → canonical snake_case)
# ---------------------------------------------------------------------------
COLUMN_RENAME_MAP = {
    "Mobilization Advance Taken": "mobilization_taken",
    "No_of_Staff_RFB": "rfb_staff",
    "CESMPS_Submitted": "cesmps",
    "OHS_Measures": "ohs",
    "IPC 1": "ipc_1",
    "IPC 2": "ipc_2",
    "IPC 3": "ipc_3",
    "IPC 4": "ipc_4",
    "IPC 5": "ipc_5",
    "IPC 6": "ipc_6",
    "Variance": "variance",
}

# ---------------------------------------------------------------------------
# Composite Site Key  (used for all site-level groupings)
# ---------------------------------------------------------------------------
SITE_KEY = ["package_name", "district", "site_name"]

# ---------------------------------------------------------------------------
# Date Columns to parse (DD/MM/YYYY, dayfirst=True)
# ---------------------------------------------------------------------------
DATE_COLUMNS = [
    "planned_start",
    "planned_finish",
    "actual_start",
    "actual_finish",
    "last_updated",
]

# ---------------------------------------------------------------------------
# IPC Columns
# ---------------------------------------------------------------------------
IPC_COLUMNS = ["ipc_1", "ipc_2", "ipc_3", "ipc_4", "ipc_5", "ipc_6"]

# IPC status priority (higher index = better)
IPC_STATUS_PRIORITY = {
    "Not Submitted": 0,
    "Submitted": 1,
    "In Process": 2,
    "Released": 3,
}

# ---------------------------------------------------------------------------
# Thresholds & Constants
# ---------------------------------------------------------------------------
COMPLETION_THRESHOLD = 95          # site_progress >= this → Completed
LOW_PROGRESS_THRESHOLD = 20        # mobilized + below this → flag
DELAY_BUCKET_CUTOFFS = [0, 30, 60] # On Track / 1-30 / 31-60 / >60
IPC_BLANK_DEFAULT = "Not Submitted"

# ---------------------------------------------------------------------------
# Risk Score Mappings
# ---------------------------------------------------------------------------
DELAY_SCORE_MAP = {
    "On Track": 0,
    "1-30": 25,
    "31-60": 50,
    ">60": 80,
}

PROGRESS_SCORE_BRACKETS = [
    (80, 100, 0),
    (60, 80, 20),
    (40, 60, 40),
    (20, 40, 60),
    (0, 20, 80),
]

MOBILIZATION_PENALTY = 20  # added when mobilized_low_progress

# ---------------------------------------------------------------------------
# Cache Settings
# ---------------------------------------------------------------------------
CACHE_DIR = "data_cache"
CACHE_LATEST_DIR = f"{CACHE_DIR}/latest"
CACHE_SNAPSHOTS_DIR = f"{CACHE_DIR}/snapshots"
INMEMORY_TTL_SECONDS = 3600        # 1 hour
MAX_SNAPSHOT_RETENTION_DAYS = 180
HTTP_TIMEOUT_SECONDS = 30

# ---------------------------------------------------------------------------
# Timezone
# ---------------------------------------------------------------------------
TIMEZONE = "Asia/Karachi"

# ---------------------------------------------------------------------------
# RAG Color Scheme for delay buckets
# ---------------------------------------------------------------------------
RAG_COLORS = {
    "On Track": "#2ecc71",   # Green
    "1-30": "#f39c12",       # Amber
    "31-60": "#e67e22",      # Orange
    ">60": "#e74c3c",        # Red
}

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
REMARKS_TRUNCATE_LENGTH = 100
PHOTO_PLACEHOLDER = "https://via.placeholder.com/300x200?text=No+Photo+Available"
