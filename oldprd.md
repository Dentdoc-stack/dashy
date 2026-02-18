# PRD — KP-HCIP Multi-Package Executive Dashboard (Replit + Streamlit)

**Version:** v1.2 (Markdown, recalculations + tech stack rechecked)  
**Owner:** PMU (KP-HCIP Health Component)  
**Deployment Target:** Replit (optional: develop on GitHub/local first)

---

## 1) Purpose

Build a single, **executive-level dashboard** that consolidates all packages into one view and supports drilldown from:

**Package → District → Site → Discipline → Task**

Data will be loaded from **Google Sheets “Published to web” CSV export links** (read-only).  
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
  5) What’s the payment/IPC pipeline status (without mixing into risk score)?

---

## 5) Tech Stack (Rechecked)

### Runtime / Framework
- **Python 3.11+**
- **Streamlit** (dashboard UI, caching, layout, filters)

### Data & Computation
- **pandas** (CSV loading, cleaning, aggregation)
- **numpy** (bucket logic, numeric handling)
- **python-dateutil** (robust date parsing; pandas also uses it under the hood)

### Visualization (choose one)
- **Plotly** (recommended for interactive charts in Streamlit)  
  OR
- Streamlit native `st.bar_chart` / `st.line_chart` (lighter, less control)

### Storage / Caching
- Streamlit cache: `st.cache_data`
- Disk cache: local folder `data_cache/` for persisted CSV snapshots between reruns

### Why this stack fits your constraint
- No backend/server heavy components
- No tokens/LLM costs
- Fast iterations; easy deployment on Replit
- Works directly with published CSV links

---

## 6) Non-Negotiable Data Rules (Prevents “broken dashboards”)

1) **Never compute “site counts” from task rows.**  
   All counts must come from **df_site** (1 row per site).

2) **Delay is computed from dates, not from `delay_flag_calc`.**  
   Text flags may be inconsistent.

3) **Site progress must be site-level.**  
   Recommended: discipline-balanced to avoid task-count bias.

4) **Manual refresh only** + caching to avoid repeated refetch/rebuild.

5) **Compliance reporting (CESMPS/OHS/RFB) is package-wise only** (per your instruction).  
   District exists for drilldown and district contribution, but compliance visuals do not need district breakdown.

6) **IPC is informational only**; **no IPC penalty** in risk score.

---

## 7) Data Model (3 Layers)

### Layer A — `df_tasks` (Raw tasks)
Concatenated raw rows from all CSVs (task-level).

### Layer B — `df_site` (Site summary; 1 row per site)
Keyed by:
`package_id, package_name, district, site_id, site_name`

This powers all executive KPIs/charts.

### Layer C — `df_pkg` / `df_dist` (Aggregates)
Derived from df_site for package-level and district contribution views.

---

## 8) Cleaning & Normalization (Rechecked with your real formats)

### 8.1 Date parsing (CRITICAL)
Your dates are in **DD/MM/YYYY** format (e.g., 18/02/2026).  
Therefore:
- Parse with `dayfirst=True`
- Coerce invalid/blank to NaT

Fields to parse:
- planned_start, planned_finish
- actual_start, actual_finish
- last_updated

### 8.2 Status normalization
For Yes/No fields:
- Strip whitespace, lower-case, map to: `Yes`, `No`, `Unknown`

### 8.3 Monthly fields (OHS & RFB)
Format: `"January - No"`  
Split into:
- `<field>_month` (January/February/…)
- `<field>_yesno` (Yes/No/Unknown)

Rules:
- If blank → month = "", yesno = Unknown
- If malformed → month = "", yesno = Unknown (do not crash)

### 8.4 CESMPS
You confirmed CESMPS is only **Yes/No** (no month).
- Yes → Yes
- No → No
- blank → Unknown

### 8.5 IPC 1–6 normalization
Statuses: `Not Submitted`, `Submitted`, `In Process`, `Released`  
Rules:
- Normalize whitespace/case
- Blank: configurable:
  - Default: `Not Submitted` (common for pipeline tracking)
  - Optional safer mode: `Unknown` (if blanks may mean N/A)

---

## 9) Calculations & Logic (Rechecked)

> All calculations below are the “single source of truth” for the dashboard.

### 9.1 Task-level delay (date-based)
Let:
- `PF = planned_finish_dt`
- `AF = actual_finish_dt`
- `TODAY = current date (Asia/Karachi)`

Compute:
- If PF is missing → `task_delay_days = NaN`
- Else:
  - `effective_finish = AF if AF exists else TODAY`
  - `raw_delay = (effective_finish - PF).days`
  - `task_delay_days = max(0, raw_delay)`

**Why max(0):** Dashboard delay should represent “days late”, not early completion.  
(If you want to also show early completion, keep a separate `task_slip_days_signed`.)

### 9.2 Site-level delay
`site_delay_days = max(task_delay_days across tasks for that site, ignoring NaN)`

### 9.3 Delay buckets
- On Track: `site_delay_days == 0`
- 1–30: `1 <= site_delay_days <= 30`
- 31–60: `31 <= site_delay_days <= 60`
- >60: `site_delay_days > 60`

### 9.4 Site progress (discipline-balanced; recommended)
Because raw is task-level, use 2-step rollup:

1) For each `(site_id, discipline)`:
   - `discipline_progress = mean(progress_pct)`
2) For each `site_id`:
   - `site_progress = mean(discipline_progress across disciplines)`

Fallback (simpler but can bias):  
`site_progress = mean(progress_pct across tasks)`

### 9.5 Site status
Task-level derived status:
- Completed: `progress_pct >= 100` OR actual_finish exists
- In Progress: `(0 < progress_pct < 100)` OR actual_start exists
- Not Started: `progress_pct == 0` AND actual_start missing

Site-level:
- **Inactive:** all tasks Not Started
- **Completed:** `site_progress >= completion_threshold` (default 95)
- **Active:** otherwise

### 9.6 Mobilization flags & score (rechecked)
- `mobilization_taken = first_non_empty("Mobilization Advance Taken")` per site; normalize to Yes/No/Unknown
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
Compute per site from IPC1–IPC6 using best status priority:
`Released > In Process > Submitted > Not Submitted`

Also compute:
- `no_ipc_released = True if none are Released`

---

## 10) Functional Requirements

### FR1 — Multi-source CSV loader
- Load each CSV URL and concatenate.
- Must fail gracefully if one source is temporarily unavailable (show warning; continue).

### FR2 — Cost control: caching + manual refresh
- Default behavior:
  - Read from disk cache if available
  - Use `st.cache_data` for in-memory caching
- Provide **Refresh Data** button:
  - Refetch all CSVs
  - Overwrite disk cache
  - Rebuild df_tasks/df_site once

### FR3 — Global hierarchical filters
Filters must cascade:
- Package (multi-select)
- District (multi-select; depends on selected packages)
- Site (single select; depends on selected district)

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
  4) Trend (one of):
     - Sites completed over time (based on last_updated snapshots)
     - Avg progress by month (based on last_updated)
  5) IPC health (stacked bar IPC1–IPC6 status)

- Compliance (package-wise only):
  - One compact table: Package vs CESMPS%Yes, OHS%Yes, RFB Staff%Yes

### FR5 — Page 2: Risk & Recovery
- Top critical sites table (sorted by risk score)
- Scatter: site_progress vs site_delay_days (to see clusters)
- One-click “Red List” filter:
  - `site_delay_days > 60` OR `mobilized_low_progress` OR (Inactive AND planned_start passed)

### FR6 — Page 3: Package Deep Dive
- One package focus
- District contribution inside package:
  - avg progress, # >60 delayed, # mobilized_low_progress, # inactive
- Site list table (sortable, exportable)

### FR7 — Page 4: Site Command Center
For selected site:
- discipline progress bar
- task table (df_tasks filtered)
- remarks
- photo panel (before/after URLs)
- compliance strip (CESMPS yes/no, OHS yes/no + month, RFB yes/no + month)
- IPC panel (IPC1–IPC6 + stage)

### FR8 — Export (optional MVP+)
- Download current filtered df_site (CSV)
- Download “Red List” (CSV)

---

## 11) UI/UX Requirements (Executive Grade)
- Minimal clutter (≤ 8 visuals per page)
- Insight titles (e.g., “Package-4 critical delays highest”)
- Consistent RAG logic for delay buckets
- Drilldown on demand; no task noise on summary pages

---

## 12) Configuration (Editable Constants)
- `completion_threshold = 95`
- `low_progress_threshold = 20`
- Delay bucket cutoffs: 0 / 30 / 60
- IPC blank mapping: Not Submitted vs Unknown
- Cache settings:
  - in-memory TTL (e.g., 1 hour)
  - disk cache persists until manual refresh

---

## 13) Acceptance Criteria (Definition of Done)

### Data correctness
- Total sites shown = unique site_id from df_site (after filters)
- Site counts never inflate due to task rows
- Delay buckets match date-based delay logic

### Hierarchical navigation
- Package filter narrows districts/sites correctly
- Selecting a site shows correct tasks and photos

### Compliance rule respected
- CESMPS/OHS/RFB visuals are package-wise only

### Risk score rule respected
- No IPC penalty in risk score (verified)

### Cost control works
- Without clicking Refresh, the app does not re-download CSV links
- Filter changes do not trigger refetch; only operate on cached df_site

---

## 14) Suggested Repo Structure
- `app.py` (Streamlit pages + routing)
- `config.py` (CSV links, constants)
- `loader.py` (fetch + disk cache + refresh)
- `transform.py` (cleaning, df_site build, risk scoring)
- `charts.py` (all plots)
- `requirements.txt`
- `.gitignore` (ignore `data_cache/`)

---

## 15) Deliverables
- Streamlit app running on Replit
- Documentation: this PRD + README (how to run, how to refresh, how to add new package links)
- Optional: Export CSV of site summary and red list

---
