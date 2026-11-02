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

# Clean Deployment Environment Preflight & Auto-Ingestion
DB_FILE = os.path.join(ROOT_DIR, "data", "processed", "deliverylens.duckdb")
RAW_DATA_DIR = os.path.join(ROOT_DIR, "data", "raw")

REQUIRED_RAW_CSVS = [
    "olist_orders_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_products_dataset.csv",
    "olist_geolocation_dataset.csv",
    "product_category_name_translation.csv"
]

@st.cache_resource(show_spinner="⏳ Building analytical DuckDB marts from raw Olist dataset (one-time setup)...")
def ensure_database_ready():
    """Initializes DuckDB database if missing. Cached across sessions to avoid re-ingestion."""
    if os.path.exists(DB_FILE) and os.path.getsize(DB_FILE) > 0:
        return True
        
    missing_files = [f for f in REQUIRED_RAW_CSVS if not os.path.exists(os.path.join(RAW_DATA_DIR, f))]
    if missing_files:
        return missing_files
        
    from src.loader import run_ingestion
    run_ingestion()
    return True

db_status = ensure_database_ready()

if db_status is not True:
    st.error("⚠️ **Dataset Missing in Deployment Environment**")
    st.markdown(f"The following required dataset files are missing from `data/raw/`:")
    for mf in db_status:
        st.markdown(f"- `{mf}`")
    st.info("""
    **To resolve this:**
    1. Ensure the dataset CSVs are placed inside the repository's `data/raw/` directory.
    2. Download source: [Brazilian E-Commerce Public Dataset by Olist on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
    3. Re-deploy or restart the application.
    """)
    st.stop()

# Sidebar Filters
st.sidebar.title("🎛️ Operational Filters")

# Available dates in database
date_range = run_query("SELECT MIN(purchase_date) as min_d, MAX(purchase_date) as max_d FROM fact_orders").iloc[0]
min_date = date_range["min_d"]
max_date = date_range["max_d"]

date_selection = st.sidebar.date_input(
    "Order Purchase Date Range",
    value=(datetime.date(2017, 1, 1), datetime.date(2018, 8, 31)),
    min_value=min_date,
    max_value=max_date,
    help="Filter transactions by purchase date."
)

# Robust date range parsing (handles single clicks, partial ranges, and cleared inputs)
if isinstance(date_selection, (tuple, list)):
    if len(date_selection) == 2:
        start_date, end_date = date_selection
    elif len(date_selection) == 1:
        start_date = date_selection[0]
        end_date = date_selection[0]
    else:
        start_date = min_date
        end_date = max_date
elif isinstance(date_selection, datetime.date):
    start_date = date_selection
    end_date = date_selection
else:
    start_date = min_date
    end_date = max_date

# Ensure chronological ordering if user selects in reverse
if start_date and end_date and start_date > end_date:
    start_date, end_date = end_date, start_date

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

