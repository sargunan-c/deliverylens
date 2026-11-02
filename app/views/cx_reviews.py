"""
Customer Experience and Reviews Analysis View.
"""

import streamlit as st
import pandas as pd
from app.components.charts import plot_delay_cliff_vs_review
from src.metrics import get_delay_buckets_vs_review
from src.db import run_query

def render_cx_reviews_view(filters: dict):
    st.subheader("💬 Customer Experience & The Delivery Satisfaction Cliff")
    st.caption("Quantify how delivery delays destroy customer satisfaction and trigger 1-star negative ratings.")
    
    df_cliff = get_delay_buckets_vs_review(filters)
    
    if df_cliff.empty:
        st.warning("No review records found matching current filters.")
        return

    st.plotly_chart(plot_delay_cliff_vs_review(df_cliff), width="stretch")
    
    # Statistical table
    st.markdown("##### 📊 Delivery Performance vs Review Sentiment Table")
    st.dataframe(
        df_cliff.style.format({
            "order_count": "{:,}",
            "avg_review_score": "{:.2f} ★",
            "pct_1_star_reviews": "{:.1f}%",
            "pct_5_star_reviews": "{:.1f}%"
        }),
        width="stretch",
        hide_index=True
    )

    st.markdown("---")
    
    st.markdown("##### 📝 Qualitative Review Feedback: On-Time vs. Late Orders")
    col_ontime_reviews, col_late_reviews = st.columns(2)
    
    with col_ontime_reviews:
        st.markdown("##### 🟢 Sample Comments: On-Time Deliveries")
        df_sample_ontime = run_query("""
            SELECT review_score, review_comment_message, customer_state, delay_days
            FROM fact_orders
            WHERE is_on_time = 1 AND review_comment_message IS NOT NULL
            ORDER BY review_score DESC, purchase_date DESC
            LIMIT 5;
        """)
        for _, row in df_sample_ontime.iterrows():
            st.markdown(f"""
            > **{row['review_score']}★** (Delivered **{abs(row['delay_days']):.0f} days early** in {row['customer_state']})  
            > *"{row['review_comment_message']}"*
            """)
            
    with col_late_reviews:
        st.markdown("##### 🔴 Sample Comments: Late Deliveries")
        df_sample_late = run_query("""
            SELECT review_score, review_comment_message, customer_state, delay_days
            FROM fact_orders
            WHERE is_late = 1 AND review_comment_message IS NOT NULL
            ORDER BY delay_days DESC
            LIMIT 5;
        """)
        for _, row in df_sample_late.iterrows():
            st.markdown(f"""
            > **{row['review_score']}★** (Delivered **+{row['delay_days']:.0f} days late** in {row['customer_state']})  
            > *"{row['review_comment_message']}"*
            """)

