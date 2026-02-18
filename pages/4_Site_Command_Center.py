"""
Page 4: Site Command Center
KP-HCIP Multi-Package Executive Dashboard
"""

import streamlit as st
import pandas as pd

from config import SITE_KEY, IPC_COLUMNS, REMARKS_TRUNCATE_LENGTH, PHOTO_PLACEHOLDER
from charts import chart_discipline_progress

st.title("🏗️ Site Command Center")

# ---------------------------------------------------------------------------
# Guard
# ---------------------------------------------------------------------------
if not st.session_state.get("data_loaded", False):
    st.warning("No data loaded. Go to the main page and click **Refresh Data**.")
    st.stop()

df_tasks = st.session_state["df_tasks"]
df_site = st.session_state["df_site_filtered"]

if df_site.empty:
    st.info("No sites match the current filters.")
    st.stop()

# ---------------------------------------------------------------------------
# Site selector (cascaded)
# ---------------------------------------------------------------------------
col_sel1, col_sel2, col_sel3 = st.columns(3)

packages = sorted(df_site["package_name"].dropna().unique())
with col_sel1:
    sel_pkg = st.selectbox("Package", options=packages, key="scc_pkg")

districts = sorted(df_site.loc[df_site["package_name"] == sel_pkg, "district"].dropna().unique())
with col_sel2:
    sel_dist = st.selectbox("District", options=districts, key="scc_dist")

sites = sorted(
    df_site.loc[
        (df_site["package_name"] == sel_pkg) &
        (df_site["district"] == sel_dist),
        "site_name"
    ].dropna().unique()
)
with col_sel3:
    sel_site = st.selectbox("Site", options=sites, key="scc_site")

# ---------------------------------------------------------------------------
# Get site data
# ---------------------------------------------------------------------------
site_mask = (
    (df_site["package_name"] == sel_pkg) &
    (df_site["district"] == sel_dist) &
    (df_site["site_name"] == sel_site)
)
site_row = df_site[site_mask]

if site_row.empty:
    st.info("No data for selected site.")
    st.stop()

site_info = site_row.iloc[0]

# Tasks for this site
task_mask = (
    (df_tasks["package_name"] == sel_pkg) &
    (df_tasks["district"] == sel_dist) &
    (df_tasks["site_name"] == sel_site)
)
site_tasks = df_tasks[task_mask]

# ---------------------------------------------------------------------------
# Site KPI strip
# ---------------------------------------------------------------------------
st.markdown(f"### {sel_site} — {sel_dist} ({sel_pkg})")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Progress", f"{site_info.get('site_progress', 0):.1f}%")
c2.metric("Delay (days)", int(site_info.get("site_delay_days", 0)))
c3.metric("Status", site_info.get("site_status", "Unknown"))
c4.metric("Delay Bucket", site_info.get("delay_bucket", "N/A"))
c5.metric("Risk Score", int(site_info.get("risk_score", 0)))

st.markdown("---")

# ---------------------------------------------------------------------------
# Discipline Progress Bar
# ---------------------------------------------------------------------------
st.markdown("### Discipline Progress")
if not site_tasks.empty:
    st.plotly_chart(
        chart_discipline_progress(site_tasks),
        width="stretch",
    )
else:
    st.info("No tasks for this site.")

st.markdown("---")

# ---------------------------------------------------------------------------
# Task Table
# ---------------------------------------------------------------------------
st.markdown("### Task Details")

if not site_tasks.empty:
    task_display_cols = [
        "discipline", "task_name", "progress_pct",
        "planned_start", "planned_finish",
        "actual_start", "actual_finish",
        "task_delay_days", "remarks",
    ]
    task_display_cols = [c for c in task_display_cols if c in site_tasks.columns]

    st.dataframe(
        site_tasks[task_display_cols].rename(columns={
            "discipline": "Discipline",
            "task_name": "Task",
            "progress_pct": "Progress (%)",
            "planned_start": "Planned Start",
            "planned_finish": "Planned Finish",
            "actual_start": "Actual Start",
            "actual_finish": "Actual Finish",
            "task_delay_days": "Delay (days)",
            "remarks": "Remarks",
        }),
        width="stretch",
        hide_index=True,
    )
else:
    st.info("No task data for this site.")

st.markdown("---")

# ---------------------------------------------------------------------------
# Remarks
# ---------------------------------------------------------------------------
st.markdown("### Remarks")
if not site_tasks.empty and "remarks" in site_tasks.columns:
    remarks_list = site_tasks["remarks"].dropna().unique()
    if len(remarks_list) > 0:
        for i, remark in enumerate(remarks_list):
            remark_str = str(remark).strip()
            if remark_str and remark_str.lower() != "nan":
                if len(remark_str) > REMARKS_TRUNCATE_LENGTH:
                    with st.expander(f"Remark {i+1}: {remark_str[:80]}..."):
                        st.write(remark_str)
                else:
                    st.write(f"- {remark_str}")
    else:
        st.caption("No remarks available.")
else:
    st.caption("No remarks available.")

st.markdown("---")

# ---------------------------------------------------------------------------
# Photo Panel
# ---------------------------------------------------------------------------
st.markdown("### Photos")

col_before, col_after = st.columns(2)

with col_before:
    st.markdown("**Before**")
    if not site_tasks.empty and "before_photo_direct_url" in site_tasks.columns:
        urls = site_tasks["before_photo_direct_url"].dropna().unique()
        if len(urls) > 0:
            for url in urls[:4]:  # Show max 4 photos
                url_str = str(url).strip()
                if url_str and url_str.lower() != "nan":
                    try:
                        st.image(url_str, use_container_width=True)
                    except Exception:
                        st.caption("⚠️ Photo could not be loaded")
                    # Share URL link
                    if "before_photo_share_url" in site_tasks.columns:
                        share_urls = site_tasks.loc[
                            site_tasks["before_photo_direct_url"] == url,
                            "before_photo_share_url"
                        ].dropna()
                        if not share_urls.empty:
                            st.markdown(f"[Open in Drive]({share_urls.iloc[0]})")
        else:
            st.caption("No before photos available.")
    else:
        st.caption("No before photos available.")

with col_after:
    st.markdown("**After**")
    if not site_tasks.empty and "after_photo_direct_url" in site_tasks.columns:
        urls = site_tasks["after_photo_direct_url"].dropna().unique()
        if len(urls) > 0:
            for url in urls[:4]:
                url_str = str(url).strip()
                if url_str and url_str.lower() != "nan":
                    try:
                        st.image(url_str, use_container_width=True)
                    except Exception:
                        st.caption("⚠️ Photo could not be loaded")
                    if "after_photo_share_url" in site_tasks.columns:
                        share_urls = site_tasks.loc[
                            site_tasks["after_photo_direct_url"] == url,
                            "after_photo_share_url"
                        ].dropna()
                        if not share_urls.empty:
                            st.markdown(f"[Open in Drive]({share_urls.iloc[0]})")
        else:
            st.caption("No after photos available.")
    else:
        st.caption("No after photos available.")

st.markdown("---")

# ---------------------------------------------------------------------------
# Compliance Strip
# ---------------------------------------------------------------------------
st.markdown("### Compliance")

comp_c1, comp_c2, comp_c3 = st.columns(3)

with comp_c1:
    cesmps_val = site_info.get("cesmps", "Unknown")
    color = "🟢" if cesmps_val == "Yes" else ("🔴" if cesmps_val == "No" else "⚪")
    st.markdown(f"**CESMPS:** {color} {cesmps_val}")

with comp_c2:
    ohs_yn = site_info.get("ohs_yesno", "Unknown")
    ohs_mo = site_info.get("ohs_month", "")
    color = "🟢" if ohs_yn == "Yes" else ("🔴" if ohs_yn == "No" else "⚪")
    st.markdown(f"**OHS:** {color} {ohs_yn}" + (f" ({ohs_mo})" if ohs_mo else ""))

with comp_c3:
    rfb_yn = site_info.get("rfb_staff_yesno", "Unknown")
    rfb_mo = site_info.get("rfb_staff_month", "")
    color = "🟢" if rfb_yn == "Yes" else ("🔴" if rfb_yn == "No" else "⚪")
    st.markdown(f"**RFB Staff:** {color} {rfb_yn}" + (f" ({rfb_mo})" if rfb_mo else ""))

st.markdown("---")

# ---------------------------------------------------------------------------
# IPC Panel
# ---------------------------------------------------------------------------
st.markdown("### IPC Status")

ipc_cols_present = [c for c in IPC_COLUMNS if c in site_info.index]

if ipc_cols_present:
    ipc_cols_display = st.columns(len(ipc_cols_present))
    for i, col in enumerate(ipc_cols_present):
        val = site_info.get(col, "Not Submitted")
        icon_map = {
            "Not Submitted": "🔴",
            "Submitted": "🟡",
            "In Process": "🔵",
            "Released": "🟢",
        }
        icon = icon_map.get(val, "⚪")
        ipc_cols_display[i].markdown(
            f"**{col.upper().replace('_', ' ')}**\n\n{icon} {val}"
        )

    st.markdown(f"**Best IPC Stage:** {site_info.get('ipc_best_stage', 'N/A')}")
else:
    st.caption("No IPC data available.")
