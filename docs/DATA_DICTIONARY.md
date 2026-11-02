# DeliveryLens: Enterprise Data Dictionary & Data Model 📖

## 1. Executive Summary & Relational Model
DeliveryLens models the Brazilian Olist E-commerce ecosystem. The operational data model transforms 9 raw normalized relational tables into high-performance analytical marts optimized for DuckDB querying.

### Entity Relationship Diagram (ERD) & Table Cardinality

```text
       [raw_customers] (99,441 rows)
              | 1:1
       [raw_orders] (99,441 rows) <-------- [raw_order_reviews] (99,224 rows)
              |                                (551 duplicate order reviews)
              | 1:N
       [raw_order_items] (112,650 rows)
        /           \
     N:1             N:1
 [raw_sellers]    [raw_products] (32,951 rows)
  (3,095 rows)          |
                       N:1
                  [raw_category_translation] (71 rows)
```

---

## 2. Table-by-Table Specifications & Grains

### Table: `fact_orders`
* **Grain:** 1 row per customer order transaction (`order_id`).
* **Source:** Derived from `raw_orders` left joined with `raw_customers`, deduplicated `mart_order_reviews_deduped`, and `mart_order_financials`.
* **Primary Key:** `order_id` (Unique, 0 nulls).

| Column Name | Data Type | Nullable | Description & Business Rules |
|---|---|---|---|
| `order_id` | VARCHAR | No | Unique alphanumeric order identifier. |
| `customer_id` | VARCHAR | No | Transaction-level customer token (1-to-1 with order). |
| `customer_unique_id` | VARCHAR | No | Persistent customer identity across multiple purchases. |
| `order_status` | VARCHAR | No | Fulfillment status (`delivered`, `shipped`, `canceled`, etc.). |
| `order_purchase_timestamp` | TIMESTAMP | No | Timestamp of order creation by customer. |
| `order_approved_at` | TIMESTAMP | Yes | Timestamp of payment gateway approval (160 nulls). |
| `order_delivered_carrier_date` | TIMESTAMP | Yes | Timestamp when seller handed the package to courier (1,783 nulls). |
| `order_delivered_customer_date` | TIMESTAMP | Yes | Timestamp when courier delivered package to customer doorstep (2,965 nulls across all statuses; 8 nulls on delivered status). |
| `order_estimated_delivery_date` | TIMESTAMP | No | Promised delivery date provided to customer during checkout. |
| `purchase_date` | DATE | No | Date part of `order_purchase_timestamp`. |
| `purchase_year_month` | VARCHAR | No | String formatted as `YYYY-MM` for monthly trend aggregation. |
| `customer_city` | VARCHAR | No | City of customer delivery destination. |
| `customer_state` | VARCHAR | No | 2-letter state code of delivery destination (27 Brazilian states). |
| `customer_macro_region` | VARCHAR | No | Standard Brazilian geopolitical macro-region (`Southeast`, `South`, `Northeast`, `Central-West`, `North`). |
| `is_delivered` | INTEGER | No | Flag: 1 if `order_status = 'delivered'`, else 0. |
| `is_canceled` | INTEGER | No | Flag: 1 if `order_status = 'canceled'`, else 0. |
| `is_late` | INTEGER | No | Flag: 1 if delivered and `order_delivered_customer_date > order_estimated_delivery_date`, else 0. |
| `is_on_time` | INTEGER | No | Flag: 1 if delivered and `order_delivered_customer_date <= order_estimated_delivery_date`, else 0. |
| `actual_delivery_days` | DOUBLE | Yes | Total elapsed days from purchase to doorstep delivery. |
| `estimated_delivery_days` | DOUBLE | No | Total expected days between purchase and promised delivery date. |
| `delay_days` | DOUBLE | Yes | Days between estimated delivery and actual delivery (`actual - estimated`). Positive indicates delay; negative indicates early arrival. |
| `carrier_dispatch_days` | DOUBLE | Yes | Days from purchase to courier pick-up/handoff. |
| `carrier_transit_days` | DOUBLE | Yes | Days in transit with courier (`delivered_customer - delivered_carrier`). |
| `review_score` | INTEGER | Yes | Customer satisfaction rating (1 to 5 stars). Deduplicated. |
| `total_items` | INTEGER | No | Total count of product items in the order. |
| `distinct_sellers` | INTEGER | No | Count of unique sellers fulfilling items in this order. |
| `total_items_value` | DOUBLE | No | Sum of item prices in BRL (R$). |
| `total_freight_value` | DOUBLE | No | Sum of item shipping costs in BRL (R$). |
| `total_order_value` | DOUBLE | No | Total transaction value (`items_value + freight_value`). |

---

### Table: `fact_order_items`
* **Grain:** 1 row per order item (`order_id` + `order_item_id`).
* **Source:** `raw_order_items` enriched with `raw_products`, `raw_sellers`, `raw_category_translation`, and `fact_orders`.

| Column Name | Data Type | Nullable | Description & Business Rules |
|---|---|---|---|
| `order_id` | VARCHAR | No | Foreign key linking to `fact_orders.order_id`. |
| `order_item_id` | INTEGER | No | Sequential line-item sequence number within the order (1, 2, 3...). |
| `product_id` | VARCHAR | No | Foreign key linking to product catalog. |
| `seller_id` | VARCHAR | No | Foreign key linking to merchant. |
| `shipping_limit_date` | TIMESTAMP | No | Seller SLA deadline to hand off item to the carrier. |
| `price` | DOUBLE | No | Item selling price in BRL. |
| `freight_value` | DOUBLE | No | Allocated shipping fee for this item in BRL. |
| `product_category_name_english` | VARCHAR | No | Translated English product category (e.g. `bed_bath_table`, `health_beauty`). |
| `seller_city` | VARCHAR | No | Merchant warehouse city. |
| `seller_state` | VARCHAR | No | Merchant warehouse 2-letter state code. |
| `seller_macro_region` | VARCHAR | No | Merchant geographic macro-region. |
| `is_intra_state_order` | INTEGER | No | 1 if `seller_state == customer_state`, else 0 (inter-state logistics). |
| `is_carrier_handoff_late` | INTEGER | No | 1 if `order_delivered_carrier_date > shipping_limit_date` (seller SLA breach). |

---

## 3. Data Integrity & Join Pitfalls Resolved
1. **Review Duplication (Fan-Out Pitfall):** 551 orders in Olist have more than one review entry. Joining `orders` directly to `reviews` produces 99,992 rows instead of 99,441, inflating order volumes and double-counting revenue. DeliveryLens deduplicates `raw_order_reviews` by keeping the latest review per order (`ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC)`).
2. **Missing Dates on Delivered Orders:** 8 orders marked `delivered` had null customer delivery timestamps. DeliveryLens excludes these 8 records from transit time and delay calculations to prevent silent division-by-zero or skewed distributions.
3. **Item Aggregation Before Join:** Order items and payments are pre-aggregated at the `order_id` grain prior to joining with `fact_orders`.

