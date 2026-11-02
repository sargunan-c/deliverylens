"""
Drilldown & CSV Data Export View.
"""

import streamlit as st
import pandas as pd
from src.metrics import get_drilldown_records

def render_drilldown_view(filters: dict):
    st.subheader("🔎 Order Records Drilldown & CSV Export")
    st.caption("Inspect granular transaction records backing the metrics, search by Order ID, and export filtered datasets.")
    
    col_limit, col_search = st.columns([1, 2])
    with col_limit:
        row_limit = st.selectbox("Maximum Records to Display", [100, 250, 500, 1000], index=1)
    with col_search:
        order_search = st.text_input("Filter by exact Order ID or Customer ID (optional)").strip()
        
    df = get_drilldown_records(filters, limit=row_limit)
    
    if order_search:
        df = df[df["order_id"].str.contains(order_search, case=False, na=False) | 
                df["customer_id"].str.contains(order_search, case=False, na=False)]
        
    if df.empty:
        st.warning("No records found matching the specified search and filter criteria.")
        return

    st.markdown(f"**Showing {len(df):,} records** (matching active filters)")
    
    # Download Button
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="deliverylens_filtered_orders.csv",
        mime="text/csv",
        type="primary"
    )
    
    st.dataframe(
        df.style.format({
            "actual_delivery_days": "{:.1f} d",
            "estimated_delivery_days": "{:.1f} d",
            "delay_days": "{:.1f} d",
            "total_order_value": "R$ {:.2f}",
            "total_freight_value": "R$ {:.2f}",
            "review_score": "{:.0f} ★"
        }),
        use_container_width=True,
        height=550,
        hide_index=True
    )

