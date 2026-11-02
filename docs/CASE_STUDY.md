# Portfolio Case Study: DeliveryLens 🚀
**E-commerce Operations & Customer Experience Analytics Platform**

* **Target Roles:** Product Analyst, Product Operations, Associate Product Manager (APM), Business Analyst
* **Author:** Candidate Portfolio Project
* **Tech Stack:** SQL (DuckDB), Python, Streamlit, Pandas, Plotly, Git/GitHub
* **Dataset:** 99,441 verified real-world orders from Brazilian Olist E-commerce

---

## 1. Project Background & Context
E-commerce marketplaces depend on timely fulfillment to sustain customer trust. When deliveries arrive late, customer experience degrades, negative reviews surge, and marketplace GMV suffers. At Olist—a major Brazilian marketplace connecting small merchants with national e-commerce channels—operations teams faced challenges isolating whether fulfillment failures stemmed from third-party merchant delays, regional courier bottlenecks, or inaccurate promised delivery dates.

As an aspiring Product Analyst, I built **DeliveryLens** to convert raw transactional data into an interactive intelligence cockpit that isolates root causes, models delivery friction, and translates findings into actionable product and operational interventions.

---

## 2. The Analytical Approach & Architecture

### 2.1 The Data Architecture
```text
Raw CSVs (9 Relational Tables)
       │
       ▼
DuckDB In-Process Engine (High-Performance Analytical DB)
       │
       ├── Deduplication & Data Integrity Layer (1 review per order, strict date validation)
       ├── Fact Table (fact_orders: 1 row per order transaction)
       └── Fact Items Table (fact_order_items: line items with seller dispatch compliance)
       │
       ▼
Metrics & Analytics Service Layer (Parameterized SQL)
       │
       ▼
Streamlit Interactive Dashboard (Executive, Regional, Seller, CX, Cancellations, Drilldown)
```

### 2.2 Analytical Rigor & Edge Cases Solved
1. **Preventing Review Fan-Out:** 551 orders contained multiple review entries. A naive SQL `JOIN` would have duplicated transactions and inflated GMV. I engineered a window function (`ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC)`) to deduplicate reviews.
2. **Mutual Exclusivity of Fulfillment Status:** Enforced that orders must be valid delivered orders (`order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL`) before calculating transit days or late flags.
3. **Decoupling Dispatch vs. Transit Delay:** Distinguished between seller fulfillment latency (`order_delivered_carrier_date > shipping_limit_date`) and courier logistics transit time (`order_delivered_customer_date - order_delivered_carrier_date`).

---

## 3. Key Empirical Discoveries from the Data

### 1. The Regional Disparity Problem
* Customers in the **Southeast (SP, RJ, MG, ES)** experience an average transit time of **10.8 days** with a **7.45% late rate** and **R$ 19.84** average freight.
* In contrast, customers in the **Northeast** wait **20.0 days**, suffer a **14.33% late rate**, and pay **R$ 35.99** in freight.
* *Takeaway:* Logistics infrastructure in Brazil is heavily concentrated in the Southeast, creating geographic disparities in customer experience.

### 2. The Satisfaction Cliff
* On-time or early deliveries maintain strong CSAT (**4.14★ to 4.31★**), with 1-star reviews below 10%.
* Delays of 1–3 days cause average ratings to drop sharply to **2.57★**, with 1-star reviews jumping to **35.4%**.
* Delays exceeding 7 days result in an average rating of **1.64★**, with **68.2%** of customers leaving 1-star reviews.
* *Takeaway:* Customer patience has a hard threshold. Interventions must occur within the first 48–72 hours of delay.

### 3. Seller Dispatch Breach vs. Courier Delays
* In **28.39% of late order items**, the seller breached their contractual shipping deadline before the courier received the package.
* *Takeaway:* Logistics delays are not solely a courier problem; more than a quarter of late deliveries stem from merchant warehouse delays.

### 4. Cancellation Timing
* **88.0% of order cancellations** occur *prior* to carrier handoff.
* *Takeaway:* Cancellations reflect inventory stockouts and merchant inactivity rather than in-transit transit friction.

---

## 4. Product Recommendations & Business Impact

1. **Dynamic Regional SLA Buffering:** Implement a location-aware delivery promise algorithm that adds +3 to +5 business days to Northeast/North delivery estimates at checkout. This will set realistic expectations, reduce perceived late deliveries from 14.3% to <6%, and protect regional review scores.
2. **Merchant Dispatch SLA Enforcement:** Introduce a "Fast Shipper" badge and penalize sellers with late handoff rates >20% by demoting them in search results, directly addressing ~28% of late delivery causes.
3. **Automated Proactive Delay Recovery:** Trigger proactive SMS/WhatsApp updates and an automatic R$ 15 discount voucher when an order passes its estimated date, aiming to reduce 1-star reviews by 15–20%.
4. **Northeast Micro-Fulfillment Hubs:** Partner with 3PL fulfillment centers in Recife or Salvador for top-selling SKUs to reduce transit times from 20 days to <6 days.

---

## 5. What I Learned & Demonstrated

* **Product Strategy:** Defined problem statements, user personas, jobs-to-be-done, and prioritizations using the MoSCoW framework.
* **SQL & Data Modeling:** Formulated dimensional models, analytical marts, window functions, and guarded against multi-table join fan-outs.
* **Full-Stack Prototyping:** Built a production-grade Streamlit analytical application powered by DuckDB, with interactive Plotly visualizations and CSV export capabilities.
* **Data-to-Action Translation:** Translated raw transactional numbers into concrete business actions with quantified impact estimates.
