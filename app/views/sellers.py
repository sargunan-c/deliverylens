"""
Seller Performance and Fulfillment Compliance View.
"""

import streamlit as st
import pandas as pd
from app.components.charts import plot_seller_handoff_vs_delivery_late
from src.metrics import get_seller_performance

def render_sellers_view(filters: dict):
    st.subheader("🏭 Seller Fulfillment & Carrier Handoff Compliance")
    st.caption("Distinguish merchant dispatch latency from carrier transit delays. Pinpoint sellers causing late customer deliveries.")
    
    col_filter, _ = st.columns([1, 2])
    with col_filter:
        min_order_threshold = st.slider("Minimum Seller Order Volume Threshold", 10, 100, 25, 5)
        
    df_sellers = get_seller_performance(filters, min_orders=min_order_threshold)
    
    if df_sellers.empty:
        st.info("No sellers meet the minimum order threshold for the selected filters.")
        return

    st.plotly_chart(plot_seller_handoff_vs_delivery_late(df_sellers), use_container_width=True)
    
    st.markdown("---")
    
    col_worst, col_best = st.columns(2)
    
    with col_worst:
        st.markdown("##### ⚠️ Highest Late Delivery Rate Sellers (SLA Risks)")
        worst_sellers = df_sellers.sort_values("late_delivery_rate_pct", ascending=False).head(10)
        st.dataframe(
            worst_sellers[[
                "seller_id", "seller_state", "total_orders", 
                "late_delivery_rate_pct", "late_handoff_rate_pct", "avg_review_score"
            ]].style.format({
                "total_orders": "{:,}",
                "late_delivery_rate_pct": "{:.1f}%",
                "late_handoff_rate_pct": "{:.1f}%",
                "avg_review_score": "{:.2f} ★"
            }),
            use_container_width=True,
            hide_index=True
        )
        
    with col_best:
        st.markdown("##### 🏆 Benchmark Sellers (Lowest Delay Rate)")
        best_sellers = df_sellers.sort_values(["late_delivery_rate_pct", "total_orders"], ascending=[True, False]).head(10)
        st.dataframe(
            best_sellers[[
                "seller_id", "seller_state", "total_orders", 
                "late_delivery_rate_pct", "late_handoff_rate_pct", "avg_review_score"
            ]].style.format({
                "total_orders": "{:,}",
                "late_delivery_rate_pct": "{:.1f}%",
                "late_handoff_rate_pct": "{:.1f}%",
                "avg_review_score": "{:.2f} ★"
            }),
            use_container_width=True,
            hide_index=True
        )
