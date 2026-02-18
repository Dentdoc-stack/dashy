"""
charts.py — All Plotly chart functions for the KP-HCIP dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from config import RAG_COLORS, IPC_COLUMNS, IPC_STATUS_PRIORITY

# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------
STATUS_COLORS = {
    "Active": "#3498db",
    "Inactive": "#95a5a6",
    "Completed": "#2ecc71",
}

IPC_COLORS = {
    "Not Submitted": "#e74c3c",
    "Submitted": "#f39c12",
    "In Process": "#3498db",
    "Released": "#2ecc71",
}


# ---------------------------------------------------------------------------
# FR4 — Situation Room charts
# ---------------------------------------------------------------------------

def chart_package_ranking(df_pkg: pd.DataFrame) -> go.Figure:
    """Horizontal bar: packages ranked by average progress with critical delay annotation."""
    if df_pkg.empty:
        return go.Figure()

    df = df_pkg.sort_values("avg_progress", ascending=True)

    fig = px.bar(
        df,
        y="package_name",
        x="avg_progress",
        orientation="h",
        text="avg_progress",
        color_discrete_sequence=["#3498db"],
        labels={"avg_progress": "Avg Progress (%)", "package_name": ""},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        title="Package Ranking — Average Progress",
        xaxis=dict(range=[0, 105]),
        height=max(300, len(df) * 45),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def chart_delay_distribution(df_site: pd.DataFrame) -> go.Figure:
    """Donut chart: site counts per delay bucket."""
    if df_site.empty:
        return go.Figure()

    bucket_order = ["On Track", "1-30", "31-60", ">60"]
    counts = df_site["delay_bucket"].value_counts().reindex(bucket_order, fill_value=0)

    fig = go.Figure(go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=0.45,
        marker=dict(colors=[RAG_COLORS.get(b, "#bdc3c7") for b in counts.index]),
        textinfo="label+value+percent",
    ))
    fig.update_layout(
        title="Delay Distribution",
        height=350,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def chart_ipc_health(df_site: pd.DataFrame) -> go.Figure:
    """Stacked bar: IPC1–IPC6 status distribution across all sites."""
    if df_site.empty:
        return go.Figure()

    ipc_cols_present = [c for c in IPC_COLUMNS if c in df_site.columns]
    if not ipc_cols_present:
        return go.Figure()

    status_order = ["Not Submitted", "Submitted", "In Process", "Released"]
    data = []
    for col in ipc_cols_present:
        counts = df_site[col].value_counts().reindex(status_order, fill_value=0)
        for status in status_order:
            data.append({
                "IPC": col.upper().replace("_", " "),
                "Status": status,
                "Count": counts.get(status, 0),
            })

    df_ipc = pd.DataFrame(data)

    fig = px.bar(
        df_ipc,
        x="IPC",
        y="Count",
        color="Status",
        barmode="stack",
        color_discrete_map=IPC_COLORS,
        category_orders={"Status": status_order},
    )
    fig.update_layout(
        title="IPC Health — Status by Stage",
        height=350,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def chart_trend_progress(df_snapshots: pd.DataFrame) -> go.Figure | None:
    """Line chart: average site progress over time from snapshots."""
    if df_snapshots.empty or "_snapshot_ts" not in df_snapshots.columns:
        return None

    trend = (
        df_snapshots.groupby("_snapshot_ts")["site_progress"]
        .mean()
        .reset_index()
        .sort_values("_snapshot_ts")
    )

    fig = px.line(
        trend,
        x="_snapshot_ts",
        y="site_progress",
        markers=True,
        labels={"_snapshot_ts": "Snapshot Date", "site_progress": "Avg Progress (%)"},
    )
    fig.update_layout(
        title="Progress Trend Over Time",
        yaxis=dict(range=[0, 105]),
        height=350,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def chart_trend_completed(df_snapshots: pd.DataFrame) -> go.Figure | None:
    """Line chart: count of completed sites over time."""
    if df_snapshots.empty or "_snapshot_ts" not in df_snapshots.columns:
        return None

    from config import COMPLETION_THRESHOLD

    trend = (
        df_snapshots.groupby("_snapshot_ts")
        .apply(lambda g: (g["site_progress"] >= COMPLETION_THRESHOLD).sum(), include_groups=False)
        .reset_index(name="completed_sites")
        .sort_values("_snapshot_ts")
    )

    fig = px.line(
        trend,
        x="_snapshot_ts",
        y="completed_sites",
        markers=True,
        labels={"_snapshot_ts": "Snapshot Date", "completed_sites": "Completed Sites"},
    )
    fig.update_layout(
        title="Sites Completed Over Time",
        height=350,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


# ---------------------------------------------------------------------------
# FR5 — Risk & Recovery charts
# ---------------------------------------------------------------------------

def chart_risk_scatter(df_site: pd.DataFrame) -> go.Figure:
    """Scatter: site_progress vs site_delay_days, colored by delay bucket."""
    if df_site.empty:
        return go.Figure()

    fig = px.scatter(
        df_site,
        x="site_delay_days",
        y="site_progress",
        color="delay_bucket",
        color_discrete_map=RAG_COLORS,
        hover_data=["package_name", "district", "site_name", "risk_score"],
        labels={
            "site_delay_days": "Delay (days)",
            "site_progress": "Progress (%)",
            "delay_bucket": "Delay Bucket",
        },
        category_orders={"delay_bucket": ["On Track", "1-30", "31-60", ">60"]},
    )
    fig.update_layout(
        title="Risk Landscape — Progress vs Delay",
        height=450,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


# ---------------------------------------------------------------------------
# FR6 — Package Deep Dive charts
# ---------------------------------------------------------------------------

def chart_district_contribution(df_dist: pd.DataFrame) -> go.Figure:
    """Grouped bar: district-level avg progress for a single package."""
    if df_dist.empty:
        return go.Figure()

    df = df_dist.sort_values("avg_progress", ascending=True)

    fig = px.bar(
        df,
        y="district",
        x="avg_progress",
        orientation="h",
        text="avg_progress",
        color_discrete_sequence=["#3498db"],
        labels={"avg_progress": "Avg Progress (%)", "district": ""},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        title="District Contribution — Average Progress",
        xaxis=dict(range=[0, 105]),
        height=max(300, len(df) * 40),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


# ---------------------------------------------------------------------------
# FR7 — Site Command Center charts
# ---------------------------------------------------------------------------

def chart_discipline_progress(df_tasks_site: pd.DataFrame) -> go.Figure:
    """Horizontal bar: progress per discipline for a single site."""
    if df_tasks_site.empty:
        return go.Figure()

    disc = (
        df_tasks_site.groupby("discipline", dropna=False)["progress_pct"]
        .mean()
        .reset_index()
        .rename(columns={"progress_pct": "avg_progress"})
        .sort_values("avg_progress", ascending=True)
    )

    fig = px.bar(
        disc,
        y="discipline",
        x="avg_progress",
        orientation="h",
        text="avg_progress",
        color_discrete_sequence=["#2ecc71"],
        labels={"avg_progress": "Avg Progress (%)", "discipline": ""},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        title="Discipline Progress",
        xaxis=dict(range=[0, 105]),
        height=max(250, len(disc) * 40),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig
