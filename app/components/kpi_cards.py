"""
KPI Scorecard components with modern CSS cards.
"""

import streamlit as st

def render_kpi_cards(kpis: dict):
    """Renders executive KPI scorecards with clean typography and badges."""
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric(
            label="Total Orders",
            value=f"{kpis['total_orders']:,}",
            help="Total recorded orders across selected period and filters."
        )
    with c2:
        st.metric(
            label="Delivered Orders",
            value=f"{int(kpis['delivered_orders']):,}",
            delta=f"{(kpis['delivered_orders'] / max(1, kpis['total_orders']) * 100):.1f}% delivery rate",
            delta_color="normal",
            help="Successfully fulfilled and delivered orders."
        )
    with c3:
        late_rate = kpis['late_delivery_rate_pct']
        st.metric(
            label="Late Delivery Rate",
            value=f"{late_rate:.2f}%",
            delta=f"{int(kpis['late_orders']):,} late orders",
            delta_color="inverse", # Red/warning when positive
            help="Percentage of delivered orders that exceeded the estimated delivery date."
        )
    with c4:
        st.metric(
            label="Avg Review Score",
            value=f"{kpis['avg_review_score']:.2f} / 5.0",
            help="Average customer review rating (1-5 stars)."
        )

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.metric(
            label="Avg Delay (Late Orders)",
            value=f"{kpis['avg_delay_days_late']:.1f} days",
            help="Average days past the promised estimated delivery date for delayed orders."
        )
    with c6:
        st.metric(
            label="Avg Transit Time",
            value=f"{kpis['avg_transit_days']:.1f} days",
            help="Average elapsed days from order purchase timestamp to customer doorstep delivery."
        )
    with c7:
        st.metric(
            label="Cancellation Rate",
            value=f"{kpis['cancellation_rate_pct']:.2f}%",
            delta=f"{int(kpis['canceled_orders']):,} canceled",
            delta_color="inverse",
            help="Orders with canceled status."
        )
    with c8:
        st.metric(
            label="Total GMV",
            value=f"R$ {kpis['total_gmv_brl']:,.2f}",
            help="Gross Merchandise Value including freight."
        )

