"""
Plotly Chart Builders for DeliveryLens.
Clean, modern aesthetic with consistent color palettes.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

COLORS = {
    "primary": "#1E3A8A",      # Deep Navy
    "secondary": "#3B82F6",    # Blue
    "accent_red": "#EF4444",   # Coral Red (Late)
    "accent_green": "#10B981", # Emerald (On-time)
    "accent_yellow": "#F59E0B",# Amber
    "neutral_gray": "#6B7280", # Slate Gray
    "bg_card": "#F8FAFC"
}

def plot_monthly_volume_and_late_rate(df: pd.DataFrame) -> go.Figure:
    """Dual-axis chart: Monthly Order Volume (bars) and Late Delivery Rate % (line)."""
    fig = go.Figure()

    # Bar: Delivered Orders
    fig.add_trace(go.Bar(
        x=df["purchase_year_month"],
        y=df["delivered_orders"],
        name="Delivered Orders",
        marker_color="#93C5FD",
        opacity=0.85,
        yaxis="y1"
    ))

    # Line: Late Delivery Rate %
    fig.add_trace(go.Scatter(
        x=df["purchase_year_month"],
        y=df["late_delivery_rate_pct"],
        name="Late Delivery Rate (%)",
        mode="lines+markers",
        line=dict(color=COLORS["accent_red"], width=3),
        marker=dict(size=7),
        yaxis="y2"
    ))

    fig.update_layout(
        title=dict(
            text="Monthly Delivered Orders vs. Late Delivery Rate",
            y=0.97,
            x=0,
            xanchor="left",
            font=dict(size=16)
        ),
        xaxis=dict(title=dict(text="Year-Month", standoff=10), tickangle=-45, showgrid=False),
        yaxis=dict(title=dict(text="Delivered Orders Volume", standoff=10), showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
        yaxis2=dict(
            title=dict(text="Late Delivery Rate (%)", standoff=10),
            overlaying="y",
            side="right",
            showgrid=False,
            ticksuffix="%"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.06,
            xanchor="right",
            x=1
        ),
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=50, r=50, t=75, b=50)
    )
    return fig

def plot_ontime_vs_late_donut(delivered: int, late: int) -> go.Figure:
    """Donut chart showing proportion of on-time vs late delivered orders."""
    on_time = max(0, delivered - late)
    fig = go.Pie(
        labels=["On-Time Deliveries", "Late Deliveries"],
        values=[on_time, late],
        hole=0.6,
        marker=dict(colors=[COLORS["accent_green"], COLORS["accent_red"]]),
        textinfo="label+percent",
        hoverinfo="label+value+percent"
    )
    layout = go.Layout(
        title=dict(
            text="Delivery Fulfillment Ratio",
            y=0.96,
            x=0.5,
            xanchor="center",
            font=dict(size=16)
        ),
        template="plotly_white",
        margin=dict(l=25, r=25, t=65, b=25),
        showlegend=False
    )
    return go.Figure(data=[fig], layout=layout)

def plot_regional_late_rates(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart comparing late delivery rates across states."""
    df_sorted = df.sort_values("late_delivery_rate_pct", ascending=True)
    fig = px.bar(
        df_sorted,
        x="late_delivery_rate_pct",
        y="customer_state",
        color="customer_macro_region",
        orientation="h",
        labels={
            "late_delivery_rate_pct": "Late Delivery Rate (%)",
            "customer_state": "State",
            "customer_macro_region": "Region"
        },
        title="Late Delivery Rate by Customer State",
        text=df_sorted["late_delivery_rate_pct"].apply(lambda v: f"{v:.1f}%")
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        title=dict(
            text="Late Delivery Rate by Customer State",
            y=0.98,
            x=0,
            xanchor="left",
            font=dict(size=16)
        ),
        template="plotly_white",
        height=660,
        margin=dict(l=55, r=50, t=70, b=45),
        xaxis=dict(ticksuffix="%", showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
        yaxis=dict(showgrid=False),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1
        )
    )
    return fig

def plot_delay_cliff_vs_review(df: pd.DataFrame) -> go.Figure:
    """The 'Delay Cliff': Average review score & % 1-star reviews across delay buckets."""
    fig = go.Figure()

    # Bar: % 1-star reviews
    fig.add_trace(go.Bar(
        x=df["delivery_performance_bucket"],
        y=df["pct_1_star_reviews"],
        name="% 1-Star Negative Reviews",
        marker_color=COLORS["accent_red"],
        opacity=0.75,
        yaxis="y1"
    ))

    # Line: Average Review Score
    fig.add_trace(go.Scatter(
        x=df["delivery_performance_bucket"],
        y=df["avg_review_score"],
        name="Average Review Rating (1-5)",
        mode="lines+markers+text",
        text=df["avg_review_score"].apply(lambda v: f"{v:.2f}★"),
        textposition="top center",
        line=dict(color=COLORS["primary"], width=3),
        marker=dict(size=9, color=COLORS["primary"]),
        yaxis="y2"
    ))

    fig.update_layout(
        title=dict(
            text="The Satisfaction Cliff: Customer Review Rating vs. Delivery Delay",
            y=0.97,
            x=0,
            xanchor="left",
            font=dict(size=16)
        ),
        xaxis=dict(
            title=dict(text="Delivery Performance Relative to Estimated Date", standoff=15),
            tickangle=-15,
            showgrid=False
        ),
        yaxis=dict(
            title=dict(text="% 1-Star Reviews", standoff=10),
            showgrid=True,
            gridcolor="rgba(128,128,128,0.15)",
            ticksuffix="%"
        ),
        yaxis2=dict(
            title=dict(text="Avg Review Score (Stars)", standoff=10),
            overlaying="y",
            side="right",
            range=[1.0, 5.6],  # Headroom for top center labels
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.06,
            xanchor="right",
            x=1
        ),
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=55, r=55, t=80, b=60)
    )
    return fig

def plot_seller_handoff_vs_delivery_late(df: pd.DataFrame) -> go.Figure:
    """Scatter plot: Late carrier handoff rate vs Late customer delivery rate."""
    fig = px.scatter(
        df,
        x="late_handoff_rate_pct",
        y="late_delivery_rate_pct",
        size="total_orders",
        color="seller_macro_region",
        hover_data=["seller_id", "seller_city", "seller_state", "avg_review_score"],
        labels={
            "late_handoff_rate_pct": "Seller Late Carrier Handoff Rate (%)",
            "late_delivery_rate_pct": "Customer Late Delivery Rate (%)",
            "total_orders": "Order Volume",
            "seller_macro_region": "Seller Region"
        },
        title="Seller Root Cause: Late Dispatch vs. Late Customer Delivery"
    )
    fig.update_layout(
        title=dict(
            text="Seller Root Cause: Late Dispatch vs. Late Customer Delivery",
            y=0.97,
            x=0,
            xanchor="left",
            font=dict(size=16)
        ),
        template="plotly_white",
        margin=dict(l=55, r=50, t=75, b=50),
        xaxis=dict(ticksuffix="%", showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
        yaxis=dict(ticksuffix="%", showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="right",
            x=1
        )
    )
    return fig

