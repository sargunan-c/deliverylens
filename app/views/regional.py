"""
Regional Logistics View.
"""

import streamlit as st
import pandas as pd
from app.components.charts import plot_regional_late_rates
from src.metrics import get_regional_performance

def render_regional_view(filters: dict):
    st.subheader("🌎 Regional Logistics & Geographic Friction")
    st.caption("Identify geographic bottlenecks, state-level late delivery spikes, and inter-state logistics costs.")
    
    df_regional = get_regional_performance(filters)
    
    if df_regional.empty:
        st.warning("No regional records match the current filter selection.")
        return

    # Macro Region Aggregation
    macro_agg = df_regional.groupby("customer_macro_region").agg({
        "total_orders": "sum",
        "delivered_orders": "sum",
        "late_orders": "sum",
        "avg_transit_days": "mean",
        "avg_freight_cost": "mean",
        "avg_review_score": "mean"
    }).reset_index()
    
    macro_agg["late_delivery_rate_pct"] = (
        macro_agg["late_orders"] * 100.0 / macro_agg["delivered_orders"].replace(0, 1)
    ).round(2)
    macro_agg = macro_agg.sort_values("late_delivery_rate_pct", ascending=False)

    st.markdown("##### 📍 Performance by Brazilian Macro-Region")
    st.dataframe(
        macro_agg.style.format({
            "total_orders": "{:,}",
            "delivered_orders": "{:,}",
            "late_orders": "{:,}",
            "late_delivery_rate_pct": "{:.2f}%",
            "avg_transit_days": "{:.1f} days",
            "avg_freight_cost": "R$ {:.2f}",
            "avg_review_score": "{:.2f} ★"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(plot_regional_late_rates(df_regional), use_container_width=True)
        
    with col2:
        st.markdown("##### 🔍 State-Level Breakdown & Friction Ranking")
        st.dataframe(
            df_regional[[
                "customer_state", "customer_macro_region", "total_orders", 
                "late_delivery_rate_pct", "avg_transit_days", "avg_freight_cost", "avg_review_score"
            ]].style.format({
                "total_orders": "{:,}",
                "late_delivery_rate_pct": "{:.2f}%",
                "avg_transit_days": "{:.1f} d",
                "avg_freight_cost": "R$ {:.2f}",
                "avg_review_score": "{:.2f} ★"
            }),
            use_container_width=True,
            height=580,
            hide_index=True
        )

