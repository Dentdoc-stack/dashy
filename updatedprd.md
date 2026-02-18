# PRD — KP-HCIP Multi-Package Executive Dashboard (Replit + Streamlit)

**Version:** v1.3 (Column contract, composite keying, snapshot versioning, architecture updates)  
**Owner:** PMU (KP-HCIP Health Component)  
**Deployment Target:** Replit (optional: develop on GitHub/local first)

### Changelog
- v1.3: Added column contract table (§3.1), column normalization step (§8.0), revised data model keying to `(package_name, district, site_name)`, added snapshot versioning for trends, specified disk cache format (Parquet), clarified photo/compliance/delay_flag disposition, added error handling & performance targets, updated repo structure to native Streamlit multipage layout.
- v1.2: Initial recalculations + tech stack recheck.

---

## 1) Purpose

Build a single, **executive-level dashboard** that consolidates all packages into one view and supports drilldown from:

**Package → District → Site → Discipline → Task**

Data will be loaded from **Google Sheets "Published to web" CSV export links** (read-only).  
The dashboard must be **accurate (no double counting)**, **easy to understand**, and **cost-efficient** (manual refresh + caching; no token/LLM usage).

---

## 2) Scope

### In Scope (MVP)
- Load 10 published CSV sources (one per package) and concatenate into a unified dataset.
- Build a stable **site summary layer** (1 row per site) used for all executive KPIs/charts.
- Provide 4 dashboard pages:
  1) **Situation Room (Executive Summary)**
  2) **Risk & Recovery**
  3) **Package Deep Dive**
  4) **Site Command Center** (tasks + photos + compliance + IPC)
- **Snapshot versioning** for historical trend charts (saved on each manual refresh).

### Out of Scope (MVP)
- Authentication/roles
- Any write-back to Google Sheets
- Auto-refresh / polling
- District-wise compliance reporting for CESMPS/OHS/RFB (must be **package-wise** only)
- IPC penalty in risk score (**explicitly excluded**)
- Any LLM/token usage

---

## 3) Data Sources

### CSV Links (Published Google Sheets)
- Flood Package-1: https://docs.google.com/spreadsheets/d/e/2PACX-1vQUvCNby9_znIiirFF8TFvaxJZOShZBlUpojKTpdEnQHxeyk6OMZxjN21r8dsBZOUNRc_cHFbcql7--/pub?output=csv
- Flood Package-2: https://docs.google.com/spreadsheets/d/e/2PACX-1vQv5GK2QLH1avgzt1ZPVESAFL-lXV5S3QuldW8fsmBYM5fxv6UmLC2Wrww3Pv7lqkBhdKdUZRzWsfeP/pub?output=csv
- Flood Package-3: https://docs.google.com/spreadsheets/d/e/2PACX-1vRuPg-9VWBqev1bs_AZYKqQV6-9C8wlVyo2y6ewjNMxwLuEzm1OXURKZrLDb6O2dTsdpJ9iIYKIlnyo/pub?output=csv
- Flood Package-4: https://docs.google.com/spreadsheets/d/e/2PACX-1vQlUGmqa0SjavAOLnVML_IMAIvnVw5Jtza3z7Tr-norg6yIZYv4GPR6BVGnj7ox7Tshwz6ZrFSxhJTr/pub?output=csv
- Flood Package-5: https://docs.google.com/spreadsheets/d/e/2PACX-1vS8lttkvWeCBNiQwY9N1yuuQqVLuKUi809JkBh9wD15ko31JlqNwvFrHpAMDf3kxrz63-Acul7jM3es/pub?output=csv
- BEmONC New Construction Package-6: https://docs.google.com/spreadsheets/d/e/2PACX-1vTX2fHyqqmdrtemmhVh0pDi3WOH0zOXWk6blv--r9PVzm1Mz0Gr6jqE4IxDI66FC-42FLw4X3ye5hEz/pub?output=csv
- BEmONC Rehab Package-7: https://docs.google.com/spreadsheets/d/e/2PACX-1vRBwi3MLqWQC5SPJsFBS6DHS1SCMlNyxDlVceblbIe3yf4RGYzTueN7T9JKpN1HERVy2qAKKa6ziLvB/pub?output=csv
- BEmONC Prefab Package-8: https://docs.google.com/spreadsheets/d/e/2PACX-1vT8ioVcUUv9VXS48-z6-gWirSNDjDZFx9CW0lhlJqF4W7XFBaRGZXrvtmh9OCnLtQOVjiJ5t9dooMXV/pub?output=csv
- CEmONC Package-9: https://docs.google.com/spreadsheets/d/e/2PACX-1vRg6nKPwYTF4HvWzFnEp4hyqmyt9mMMjbE0LKVQPwWQ_cB5y1F3BhjelizGcvJzVzEvnnHtMv58dvQc/pub?output=csv
- Warehouses Package-10: https://docs.google.com/spreadsheets/d/e/2PACX-1vTrpyYcmR_1-9Apkn0l3O7NQHLcrx2hDe52NDxjO4KwofiAG1EWaKfYJPESyNjb8SjP2fWScshd6zMP/pub?output=csv

### 3.1 Column Contract Table

Every CSV source shares the same schema (30 columns). The table below defines the mapping from raw CSV header to canonical internal name, expected type, example value, and nullability.

| # | Raw CSV Column | Canonical Name | Type | Example | Nullable | Notes |
|---|---|---|---|---|---|---|
| 1 | `package_id` | `package_id` | int | `1` | No | Informational; not used as primary key |
| 2 | `package_name` | `package_name` | str | `Flood Package-1` | No | Part of composite site key |
| 3 | `district` | `district` | str | `Swat` | No | Part of composite site key |
| 4 | `site_id` | `site_id` | str | `FP1-001` | Yes | Informational; may repeat across packages |
| 5 | `site_name` | `site_name` | str | `BHU Kalam` | No | Part of composite site key |
| 6 | `discipline` | `discipline` | str | `Civil` | No | Used in discipline-balanced progress |
| 7 | `task_name` | `task_name` | str | `Foundation Work` | No | Display in Site Command Center |
| 8 | `planned_start` | `planned_start` | date (DD/MM/YYYY) | `01/03/2025` | Yes | Parsed with `dayfirst=True` |
| 9 | `planned_finish` | `planned_finish` | date (DD/MM/YYYY) | `30/06/2025` | Yes | Parsed with `dayfirst=True` |
| 10 | `planned_duration_days` | `planned_duration_days` | int | `122` | Yes | Validation: should ≈ `planned_finish − planned_start` |
| 11 | `actual_start` | `actual_start` | date (DD/MM/YYYY) | `15/03/2025` | Yes | Parsed with `dayfirst=True` |
| 12 | `actual_finish` | `actual_finish` | date (DD/MM/YYYY) | `18/02/2026` | Yes | Parsed with `dayfirst=True` |
| 13 | `progress_pct` | `progress_pct` | float | `45.5` | Yes | Strip `%` if present; clamp to [0, 100] |
| 14 | `Variance` | `variance` | float/int | `-15` | Yes | Retained for validation cross-check; not used in KPIs |
| 15 | `delay_flag_calc` | `delay_flag_calc` | str | `Delayed` | Yes | Retained in df_tasks only; never used in calculations |
| 16 | `last_updated` | `last_updated` | date (DD/MM/YYYY) | `18/02/2026` | Yes | Parsed with `dayfirst=True` |
| 17 | `remarks` | `remarks` | str | `Waiting for materials` | Yes | Display in Site Command Center |
| 18 | `before_photo_share_url` | `before_photo_share_url` | str (URL) | `https://drive.google.com/...` | Yes | Clickable "Open in Drive" link |
| 19 | `before_photo_direct_url` | `before_photo_direct_url` | str (URL) | `https://drive.google.com/uc?...` | Yes | Used for `st.image()` inline display |
| 20 | `after_photo_share_url` | `after_photo_share_url` | str (URL) | `https://drive.google.com/...` | Yes | Clickable "Open in Drive" link |
| 21 | `after_photo_direct_url` | `after_photo_direct_url` | str (URL) | `https://drive.google.com/uc?...` | Yes | Used for `st.image()` inline display |
| 22 | `Mobilization Advance Taken` | `mobilization_taken` | str | `Yes` | Yes | Normalize to Yes/No/Unknown |
| 23 | `No_of_Staff_RFB` | `rfb_staff` | str | `January - No` | Yes | Monthly Yes/No format (name misleading; NOT numeric) |
| 24 | `CESMPS_Submitted` | `cesmps` | str | `Yes` | Yes | Plain Yes/No |
| 25 | `OHS_Measures` | `ohs` | str | `January - No` | Yes | Monthly Yes/No format |
| 26 | `IPC 1` | `ipc_1` | str | `Released` | Yes | Status: Not Submitted / Submitted / In Process / Released |
| 27 | `IPC 2` | `ipc_2` | str | `In Process` | Yes | Same statuses as IPC 1 |
| 28 | `IPC 3` | `ipc_3` | str | `Submitted` | Yes | Same statuses as IPC 1 |
| 29 | `IPC 4` | `ipc_4` | str | `Not Submitted` | Yes | Same statuses as IPC 1 |
| 30 | `IPC 5` | `ipc_5` | str | `Not Submitted` | Yes | Same statuses as IPC 1 |
| 31 | `IPC 6` | `ipc_6` | str | `Not Submitted` | Yes | Same statuses as IPC 1 |

> **Implementation note:** The rename map from raw CSV columns to canonical names must be applied as the **first** cleaning step, before any parsing or transformation (see §8.0).

---

## 4) Users & Success Criteria

### Users
- PMU leadership (executive view)
- Package managers (performance + accountability)
- Monitoring teams (drilldown evidence)

### Success Criteria
- In **≤ 30 seconds**, an executive can answer:
  1) Are we on track?
  2) Which package is worst?
  3) Which districts/sites are driving delay?
  4) Is mobilization translating into progress?
  5) What's the payment/IPC pipeline status (without mixing into risk score)?

---

## 5) Tech Stack

### Runtime / Framework
- **Python 3.11+**
- **Streamlit** (dashboard UI, caching, layout, filters)

### Data & Computation
- **pandas** (CSV loading, cleaning, aggregation)
- **numpy** (bucket logic, numeric handling)
- **python-dateutil** (robust date parsing; pandas also uses it under the hood)
- **pyarrow** (Parquet read/write for disk cache; preserves dtypes)

### Visualization
- **Plotly** (recommended for interactive charts in Streamlit)

### Storage / Caching
- Streamlit cache: `st.cache_data`
- Disk cache: `data_cache/` folder:
  - `data_cache/latest/df_tasks.parquet` — current task-level data
  - `data_cache/latest/df_site.parquet` — current site summary
  - `data_cache/snapshots/{YYYY-MM-DDTHH-MM-SS}.parquet` — historical site summaries (one per refresh)
- Format: **Parquet** (preserves dtypes, compact, fast)

### Why this stack fits your constraint
- No backend/server heavy components
- No tokens/LLM costs
- Fast iterations; easy deployment on Replit
- Works directly with published CSV links

---

## 6) Non-Negotiable Data Rules (Prevents "broken dashboards")

1) **Never compute "site counts" from task rows.**  
   All counts must come from **df_site** (1 row per site).

2) **Delay is computed from dates, not from `delay_flag_calc`.**  
   `delay_flag_calc` is retained in `df_tasks` for reference only; it is never used in calculations or shown on summary pages.

3) **Site progress must be site-level.**  
   Discipline-balanced to avoid task-count bias (see §9.4).

4) **Manual refresh only** + caching to avoid repeated refetch/rebuild.

5) **Compliance reporting (CESMPS/OHS/RFB) is package-wise only** (per your instruction).  
   District exists for drilldown and district contribution, but compliance visuals do not need district breakdown.

6) **IPC is informational only**; **no IPC penalty** in risk score.

7) **Site identity is `(package_name, district, site_name)`** — not `site_id`.  
   `site_id` is retained as an informational column but is never used as a primary key because it may not be globally unique across packages.

---

## 7) Data Model (3 Layers)

### Layer A — `df_tasks` (Raw tasks)
Concatenated raw rows from all CSVs (task-level), after column renaming (§8.0) and cleaning (§8.1–§8.5).

### Layer B — `df_site` (Site summary; 1 row per site)
Keyed by composite:
`(package_name, district, site_name)`

Retains: `package_id`, `site_id` (informational only).

This powers all executive KPIs/charts.

### Layer C — `df_pkg` / `df_dist` (Aggregates)
Derived from `df_site` for package-level and district contribution views.

---

## 8) Cleaning & Normalization

### 8.0 Column Renaming (FIRST STEP)
Before any parsing, apply the rename map from §3.1 to convert all CSV column headers to canonical snake_case names:
Rename map:
"Mobilization Advance Taken" → "mobilization_taken"
"No_of_Staff_RFB" → "rfb_staff"
"CESMPS_Submitted" → "cesmps"
"OHS_Measures" → "ohs"
"IPC 1" → "ipc_1"
"IPC 2" → "ipc_2"
"IPC 3" → "ipc_3"
"IPC 4" → "ipc_4"
"IPC 5" → "ipc_5"
"IPC 6" → "ipc_6"
"Variance" → "variance"

Also: strip leading/trailing whitespace from all column headers before renaming.

### 8.1 Date parsing (CRITICAL)
Your dates are in **DD/MM/YYYY** format (e.g., 18/02/2026).  
Therefore:
- Parse with `dayfirst=True`
- Coerce invalid/blank to NaT

Fields to parse:
- `planned_start`, `planned_finish`
- `actual_start`, `actual_finish`
- `last_updated`

**Validation (post-parse):**
- If `actual_start > actual_finish` → log warning (keep both values)
- If `planned_start > planned_finish` → log warning (keep both values)
- If `planned_duration_days` is available, compare against `(planned_finish − planned_start).days`; log warning if mismatch > 1 day

### 8.2 Status normalization
For Yes/No fields (`mobilization_taken`, `cesmps`):
- Strip whitespace, lower-case, map to: `Yes`, `No`, `Unknown`

### 8.3 Monthly fields (OHS & RFB)
Fields: `ohs`, `rfb_staff`

Format: `"January - No"`  
Split into:
- `<field>_month` (January/February/…)
- `<field>_yesno` (Yes/No/Unknown)

Rules:
- If blank → month = `""`, yesno = `Unknown`
- If malformed (no ` - ` separator) → month = `""`, yesno = `Unknown` (do not crash)

> **Note:** The raw column `No_of_Staff_RFB` has a misleading name — it is NOT numeric. It contains monthly Yes/No strings like `"January - No"`.

### 8.4 CESMPS
`cesmps` is **Yes/No** only (no month).
- Yes → `Yes`
- No → `No`
- blank → `Unknown`

### 8.5 IPC 1–6 normalization
Fields: `ipc_1` through `ipc_6`

Statuses: `Not Submitted`, `Submitted`, `In Process`, `Released`  
Rules:
- Normalize whitespace/case
- Blank → `Not Submitted` (default for pipeline tracking)

### 8.6 Progress percentage
Field: `progress_pct`
- Strip `%` suffix if present
- Cast to float
- Clamp to `[0, 100]`: values > 100 → 100, negative → 0
- Log warnings for out-of-range original values

---

## 9) Calculations & Logic

> All calculations below are the "single source of truth" for the dashboard.  
> **All site-level groupings use the composite key `(package_name, district, site_name)`.**

### 9.1 Task-level delay (date-based)
Let:
- `PF = planned_finish` (parsed datetime)
- `AF = actual_finish` (parsed datetime)
- `TODAY = current date (Asia/Karachi)`

Compute:
- If PF is missing → `task_delay_days = NaN`
- Else:
  - `effective_finish = AF if AF exists else TODAY`
  - `raw_delay = (effective_finish - PF).days`
  - `task_delay_days = max(0, raw_delay)`

**Why max(0):** Dashboard delay should represent "days late", not early completion.

**Optional cross-check:** Compare computed `task_delay_days` against `variance` column. Log divergences above a configurable threshold (e.g., 5 days). Do not use `variance` for any KPI.

### 9.2 Site-level delay
Group by `(package_name, district, site_name)`:  
`site_delay_days = max(task_delay_days across tasks for that site, ignoring NaN)`

### 9.3 Delay buckets
- On Track: `site_delay_days == 0`
- 1–30: `1 <= site_delay_days <= 30`
- 31–60: `31 <= site_delay_days <= 60`
- >60: `site_delay_days > 60`

### 9.4 Site progress (discipline-balanced; recommended)
Because raw data is task-level, use 2-step rollup:

1) For each `(package_name, district, site_name, discipline)`:
   - `discipline_progress = mean(progress_pct)`
2) For each `(package_name, district, site_name)`:
   - `site_progress = mean(discipline_progress across disciplines)`

Fallback (simpler but can bias):  
`site_progress = mean(progress_pct across tasks)`

### 9.5 Site status
Task-level derived status:
- Completed: `progress_pct >= 100` OR `actual_finish` exists
- In Progress: `(0 < progress_pct < 100)` OR `actual_start` exists
- Not Started: `progress_pct == 0` AND `actual_start` missing

Site-level (grouped by `(package_name, district, site_name)`):
- **Inactive:** all tasks Not Started
- **Completed:** `site_progress >= completion_threshold` (default 95)
- **Active:** otherwise

### 9.6 Mobilization flags & score
Group by `(package_name, district, site_name)`:
- `mobilization_taken = "Yes"` if **any** task for the site has `mobilization_taken == "Yes"`, else `"No"`
  - (Uses `any == "Yes"` logic, not `first_non_empty`, to avoid order-dependent results)
- `mobilized_low_progress = (mobilization_taken == "Yes") AND (site_progress < low_progress_threshold)` (default 20)

Mobilization score (used in risk score):
- `mobilization_score = 20 if mobilized_low_progress else 0`

### 9.7 Risk score (NO IPC penalty)
Delay score:
- 0 (On Track)
- 25 (1–30)
- 50 (31–60)
- 80 (>60)

Progress score:
- 0 (>=80%)
- 20 (60–79%)
- 40 (40–59%)
- 60 (20–39%)
- 80 (<20%)

Risk score:
`risk_score = delay_score + progress_score + mobilization_score`

> IPC is not used here.

### 9.8 IPC stage (display only)
Compute per site from `ipc_1`–`ipc_6` using best status priority:
`Released > In Process > Submitted > Not Submitted`

Also compute:
- `no_ipc_released = True if none are Released`

---

## 10) Functional Requirements

### FR1 — Multi-source CSV loader
- Load each CSV URL and concatenate.
- Must fail gracefully per the error handling rules in §13.5.
- Apply column rename map (§8.0) immediately after loading each CSV.

### FR2 — Cost control: caching + manual refresh
- Default behavior:
  - Read from disk cache (`data_cache/latest/*.parquet`) if available
  - Use `st.cache_data` for in-memory caching
- Provide **Refresh Data** button:
  - Refetch all CSVs
  - Overwrite disk cache (`data_cache/latest/`)
  - Save `df_site` snapshot to `data_cache/snapshots/{ISO_timestamp}.parquet`
  - Rebuild df_tasks/df_site once
  - Clean up snapshots older than `max_snapshot_retention_days`

### FR3 — Global hierarchical filters
Filters must cascade:
- **Package** (multi-select)
- **District** (multi-select; depends on selected packages)
- **Site Name** (single select; depends on selected district)

Other filters:
- Delay bucket
- Site status
- Mobilization (Yes/No)

### FR4 — Page 1: Situation Room (Executive Summary)
Must show (from df_site/df_pkg):
- KPI strip:
  - Total sites, Active, Inactive
  - Avg site progress
  - Sites >30 days delayed
  - Sites >60 days delayed
  - Mobilized & <20% progress
  - Sites with no IPC released (informational)
- Visuals:
  1) Package ranking (Avg progress, Critical delays)
  2) Delay distribution (buckets)
  3) District contribution table (within selected packages): avg progress + critical counts + mobilized_low_progress counts
  4) Trend chart (from snapshots):
     - Sites completed over time (based on accumulated snapshots)
     - Avg progress by time period (based on accumulated snapshots)
     - If no snapshots exist yet → show: *"Not enough data for trends — refresh periodically to build history"*
  5) IPC health (stacked bar ipc_1–ipc_6 status)

- Compliance (package-wise only):
  - One compact table: Package vs CESMPS %Yes, OHS %Yes, RFB Staff %Yes

### FR5 — Page 2: Risk & Recovery
- Top critical sites table (sorted by risk score)
- Scatter: site_progress vs site_delay_days (to see clusters)
- One-click "Red List" filter:
  - `site_delay_days > 60` OR `mobilized_low_progress` OR (Inactive AND planned_start passed)

### FR6 — Page 3: Package Deep Dive
- One package focus
- District contribution inside package:
  - avg progress, # >60 delayed, # mobilized_low_progress, # inactive
- Site list table (sortable, exportable)

### FR7 — Page 4: Site Command Center
For selected site:
- Discipline progress bar
- Task table with columns: `discipline`, `task_name`, `progress_pct`, `planned_start`, `planned_finish`, `actual_start`, `actual_finish`, `task_delay_days`, `remarks`
- Remarks: display as expandable text (`st.expander`) if > 100 chars; show "No remarks" when blank
- Photo panel:
  - Before/After images displayed inline using `before_photo_direct_url` / `after_photo_direct_url` via `st.image()`
  - Fallback: if URL is blank or returns 404 → show placeholder with "No photo available"
  - Optional: clickable "Open in Drive" link using `*_share_url`
- Compliance strip (cesmps yes/no, ohs yes/no + month, rfb_staff yes/no + month)
- IPC panel (ipc_1–ipc_6 + computed stage)

### FR8 — Export (optional MVP+)
- Download current filtered df_site (CSV)
- Download "Red List" (CSV)

---

## 11) UI/UX Requirements (Executive Grade)
- Minimal clutter (≤ 8 visuals per page)
- Insight titles (e.g., "Package-4 critical delays highest")
- Consistent RAG logic for delay buckets:
  - Green: On Track
  - Amber: 1–30 days
  - Orange: 31–60 days
  - Red: >60 days
- Drilldown on demand; no task noise on summary pages
- Data quality badge in sidebar: rows loaded, parse warnings count, last refresh timestamp

---

## 12) Configuration (Editable Constants)
- `completion_threshold = 95`
- `low_progress_threshold = 20`
- Delay bucket cutoffs: 0 / 30 / 60
- IPC blank mapping: `Not Submitted` (default)
- Cache settings:
  - in-memory TTL (e.g., 1 hour)
  - disk cache persists until manual refresh
- `max_snapshot_retention_days = 180`
- `variance_cross_check_threshold = 5` (days; for §9.1 optional validation)
- `http_timeout_seconds = 30` (per CSV fetch)

---

## 13) Acceptance Criteria (Definition of Done)

### 13.1 Data correctness
- Total sites shown = unique `(package_name, district, site_name)` from df_site (after filters)
- Site counts never inflate due to task rows
- Delay buckets match date-based delay logic
- Column rename map applied successfully (no raw column names persist past §8.0)

### 13.2 Hierarchical navigation
- Package filter narrows districts/sites correctly
- Selecting a site shows correct tasks and photos

### 13.3 Compliance rule respected
- CESMPS/OHS/RFB visuals are package-wise only

### 13.4 Risk score rule respected
- No IPC penalty in risk score (verified)

### 13.5 Error handling
- If 1–9 CSVs fail: show warning banner listing failed sources, continue with available data
- If all 10 CSVs fail: load from disk cache if available; show error page with "All sources unavailable — showing cached data from {timestamp}" if cache exists, or "No data available — check network and try again" if no cache
- HTTP timeout: 30 seconds per CSV (configurable in §12)
- No automatic retry (manual Refresh handles this)

### 13.6 Cost control works
- Without clicking Refresh, the app does not re-download CSV links
- Filter changes do not trigger refetch; only operate on cached df_site

### 13.7 Snapshot versioning
- Each Refresh creates a new snapshot in `data_cache/snapshots/`
- Snapshots older than `max_snapshot_retention_days` are cleaned up on refresh
- Trend charts correctly read from accumulated snapshots

### 13.8 Performance targets
- From cache: full dashboard renders in < 5 seconds
- From fresh fetch (10 CSVs): completes in < 30 seconds

---

## 14) Repo Structure
app.py # Streamlit entry point, sidebar, global filters, shared state
pages/
1_Situation_Room.py # Executive Summary
2_Risk_Recovery.py # Risk & Recovery
3_Package_Deep_Dive.py # Package Deep Dive
4_Site_Command_Center.py # Site-level drilldown
config.py # CSV links, constants, rename map
loader.py # Fetch + disk cache + refresh + snapshot save
transform.py # Cleaning (§8), df_site build, risk scoring (§9)
charts.py # All Plotly plot functions
requirements.txt # pandas, numpy, streamlit, plotly, pyarrow, python-dateutil
.replit # run = "streamlit run app.py --server.port 8501 --server.address 0.0.0.0"
.gitignore # data_cache/
data_cache/
latest/ # Current df_tasks.parquet, df_site.parquet
snapshots/ # Historical df_site snapshots (one per refresh)

---

## 15) Deliverables
- Streamlit app running on Replit
- Documentation: this PRD + README (how to run, how to refresh, how to add new package links)
- Export CSV of site summary and red list (FR8)
- Snapshot-based trend charts operational after ≥ 2 manual refreshes

---