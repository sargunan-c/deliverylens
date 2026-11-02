# DeliveryLens 📦🔍
**E-commerce Operations and Customer Experience Analytics Platform**

DeliveryLens is an interactive, SQL-backed operations intelligence platform built with **Python**, **DuckDB**, **Streamlit**, and **Plotly**. It models and analyzes 99,441 verified real-world transactions from the Brazilian Olist e-commerce ecosystem to diagnose delivery friction, isolate seller vs courier delays, and quantify the impact of transit delays on customer satisfaction.

---

## 🌟 Key Features

1. **Executive Operations Cockpit:** Real-time visibility into Total Orders, Delivered Orders, Late Delivery Rate (%), Average Delay (Days), Transit Times, GMV, and Average Review Score.
2. **Monthly Delivery & Volume Trends:** Dual-axis visualization tracking order growth against fulfillment performance.
3. **Regional Logistics Friction:** Deep-dive into Brazilian macro-regions and 27 states, spotlighting geographic delivery disparities and freight cost burdens.
4. **Seller Fulfillment Compliance:** Isolate merchant dispatch delays from courier transit times to identify SLA risks.
5. **The Satisfaction Cliff:** Quantify how delivery delays destroy customer satisfaction and trigger 1-star reviews.
6. **Cancellation Diagnostics:** Decompose order drop-offs into pre-dispatch vs in-transit cancellations.
7. **Granular Order Drilldown & CSV Export:** Search individual orders and export filtered datasets for offline analysis.

---

## 📊 Ground Truth Insights (Empirical Findings)

- **Platform Late Rate:** Out of 96,478 delivered orders, **7,826 (8.11%)** arrived late, averaging **+9.55 days** of delay.
- **Regional Polarization:** The **Northeast** suffers a **14.33% late delivery rate** and an average transit time of **20.0 days**, compared to the **Southeast** at **7.45% late rate** and **10.8 days**.
- **The "Satisfaction Cliff":** On-time deliveries maintain an average score of **4.26★** (9.4% 1-star). For orders delayed >7 days, the average score collapses to **1.64★**, with **68.2%** of customers leaving 1-star reviews.
- **Upstream Seller Delays:** In **28.39% of late order items**, the seller breached their shipping limit deadline *before* the carrier even received the item.
- **Pre-Dispatch Cancellations:** **88.0% of order cancellations** occur before the package is handed off to a courier, indicating upstream inventory issues.

---

## 🏗️ Architecture & Directory Structure

```text
deliverylens/
├── app/
│   ├── main.py               # Streamlit application entry point
│   ├── components/           # Reusable KPI scorecards and Plotly chart builders
│   └── views/                # Tabbed analytical modules (Executive, Regional, Sellers, CX, Drilldown)
├── data/
│   ├── raw/                  # Source Olist CSV files
│   └── processed/            # DuckDB analytical database (deliverylens.duckdb)
├── docs/
│   ├── PRD.md                # Product Requirements Document & User Stories
│   ├── DATA_DICTIONARY.md    # Schema specifications, table relationships & grain definitions
│   ├── KPI_DEFINITIONS.md    # Formal mathematical equations & SQL logic
│   ├── FINDINGS_AND_RECOMMENDATIONS.md # Real data findings & business action plan
│   └── CASE_STUDY.md         # Professional portfolio case study
├── sql/
│   ├── kpi/                  # Modular SQL queries for all core metrics
│   └── drilldown/            # Root-cause analysis queries
├── src/
│   ├── db.py                 # DuckDB connection manager & query runner
│   ├── loader.py             # CSV-to-DuckDB ingestion & schema validation pipeline
│   └── metrics.py            # Analytics calculation service & data access layer
├── tests/
│   ├── test_queries.py       # Automated metric assertions & edge-case checks
│   └── test_views.py         # End-to-end smoke test for charts and views
├── requirements.txt          # Python dependencies
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites & Environment Setup
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/deliverylens.git
cd deliverylens
pip install -r requirements.txt
```

### 2. Ingest the Data into DuckDB
Ensure the 9 Olist CSV files are placed in `data/raw/`, then execute the ingestion pipeline:
```bash
python src/loader.py
```
*This creates the optimized database at `data/processed/deliverylens.duckdb` with deduplicated reviews and analytical fact tables.*

### 3. Run Automated Validation Tests
Run the test suite to verify metric calculations and data integrity:
```bash
python tests/test_queries.py
python tests/test_views.py
```

### 4. Launch the Streamlit Dashboard
Start the interactive dashboard locally:
```bash
streamlit run app/main.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Analytical Rigor & Edge Case Handling

1. **Review Fan-Out Prevention:** Deduplicated 551 multi-review orders using window functions (`ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC)`) to prevent revenue inflation.
2. **Strict Late Delivery Logic:** Only completed deliveries with valid delivery dates (`order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL`) are evaluated for late rates.
3. **Dispatch vs. Transit Attribution:** Decoupled merchant packaging delays from carrier transit delays by comparing carrier handoff dates against contractual seller shipping deadlines.
