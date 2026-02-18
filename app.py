"""
app.py — Streamlit entry point: sidebar, global filters, shared state, page routing.
KP-HCIP Multi-Package Executive Dashboard
"""

import streamlit as st
import pandas as pd

from config import SITE_KEY
from loader import get_data, get_cache_timestamp

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="KP-HCIP Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for executive look
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 10px 16px;
        border-left: 4px solid #3498db;
    }
    [data-testid="stMetric"] label { font-size: 0.8rem; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar — Data Controls
# ---------------------------------------------------------------------------
st.sidebar.title("🏥 KP-HCIP Dashboard")
st.sidebar.markdown("---")

# Refresh button
if st.sidebar.button("🔄 Refresh Data", type="primary", use_container_width=True):
    get_data.clear()
    df_tasks, df_site, warnings = get_data(force_refresh=True)
    st.sidebar.success("Data refreshed!")
else:
    df_tasks, df_site, warnings = get_data(force_refresh=False)

# Show warnings
for w in warnings:
    if "Failed" in w or "unavailable" in w:
        st.sidebar.warning(w)
    else:
        st.sidebar.info(w)

# Data quality badge
cache_ts = get_cache_timestamp()
st.sidebar.markdown("---")
st.sidebar.caption(f"📊 **Rows:** {len(df_tasks):,} tasks | {len(df_site):,} sites")
if cache_ts:
    st.sidebar.caption(f"🕐 **Last refresh:** {cache_ts}")

# ---------------------------------------------------------------------------
# Sidebar — Global Filters (FR3)
# ---------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

if not df_site.empty:
    # Package filter
    all_packages = sorted(df_site["package_name"].dropna().unique())
    selected_packages = st.sidebar.multiselect(
        "Package",
        options=all_packages,
        default=all_packages,
        key="filter_package",
    )

    # Cascade: District
    mask_pkg = df_site["package_name"].isin(selected_packages) if selected_packages else pd.Series(True, index=df_site.index)
    available_districts = sorted(df_site.loc[mask_pkg, "district"].dropna().unique())
    selected_districts = st.sidebar.multiselect(
        "District",
        options=available_districts,
        default=available_districts,
        key="filter_district",
    )

    # Cascade: Site Name (single select — optional)
    mask_dist = mask_pkg & df_site["district"].isin(selected_districts)
    available_sites = sorted(df_site.loc[mask_dist, "site_name"].dropna().unique())

    selected_site = st.sidebar.selectbox(
        "Site (optional — for Site Command Center)",
        options=["All"] + available_sites,
        index=0,
        key="filter_site",
    )

    # Other filters
    st.sidebar.markdown("---")
    delay_buckets_all = ["On Track", "1-30", "31-60", ">60"]
    selected_delay_buckets = st.sidebar.multiselect(
        "Delay Bucket",
        options=delay_buckets_all,
        default=delay_buckets_all,
        key="filter_delay",
    )

    status_all = ["Active", "Inactive", "Completed"]
    selected_statuses = st.sidebar.multiselect(
        "Site Status",
        options=status_all,
        default=status_all,
        key="filter_status",
    )

    mob_options = ["Yes", "No"]
    selected_mob = st.sidebar.multiselect(
        "Mobilization Taken",
        options=mob_options,
        default=mob_options,
        key="filter_mob",
    )

    # ---------------------------------------------------------------------------
    # Apply filters → store in session_state
    # ---------------------------------------------------------------------------
    filtered = df_site.copy()
    if selected_packages:
        filtered = filtered[filtered["package_name"].isin(selected_packages)]
    if selected_districts:
        filtered = filtered[filtered["district"].isin(selected_districts)]
    if selected_delay_buckets:
        filtered = filtered[filtered["delay_bucket"].isin(selected_delay_buckets)]
    if selected_statuses:
        filtered = filtered[filtered["site_status"].isin(selected_statuses)]
    if selected_mob:
        filtered = filtered[filtered["mobilization_taken"].isin(selected_mob)]

    st.session_state["df_tasks"] = df_tasks
    st.session_state["df_site"] = df_site
    st.session_state["df_site_filtered"] = filtered
    st.session_state["selected_packages"] = selected_packages
    st.session_state["selected_districts"] = selected_districts
    st.session_state["selected_site"] = selected_site
    st.session_state["data_loaded"] = True

else:
    st.session_state["data_loaded"] = False

# ---------------------------------------------------------------------------
# Main area — Landing / Navigation hint
# ---------------------------------------------------------------------------
if not st.session_state.get("data_loaded", False):
    st.error("No data available. Click **Refresh Data** in the sidebar to load.")
    st.stop()

st.title("KP-HCIP Multi-Package Executive Dashboard")
st.info("👈 Use the sidebar to filter data. Navigate to pages using the sidebar menu.")

# Quick overview KPI strip on home page
df_f = st.session_state["df_site_filtered"]

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Sites", len(df_f))
c2.metric("Active", (df_f["site_status"] == "Active").sum())
c3.metric("Inactive", (df_f["site_status"] == "Inactive").sum())
c4.metric("Completed", (df_f["site_status"] == "Completed").sum())
c5.metric("Avg Progress", f"{df_f['site_progress'].mean():.1f}%")
c6.metric(">60 Days Delayed", (df_f["site_delay_days"] > 60).sum())
