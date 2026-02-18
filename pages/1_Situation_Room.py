"""
Page 1: Situation Room — Executive Summary
KP-HCIP Multi-Package Executive Dashboard
"""

import streamlit as st
import pandas as pd

from transform import build_package_summary, build_district_summary
from charts import (
    chart_package_ranking,
    chart_delay_distribution,
    chart_ipc_health,
    chart_trend_progress,
    chart_trend_completed,
)
from loader import load_all_snapshots

st.title("📊 Situation Room — Executive Summary")

# ---------------------------------------------------------------------------
# Guard: data loaded?
# ---------------------------------------------------------------------------
if not st.session_state.get("data_loaded", False):
    st.warning("No data loaded. Go to the main page and click **Refresh Data**.")
    st.stop()

df_site = st.session_state["df_site_filtered"]

if df_site.empty:
    st.info("No sites match the current filters.")
    st.stop()

# ---------------------------------------------------------------------------
# KPI Strip
# ---------------------------------------------------------------------------
st.markdown("### Key Performance Indicators")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sites", len(df_site))
c2.metric("Active", int((df_site["site_status"] == "Active").sum()))
c3.metric("Inactive", int((df_site["site_status"] == "Inactive").sum()))
c4.metric("Completed", int((df_site["site_status"] == "Completed").sum()))

c5, c6, c7, c8 = st.columns(4)
avg_prog = df_site["site_progress"].mean()
c5.metric("Avg Progress", f"{avg_prog:.1f}%")
c6.metric(">30 Days Delayed", int((df_site["site_delay_days"] > 30).sum()))
c7.metric(">60 Days Delayed", int((df_site["site_delay_days"] > 60).sum()))
c8.metric(
    "Mobilized & Low Progress",
    int(df_site["mobilized_low_progress"].sum()),
)

col_extra1, col_extra2 = st.columns(2)
if "no_ipc_released" in df_site.columns:
    col_extra1.metric(
        "No IPC Released (info)",
        int(df_site["no_ipc_released"].sum()),
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Visuals row 1: Package ranking + Delay distribution
# ---------------------------------------------------------------------------
df_pkg = build_package_summary(df_site)

col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(chart_package_ranking(df_pkg), width="stretch")
with col_b:
    st.plotly_chart(chart_delay_distribution(df_site), width="stretch")

st.markdown("---")

# ---------------------------------------------------------------------------
# District contribution table
# ---------------------------------------------------------------------------
st.markdown("### District Contribution")
df_dist = build_district_summary(df_site)

if not df_dist.empty:
    display_dist = df_dist.rename(columns={
        "package_name": "Package",
        "district": "District",
        "total_sites": "Sites",
        "avg_progress": "Avg Progress (%)",
        "sites_gt60_delayed": ">60 Day Delayed",
        "mobilized_low_progress_count": "Mob + Low Progress",
        "inactive_sites": "Inactive",
    })
    st.dataframe(
        display_dist,
        width="stretch",
        hide_index=True,
        height=min(400, 35 * len(display_dist) + 40),
    )
else:
    st.info("No district data available.")

st.markdown("---")

# ---------------------------------------------------------------------------
# Trend charts (from snapshots)
# ---------------------------------------------------------------------------
st.markdown("### Trends")

df_snapshots = load_all_snapshots()
if df_snapshots.empty:
    st.info("📈 Not enough data for trends — refresh periodically to build history.")
else:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        fig = chart_trend_progress(df_snapshots)
        if fig:
            st.plotly_chart(fig, width="stretch")
    with col_t2:
        fig = chart_trend_completed(df_snapshots)
        if fig:
            st.plotly_chart(fig, width="stretch")

st.markdown("---")

# ---------------------------------------------------------------------------
# IPC Health
# ---------------------------------------------------------------------------
st.markdown("### IPC Health")
st.plotly_chart(chart_ipc_health(df_site), width="stretch")

st.markdown("---")

# ---------------------------------------------------------------------------
# Compliance Table (package-wise)
# ---------------------------------------------------------------------------
st.markdown("### Compliance Overview (Package-wise)")

if not df_pkg.empty:
    comp_cols = ["package_name"]
    rename_map = {"package_name": "Package"}
    if "cesmps_pct_yes" in df_pkg.columns:
        comp_cols.append("cesmps_pct_yes")
        rename_map["cesmps_pct_yes"] = "CESMPS % Yes"
    if "ohs_pct_yes" in df_pkg.columns:
        comp_cols.append("ohs_pct_yes")
        rename_map["ohs_pct_yes"] = "OHS % Yes"
    if "rfb_pct_yes" in df_pkg.columns:
        comp_cols.append("rfb_pct_yes")
        rename_map["rfb_pct_yes"] = "RFB Staff % Yes"

    if len(comp_cols) > 1:
        st.dataframe(
            df_pkg[comp_cols].rename(columns=rename_map),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No compliance data available.")
else:
    st.info("No package data available.")
