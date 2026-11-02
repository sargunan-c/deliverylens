"""
Executive Overview View.
"""

import streamlit as st
import pandas as pd
from app.components.kpi_cards import render_kpi_cards
from app.components.charts import (
    plot_monthly_volume_and_late_rate,
    plot_ontime_vs_late_donut
)
from src.metrics import get_executive_kpis, get_monthly_trends

def render_executive_view(filters: dict):
    st.subheader("📊 Executive Operations & Performance Cockpit")
    st.caption("High-level visibility into order fulfillment, transit SLA compliance, customer satisfaction, and revenue.")
    
    # KPIs
    kpis = get_executive_kpis(filters)
    render_kpi_cards(kpis)
    
    st.markdown("---")
    
    # Charts Section
    col_main, col_donut = st.columns([2, 1])
    
    with col_main:
        trends_df = get_monthly_trends(filters)
        if not trends_df.empty:
            st.plotly_chart(plot_monthly_volume_and_late_rate(trends_df), use_container_width=True)
        else:
            st.info("No trend data available for current filter selection.")
            
    with col_donut:
        delivered_count = int(kpis["delivered_orders"])
        late_count = int(kpis["late_orders"])
        if delivered_count > 0:
            st.plotly_chart(plot_ontime_vs_late_donut(delivered_count, late_count), use_container_width=True)
            
            # Quick summary badge
            st.markdown(f"""
            <div style="background-color: #F1F5F9; padding: 12px; border-radius: 8px; border-left: 4px solid #3B82F6;">
                <strong>Key Insight:</strong> 
                Out of <b>{delivered_count:,}</b> fulfilled deliveries, <b>{late_count:,}</b> orders 
                ({kpis['late_delivery_rate_pct']}%) exceeded promised arrival dates, averaging 
                <b>+{kpis['avg_delay_days_late']:.1f} days</b> of customer delay.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No delivered orders found in selection.")
