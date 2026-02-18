"""
Page 2: Risk & Recovery
KP-HCIP Multi-Package Executive Dashboard
"""

import streamlit as st
import pandas as pd

from charts import chart_risk_scatter
from transform import _get_today

st.title("⚠️ Risk & Recovery")

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
# Red List filter toggle
# ---------------------------------------------------------------------------
st.markdown("### Red List Filter")
today = _get_today()

red_list_mask = (
    (df_site["site_delay_days"] > 60) |
    (df_site["mobilized_low_progress"]) |
    (
        (df_site["site_status"] == "Inactive") &
        (df_site["earliest_planned_start"].notna()) &
        (df_site["earliest_planned_start"] < today)
    )
)

show_red_list = st.toggle("Show Red List Only", value=False)

if show_red_list:
    display_df = df_site[red_list_mask].copy()
    st.caption(f"🔴 Showing **{len(display_df)}** red-flag sites")
else:
    display_df = df_site.copy()

# ---------------------------------------------------------------------------
# Top Critical Sites Table
# ---------------------------------------------------------------------------
st.markdown("### Top Critical Sites")

top_critical = display_df.sort_values("risk_score", ascending=False).head(50)

display_cols = [
    "package_name", "district", "site_name",
    "site_progress", "site_delay_days", "delay_bucket",
    "mobilization_taken", "mobilized_low_progress",
    "risk_score", "site_status",
]
display_cols = [c for c in display_cols if c in top_critical.columns]

st.dataframe(
    top_critical[display_cols].rename(columns={
        "package_name": "Package",
        "district": "District",
        "site_name": "Site",
        "site_progress": "Progress (%)",
        "site_delay_days": "Delay (days)",
        "delay_bucket": "Delay Bucket",
        "mobilization_taken": "Mobilized",
        "mobilized_low_progress": "Mob+Low Prog",
        "risk_score": "Risk Score",
        "site_status": "Status",
    }),
    width="stretch",
    hide_index=True,
    height=min(600, 35 * len(top_critical) + 40),
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Risk Scatter
# ---------------------------------------------------------------------------
st.markdown("### Risk Landscape")
st.plotly_chart(chart_risk_scatter(display_df), width="stretch")

st.markdown("---")

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
st.markdown("### Export")

col_e1, col_e2 = st.columns(2)

with col_e1:
    csv_filtered = display_df.to_csv(index=False)
    st.download_button(
        "📥 Download Filtered Sites (CSV)",
        data=csv_filtered,
        file_name="filtered_sites.csv",
        mime="text/csv",
    )

with col_e2:
    red_list_df = df_site[red_list_mask]
    if not red_list_df.empty:
        csv_red = red_list_df.to_csv(index=False)
        st.download_button(
            "📥 Download Red List (CSV)",
            data=csv_red,
            file_name="red_list.csv",
            mime="text/csv",
        )
    else:
        st.caption("No red-list sites to export.")
