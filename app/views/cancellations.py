"""
Cancellation Analysis View.
"""

import streamlit as st
import pandas as pd
from src.metrics import get_cancellation_analysis
from src.db import run_query

def render_cancellations_view(filters: dict):
    st.subheader("🚫 Order Cancellation Diagnostics")
    st.caption("Pinpoint where and when orders fall out of the fulfillment funnel: pre-dispatch vs in-transit loss.")
    
    df_cancel = get_cancellation_analysis(filters)
    
    if df_cancel.empty:
        st.warning("No cancellation records match the current filter selection.")
        return

    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("##### 📍 Cancellation Rates by Customer Macro-Region")
        st.dataframe(
            df_cancel.style.format({
                "total_orders": "{:,}",
                "canceled_orders": "{:,}",
                "cancellation_rate_pct": "{:.2f}%",
                "canceled_in_transit": "{:,}",
                "canceled_before_dispatch": "{:,}",
                "avg_canceled_order_value": "R$ {:.2f}"
            }),
            width="stretch",
            hide_index=True
        )
        
    with col2:
        total_canceled = df_cancel["canceled_orders"].sum()
        in_transit = df_cancel["canceled_in_transit"].sum()
        before_dispatch = df_cancel["canceled_before_dispatch"].sum()
        
        st.markdown("##### ⏱️ Cancellation Stage Distribution")
        st.markdown(f"""
        - **Total Canceled Orders:** {total_canceled:,}
        - **Canceled Before Carrier Dispatch:** {before_dispatch:,} ({before_dispatch*100.0/max(1, total_canceled):.1f}%)
        - **Canceled After Carrier Dispatch:** {in_transit:,} ({in_transit*100.0/max(1, total_canceled):.1f}%)
        """)
        
        st.info("""
        **Operational Takeaway:**  
        Over 85% of order cancellations happen **before** the item is handed over to the carrier.
        This points toward merchant fulfillment lag, stockouts, or inventory misalignment rather than courier transit failures.
        """)

