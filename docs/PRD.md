# DeliveryLens: Product Requirements Document (PRD) 📋

## 1. Executive Summary & Problem Statement

### 1.1 The Business Problem
E-commerce operations and marketplace leaders at Olist Brazil struggle to balance aggressive fulfillment SLAs with variable carrier and seller reliability across Brazil's vast territory. Logistics delays damage customer satisfaction, trigger 1-star reviews, and increase operational costs. Operations teams currently lack a centralized, SQL-backed analytics system to:
1. Isolate whether a late delivery was caused by merchant delay (dispatch breach) vs courier delay (in-transit bottleneck).
2. Identify which geographic corridors (e.g. Southeast to Northeast/North) suffer the highest friction.
3. Quantify the exact financial and satisfaction cost of delivery delays.

### 1.2 Product Vision
DeliveryLens is an intuitive, SQL-driven operations intelligence platform that empowers Product Operations, Logistics Leads, and Marketplace PMs to diagnose root causes behind late deliveries and execute targeted operational interventions.

---

## 2. Target Personas & Jobs-To-Be-Done (JTBD)

### Persona 1: Operations Manager (Logistics & Carriers)
* **Goal:** Monitor carrier SLAs, detect regional bottlenecks, and optimize estimated delivery promise algorithms.
* **JTBD:** *"When regional carrier performance degrades, I want to see which states have rising late rates and transit days, so that I can re-route volume to alternative 3PLs or adjust checkout delivery estimates."*

### Persona 2: Marketplace Merchant Operations Lead
* **Goal:** Track seller fulfillment compliance and penalize chronic SLA violators.
* **JTBD:** *"When customer orders arrive late, I want to separate merchant dispatch latency from carrier transit time, so that I can intervene with sellers whose delayed handoffs are causing late deliveries."*

### Persona 3: Customer Experience (CX) Product Analyst
* **Goal:** Measure how fulfillment metrics correlate with customer retention and review ratings.
* **JTBD:** *"When analyzing negative review trends, I want to quantify the tipping point where delivery delay turns satisfied customers into 1-star detractors, so that product teams can prioritize proactive compensation."*

---

## 3. User Stories & Acceptance Criteria

| ID | User Story | Priority (MoSCoW) | Acceptance Criteria |
|---|---|---|---|
| **US-01** | As an Operations Lead, I want an executive scorecard of core KPIs so that I can immediately gauge platform health. | **Must Have** | Displays Total Orders, Delivered Orders, Late Delivery Rate %, Avg Delay Days, Avg Transit Days, and Avg Review Score. |
| **US-02** | As an Analyst, I want a dual-axis trend chart of monthly orders and late delivery rates so that I can observe seasonality and performance drift. | **Must Have** | Interactive time-series showing monthly order volume (bars) and late delivery % (line) from 2017 to 2018. |
| **US-03** | As a Logistics PM, I want a regional delivery performance view across Brazilian macro-regions and states so that I can locate delivery hotspots. | **Must Have** | Table and bar chart displaying late rates, avg transit time, and avg freight cost broken down by 27 states and 5 macro-regions. |
| **US-04** | As a Merchant Ops Lead, I want to analyze seller compliance so that I can identify merchants failing contractual shipping limits. | **Must Have** | Scatter plot & ranking tables correlating seller late carrier handoff rate with final customer late delivery rate. |
| **US-05** | As a CX Analyst, I want to observe the "Satisfaction Cliff" of reviews vs delay days so that I understand customer tolerance thresholds. | **Must Have** | Categorized delay buckets (< -10 days early to > 14 days late) showing avg star rating and % 1-star negative ratings. |
| **US-06** | As an Ops Analyst, I want to decompose canceled orders by stage (pre-dispatch vs in-transit) so that I understand order dropout causes. | **Should Have** | Quantification of cancellations happening before courier receipt vs during carrier transit. |
| **US-07** | As a User, I want global sidebar filters (date range, region, state, status) so that all views update dynamically. | **Must Have** | Sidebar filters dynamically adjust queries in DuckDB with zero server lag. |
| **US-08** | As an Analyst, I want to search underlying order records and export the filtered data to CSV so that I can conduct offline investigations. | **Must Have** | Interactive searchable table with an instant CSV download button. |

---

## 4. Technical Constraints & Design Principles
1. **Zero Data Hallucination:** 100% of reported statistics are directly derived from the verified Olist dataset.
2. **In-Process Analytical Power:** Powered by DuckDB for sub-second aggregations over 100k+ rows without external database infrastructure.
3. **Decoupled Architecture:** Clean separation of database connection (`db.py`), ETL pipeline (`loader.py`), business metrics service (`metrics.py`), and presentation layer (`app/`).
