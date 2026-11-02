"""
Relationship, Cardinality, and Grain Validator.
Examines primary/foreign keys, joins, fan-outs, and delivery date nullability.
"""

import duckdb
import json

DATA_DIR = r"C:\Users\csarg\.gemini\antigravity\scratch\deliverylens\data\raw".replace("\\", "/")

con = duckdb.connect()

print("--- 1. Checking Key Uniqueness & Cardinality ---")
# Orders
res = con.execute(f"""
    SELECT 
        COUNT(*) as total_rows,
        COUNT(DISTINCT order_id) as distinct_orders,
        COUNT(DISTINCT customer_id) as distinct_customers
    FROM read_csv_auto('{DATA_DIR}/olist_orders_dataset.csv')
""").df()
print("Orders:", res.to_dict(orient="records")[0])

# Order status distribution
res_status = con.execute(f"""
    SELECT 
        order_status, 
        COUNT(*) as order_count,
        COUNT(order_delivered_customer_date) as delivered_date_not_null,
        COUNT(order_delivered_carrier_date) as carrier_date_not_null
    FROM read_csv_auto('{DATA_DIR}/olist_orders_dataset.csv')
    GROUP BY order_status
    ORDER BY order_count DESC
""").df()
print("\nOrder Status Breakdown:\n", res_status.to_string())

# Reviews duplication per order_id
res_reviews = con.execute(f"""
    SELECT 
        COUNT(*) as total_reviews,
        COUNT(DISTINCT review_id) as distinct_reviews,
        COUNT(DISTINCT order_id) as distinct_orders_with_review,
        COUNT(*) - COUNT(DISTINCT order_id) as duplicate_order_reviews
    FROM read_csv_auto('{DATA_DIR}/olist_order_reviews_dataset.csv')
""").df()
print("\nReviews Cardinality:", res_reviews.to_dict(orient="records")[0])

# Order items cardinality
res_items = con.execute(f"""
    SELECT 
        COUNT(*) as total_items,
        COUNT(DISTINCT order_id) as distinct_orders_in_items,
        COUNT(DISTINCT seller_id) as distinct_sellers_in_items,
        COUNT(DISTINCT product_id) as distinct_products_in_items
    FROM read_csv_auto('{DATA_DIR}/olist_order_items_dataset.csv')
""").df()
print("\nOrder Items Cardinality:", res_items.to_dict(orient="records")[0])

# Customers table
res_cust = con.execute(f"""
    SELECT 
        COUNT(*) as total_rows,
        COUNT(DISTINCT customer_id) as distinct_customer_ids,
        COUNT(DISTINCT customer_unique_id) as distinct_unique_customers
    FROM read_csv_auto('{DATA_DIR}/olist_customers_dataset.csv')
""").df()
print("\nCustomers:", res_cust.to_dict(orient="records")[0])

# On-time vs Late Delivery definition check on delivered orders
res_ontime = con.execute(f"""
    SELECT 
        COUNT(*) as delivered_orders,
        COUNT(CASE WHEN order_delivered_customer_date IS NOT NULL THEN 1 END) as valid_delivered_orders,
        COUNT(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 END) as late_orders,
        COUNT(CASE WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 1 END) as on_time_orders,
        ROUND(AVG(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date 
                       THEN DATE_DIFF('day', order_estimated_delivery_date, order_delivered_customer_date) END), 2) as avg_delay_days_late_only,
        ROUND(AVG(DATE_DIFF('day', order_estimated_delivery_date, order_delivered_customer_date)), 2) as avg_delay_days_all_delivered,
        ROUND(AVG(DATE_DIFF('day', order_purchase_timestamp, order_delivered_customer_date)), 2) as avg_actual_delivery_time_days
    FROM read_csv_auto('{DATA_DIR}/olist_orders_dataset.csv')
    WHERE order_status = 'delivered'
""").df()
print("\nDelivered Orders KPI Check:\n", res_ontime.to_string())
