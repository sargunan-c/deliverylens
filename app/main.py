"""
DeliveryLens: E-commerce Operations and Customer Experience Analytics Platform.
Main Streamlit Application Entrypoint.
"""

import sys
import os
import datetime
import streamlit as st

# Ensure project root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.views.executive import render_executive_view
from app.views.regional import render_regional_view
from app.views.sellers import render_sellers_view
from app.views.cx_reviews import render_cx_reviews_view
from app.views.cancellations import render_cancellations_view
from app.views.drilldown import render_drilldown_view
from src.db import run_query

st.set_page_config(
    page_title="DeliveryLens | Operations & CX Platform",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }
    div[data-testid="metric-container"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 14px 18px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0F172A;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📦 DeliveryLens")
st.markdown("**E-commerce Logistics Operations & Customer Experience Analytics**")

# Clean Deployment Environment Preflight Check
DB_FILE = os.path.join(ROOT_DIR, "data", "processed", "deliverylens.duckdb")
RAW_DATA_DIR = os.path.join(ROOT_DIR, "data", "raw")

if not os.path.exists(DB_FILE):
    core_csv = os.path.join(RAW_DATA_DIR, "olist_orders_dataset.csv")
    if os.path.exists(core_csv):
        with st.spinner("⏳ Initializing DuckDB analytical database from raw CSVs (first-time deployment run)..."):
            from src.loader import run_ingestion
            run_ingestion()
        st.success("Database initialized successfully!")
        st.rerun()
    else:
        st.error("⚠️ **Dataset Not Found in Deployment Environment**")
        st.info("""
        DeliveryLens requires the Brazilian Olist E-commerce dataset to be ingested into DuckDB.
        
        **How to Initialize the Platform:**
        1. Download the public Olist dataset from Kaggle:
           👉 [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
        2. Extract and place the CSV files inside `data/raw/`
        3. Run the automated ingestion pipeline:
           ```bash
           python src/loader.py
           ```
        4. Reload this application once the analytical database `data/processed/deliverylens.duckdb` is created.
        """)
        st.stop()

# Sidebar Filters
st.sidebar.title("🎛️ Operational Filters")

# Available dates in database
date_range = run_query("SELECT MIN(purchase_date) as min_d, MAX(purchase_date) as max_d FROM fact_orders").iloc[0]
min_date = date_range["min_d"]
max_date = date_range["max_d"]

start_date, end_date = st.sidebar.date_input(
    "Order Purchase Date Range",
    value=(datetime.date(2017, 1, 1), datetime.date(2018, 8, 31)),
    min_value=min_date,
    max_value=max_date,
    help="Filter transactions by purchase date."
)

# Macro Region Filter
macro_regions = ["All", "Southeast", "South", "Northeast", "Central-West", "North"]
selected_region = st.sidebar.selectbox("Customer Macro-Region", macro_regions, index=0)

# Dynamic State Filter
if selected_region == "All":
    available_states = ["All"] + sorted(run_query("SELECT DISTINCT customer_state FROM fact_orders WHERE customer_state IS NOT NULL")["customer_state"].tolist())
else:
    available_states = ["All"] + sorted(run_query(f"SELECT DISTINCT customer_state FROM fact_orders WHERE customer_macro_region = '{selected_region}'")["customer_state"].tolist())

selected_state = st.sidebar.selectbox("Customer State", available_states, index=0)

# Order Status Filter
statuses = ["All", "delivered", "canceled", "shipped", "unavailable", "invoiced", "processing"]
selected_status = st.sidebar.selectbox("Order Status", statuses, index=0)

# Assemble Filters dictionary
active_filters = {
    "start_date": start_date.strftime("%Y-%m-%d") if isinstance(start_date, datetime.date) else None,
    "end_date": end_date.strftime("%Y-%m-%d") if isinstance(end_date, datetime.date) else None,
    "macro_region": selected_region,
    "state": selected_state,
    "order_status": selected_status
}

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Methodology & Data Specs")
st.sidebar.caption("""
- **Dataset:** 99,441 verified orders from Olist Brazil.
- **Engine:** DuckDB in-process analytical engine.
- **Strict SLA Rule:** Late deliveries strictly evaluated against `order_estimated_delivery_date` on delivered orders.
- **Review Deduplication:** 1-to-1 latest review per order.
""")

# Top Tab Navigation
tabs = st.tabs([
    "📈 Executive Cockpit",
    "🗺️ Regional Logistics",
    "🏭 Seller Compliance",
    "⭐ CX & Reviews",
    "🚫 Cancellations",
    "🔎 Order Drilldown & CSV"
])

with tabs[0]:
    render_executive_view(active_filters)

with tabs[1]:
    render_regional_view(active_filters)

with tabs[2]:
    render_sellers_view(active_filters)

with tabs[3]:
    render_cx_reviews_view(active_filters)

with tabs[4]:
    render_cancellations_view(active_filters)

with tabs[5]:
    render_drilldown_view(active_filters)

