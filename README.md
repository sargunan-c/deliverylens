# DeliveryLens 📦🔍
**E-commerce Operations and Customer Experience Analytics Platform**

DeliveryLens is an operations and customer experience intelligence platform built using Python, DuckDB, Streamlit, and Plotly. It ingests real-world e-commerce transaction data from the Brazilian Olist platform to uncover root causes behind delayed deliveries, poor customer reviews, and logistics bottlenecks across regions and sellers.

---

## 🏗️ Project Architecture & Directory Structure

```text
deliverylens/
├── data/
│   ├── raw/                  # Source CSV files from Olist dataset (not tracked in Git)
│   └── processed/            # DuckDB database file (deliverylens.duckdb) and analytics marts
├── sql/
│   ├── schema/               # DDL for raw staging tables & indexes
│   ├── kpi/                  # Core operational & CX metric SQL queries
│   └── drilldown/            # Granular root-cause & cohort SQL queries
├── src/
│   ├── db.py                 # DuckDB connection manager & query runner
│   ├── loader.py             # CSV-to-DuckDB ingestion & schema validation script
│   └── metrics.py            # Analytics calculation service & data access layer
├── app/
│   ├── main.py               # Streamlit application entry point
│   ├── components/           # Reusable UI widgets (KPI scorecards, filters, tables)
│   └── views/                # Dashboard views (Executive, Logistics, Sellers, CX, Drilldown)
├── docs/
│   ├── PRD.md                # Product Requirements Document & User Stories
│   ├── DATA_DICTIONARY.md   # Schema catalog, table relationships & grain definitions
│   ├── KPI_DEFINITIONS.md    # Formal operational KPI equations & business logic
│   └── CASE_STUDY.md         # Portfolio case study & business findings
├── tests/
│   └── test_queries.py       # SQL assertion checks & data reconciliation tests
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📥 Dataset Setup Instructions

1. Download the public Brazilian E-Commerce dataset from Kaggle:
   👉 **URL:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
2. Extract the downloaded `archive.zip` and place all 9 `.csv` files inside `data/raw/`:
   - `olist_orders_dataset.csv`
   - `olist_order_items_dataset.csv`
   - `olist_order_payments_dataset.csv`
   - `olist_order_reviews_dataset.csv`
   - `olist_customers_dataset.csv`
   - `olist_sellers_dataset.csv`
   - `olist_products_dataset.csv`
   - `olist_geolocation_dataset.csv`
   - `product_category_name_translation.csv`
