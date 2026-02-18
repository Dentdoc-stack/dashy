"""
Page 3: Package Deep Dive
KP-HCIP Multi-Package Executive Dashboard
"""

import streamlit as st
import pandas as pd

from transform import build_district_summary
from charts import chart_district_contribution

st.title("📦 Package Deep Dive")

# ---------------------------------------------------------------------------
# Guard
# ---------------------------------------------------------------------------
if not st.session_state.get("data_loaded", False):
    st.warning("No data loaded. Go to the main page and click **Refresh Data**.")
    st.stop()

df_site = st.session_state["df_site_filtered"]

if df_site.empty:
    st.info("No sites match the current filters.")
    st.stop()

# ---------------------------------------------------------------------------
# Package selector
# ---------------------------------------------------------------------------
packages = sorted(df_site["package_name"].dropna().unique())

if not packages:
    st.info("No packages available.")
    st.stop()

selected_pkg = st.selectbox("Select Package", options=packages, key="deep_dive_pkg")

pkg_data = df_site[df_site["package_name"] == selected_pkg]

if pkg_data.empty:
    st.info(f"No sites found for {selected_pkg}.")
    st.stop()

# ---------------------------------------------------------------------------
# Package KPIs
# ---------------------------------------------------------------------------
st.markdown(f"### {selected_pkg} — Overview")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Sites", len(pkg_data))
c2.metric("Avg Progress", f"{pkg_data['site_progress'].mean():.1f}%")
c3.metric("Active", int((pkg_data["site_status"] == "Active").sum()))
c4.metric("Inactive", int((pkg_data["site_status"] == "Inactive").sum()))
c5.metric("Completed", int((pkg_data["site_status"] == "Completed").sum()))

c6, c7, c8 = st.columns(3)
c6.metric(">60 Days Delayed", int((pkg_data["site_delay_days"] > 60).sum()))
c7.metric("Mob + Low Progress", int(pkg_data["mobilized_low_progress"].sum()))
if "no_ipc_released" in pkg_data.columns:
    c8.metric("No IPC Released", int(pkg_data["no_ipc_released"].sum()))

st.markdown("---")

# ---------------------------------------------------------------------------
# District contribution
# ---------------------------------------------------------------------------
st.markdown("### District Contribution")

df_dist = build_district_summary(pkg_data)

if not df_dist.empty:
    col_chart, col_table = st.columns([1, 1])

    with col_chart:
        st.plotly_chart(
            chart_district_contribution(df_dist),
            width="stretch",
        )

    with col_table:
        display_dist = df_dist.rename(columns={
            "package_name": "Package",
            "district": "District",
            "total_sites": "Sites",
            "avg_progress": "Avg Progress (%)",
            "sites_gt60_delayed": ">60 Delayed",
            "mobilized_low_progress_count": "Mob+Low Prog",
            "inactive_sites": "Inactive",
        })
        st.dataframe(
            display_dist,
            width="stretch",
            hide_index=True,
        )
else:
    st.info("No district data for this package.")

st.markdown("---")

# ---------------------------------------------------------------------------
# Site list table (sortable, exportable)
# ---------------------------------------------------------------------------
st.markdown("### Site List")

display_cols = [
    "district", "site_name", "site_progress", "site_delay_days",
    "delay_bucket", "site_status", "mobilization_taken",
    "mobilized_low_progress", "risk_score",
]
display_cols = [c for c in display_cols if c in pkg_data.columns]

st.dataframe(
    pkg_data[display_cols].rename(columns={
        "district": "District",
        "site_name": "Site",
        "site_progress": "Progress (%)",
        "site_delay_days": "Delay (days)",
        "delay_bucket": "Delay Bucket",
        "site_status": "Status",
        "mobilization_taken": "Mobilized",
        "mobilized_low_progress": "Mob+Low Prog",
        "risk_score": "Risk Score",
    }).sort_values("Risk Score", ascending=False),
    width="stretch",
    hide_index=True,
    height=min(600, 35 * len(pkg_data) + 40),
)

# Export
csv_pkg = pkg_data.to_csv(index=False)
st.download_button(
    f"📥 Download {selected_pkg} Sites (CSV)",
    data=csv_pkg,
    file_name=f"{selected_pkg.replace(' ', '_')}_sites.csv",
    mime="text/csv",
)
