# DeliveryLens: KPI Specifications & Formula Reference 📐

This document establishes the official definitions, mathematical equations, edge-case handling rules, and SQL logic for all metrics within DeliveryLens.

---

## 1. Primary Operational & Delivery KPIs

### 1.1 Late Delivery Rate (%)
* **Business Objective:** Measure the proportion of completed customer deliveries that failed to meet the promised delivery date.
* **Formula:**
  $$\text{Late Delivery Rate (\%)} = \frac{\text{Delivered Orders where } (\text{Actual Delivery Date} > \text{Estimated Delivery Date})}{\text{Total Valid Delivered Orders}} \times 100$$
* **Edge Cases & Rules:**
  - Evaluated **strictly** on orders where `order_status = 'delivered'` AND `order_delivered_customer_date IS NOT NULL`.
  - Non-delivered orders (e.g. `shipped`, `processing`, `canceled`) are **excluded** from this denominator to prevent false deflations.
* **SQL Implementation:**
  ```sql
  ROUND(
      SUM(CASE WHEN order_status = 'delivered' 
                    AND order_delivered_customer_date IS NOT NULL 
                    AND order_delivered_customer_date > order_estimated_delivery_date 
               THEN 1 ELSE 0 END) * 100.0 /
      NULLIF(SUM(CASE WHEN order_status = 'delivered' 
                           AND order_delivered_customer_date IS NOT NULL 
                      THEN 1 ELSE 0 END), 0),
      2
  ) AS late_delivery_rate_pct
  ```

---

### 1.2 Average Delivery Delay (Days)
* **Business Objective:** Measure the average severity (magnitude) of delivery delays for late shipments.
* **Formula:**
  $$\text{Avg Delay (Late Orders)} = \frac{1}{N_{\text{late}}} \sum_{i \in \text{late}} (\text{Actual Delivery Date}_i - \text{Estimated Delivery Date}_i)$$
* **Edge Cases & Rules:**
  - Calculated **only** across orders that are late (`delay_days > 0`). 
  - On-time orders arriving early (negative delay days) are excluded from this metric so early arrivals do not artificially dilute the visible severity of late orders.
* **SQL Implementation:**
  ```sql
  ROUND(
      AVG(CASE WHEN is_late = 1 THEN delay_days END),
      2
  ) AS avg_delay_days_late
  ```

---

### 1.3 Average Doorstep Transit Time (Days)
* **Business Objective:** Measure the total duration elapsed between order placement and physical doorstep delivery.
* **Formula:**
  $$\text{Avg Transit Time} = \frac{1}{N_{\text{valid delivered}}} \sum (\text{Actual Delivery Date} - \text{Order Purchase Date})$$
* **SQL Implementation:**
  ```sql
  ROUND(
      AVG(CASE WHEN is_delivered = 1 AND order_delivered_customer_date IS NOT NULL 
               THEN DATE_DIFF('second', order_purchase_timestamp, order_delivered_customer_date) / 86400.0 
          END),
      2
  ) AS avg_transit_days
  ```

---

### 1.4 Seller Dispatch Breach Rate (Late Carrier Handoff %)
* **Business Objective:** Isolate merchant fulfillment delay from logistics courier transit delay.
* **Definition:** Percentage of order items where the seller handed the package to the courier after the contractual `shipping_limit_date`.
* **SQL Implementation:**
  ```sql
  ROUND(
      SUM(CASE WHEN order_delivered_carrier_date > shipping_limit_date THEN 1 ELSE 0 END) * 100.0 /
      NULLIF(COUNT(*), 0),
      2
  ) AS late_handoff_rate_pct
  ```

---

## 2. Customer Experience (CX) KPIs

### 2.1 Average Review Score (CSAT)
* **Business Objective:** Track overall customer sentiment on a 1.00 to 5.00 star scale.
* **Rule:** Uses deduplicated reviews to ensure 1 review weight per order transaction.
* **SQL Implementation:**
  ```sql
  ROUND(AVG(review_score), 2) AS avg_review_score
  ```

### 2.2 1-Star Negative Rating Concentration (%)
* **Business Objective:** Quantify severe customer dissatisfaction triggered by operational failures.
* **Formula:**
  $$\% \text{ 1-Star Reviews} = \frac{\text{Count of Orders with Review Score} = 1}{\text{Total Reviewed Orders}} \times 100$$

---

## 3. Order Quality & Cancellation KPIs

### 3.1 Order Cancellation Rate (%)
* **Formula:**
  $$\text{Cancellation Rate (\%)} = \frac{\text{Count of Orders where } \text{order\_status} = \text{'canceled'}}{\text{Total Orders Recorded}} \times 100$$
* **Stage Decomposition:**
  - **Pre-Dispatch Cancellations:** Canceled when `order_delivered_carrier_date IS NULL` (inventory stockouts, merchant unresponsive).
  - **In-Transit Cancellations:** Canceled when `order_delivered_carrier_date IS NOT NULL` (package lost, damaged, severe transit delay).
