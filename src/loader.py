"""
DuckDB Ingestion Pipeline for DeliveryLens.
Loads raw Olist CSVs into typed DuckDB tables and builds analytical marts.
"""

import os
import sys
import duckdb

BASE_DIR = r"C:\Users\csarg\.gemini\antigravity\scratch\deliverylens".replace("\\", "/")
RAW_DIR = f"{BASE_DIR}/data/raw"
DB_PATH = f"{BASE_DIR}/data/processed/deliverylens.duckdb"

def run_ingestion():
    os.makedirs(f"{BASE_DIR}/data/processed", exist_ok=True)
    
    # Remove existing db file if any to ensure clean rebuild
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception as e:
            print(f"Notice: {e}")

    print(f"Connecting to DuckDB at: {DB_PATH}")
    con = duckdb.connect(DB_PATH)

    print("\n--- 1. Ingesting Raw Tables with Inferred & Validated Schemas ---")
    
    # 1. Orders
    con.execute(f"""
        CREATE TABLE raw_orders AS 
        SELECT 
            order_id::VARCHAR AS order_id,
            customer_id::VARCHAR AS customer_id,
            order_status::VARCHAR AS order_status,
            order_purchase_timestamp::TIMESTAMP AS order_purchase_timestamp,
            order_approved_at::TIMESTAMP AS order_approved_at,
            order_delivered_carrier_date::TIMESTAMP AS order_delivered_carrier_date,
            order_delivered_customer_date::TIMESTAMP AS order_delivered_customer_date,
            order_estimated_delivery_date::TIMESTAMP AS order_estimated_delivery_date
        FROM read_csv_auto('{RAW_DIR}/olist_orders_dataset.csv');
    """)
    print("Created raw_orders")

    # 2. Customers
    con.execute(f"""
        CREATE TABLE raw_customers AS 
        SELECT 
            customer_id::VARCHAR AS customer_id,
            customer_unique_id::VARCHAR AS customer_unique_id,
            customer_zip_code_prefix::VARCHAR AS customer_zip_code_prefix,
            customer_city::VARCHAR AS customer_city,
            UPPER(customer_state)::VARCHAR AS customer_state
        FROM read_csv_auto('{RAW_DIR}/olist_customers_dataset.csv');
    """)
    print("Created raw_customers")

    # 3. Order Items
    con.execute(f"""
        CREATE TABLE raw_order_items AS 
        SELECT 
            order_id::VARCHAR AS order_id,
            order_item_id::INTEGER AS order_item_id,
            product_id::VARCHAR AS product_id,
            seller_id::VARCHAR AS seller_id,
            shipping_limit_date::TIMESTAMP AS shipping_limit_date,
            price::DOUBLE AS price,
            freight_value::DOUBLE AS freight_value
        FROM read_csv_auto('{RAW_DIR}/olist_order_items_dataset.csv');
    """)
    print("Created raw_order_items")

    # 4. Order Payments
    con.execute(f"""
        CREATE TABLE raw_order_payments AS 
        SELECT 
            order_id::VARCHAR AS order_id,
            payment_sequential::INTEGER AS payment_sequential,
            payment_type::VARCHAR AS payment_type,
            payment_installments::INTEGER AS payment_installments,
            payment_value::DOUBLE AS payment_value
        FROM read_csv_auto('{RAW_DIR}/olist_order_payments_dataset.csv');
    """)
    print("Created raw_order_payments")

    # 5. Order Reviews (Handling duplicates by ranking on review_answer_timestamp DESC)
    con.execute(f"""
        CREATE TABLE raw_order_reviews AS 
        SELECT 
            review_id::VARCHAR AS review_id,
            order_id::VARCHAR AS order_id,
            review_score::INTEGER AS review_score,
            review_comment_title::VARCHAR AS review_comment_title,
            review_comment_message::VARCHAR AS review_comment_message,
            review_creation_date::TIMESTAMP AS review_creation_date,
            review_answer_timestamp::TIMESTAMP AS review_answer_timestamp
        FROM read_csv_auto('{RAW_DIR}/olist_order_reviews_dataset.csv');
    """)
    print("Created raw_order_reviews")

    # 6. Sellers
    con.execute(f"""
        CREATE TABLE raw_sellers AS 
        SELECT 
            seller_id::VARCHAR AS seller_id,
            seller_zip_code_prefix::VARCHAR AS seller_zip_code_prefix,
            seller_city::VARCHAR AS seller_city,
            UPPER(seller_state)::VARCHAR AS seller_state
        FROM read_csv_auto('{RAW_DIR}/olist_sellers_dataset.csv');
    """)
    print("Created raw_sellers")

    # 7. Products
    con.execute(f"""
        CREATE TABLE raw_products AS 
        SELECT 
            product_id::VARCHAR AS product_id,
            product_category_name::VARCHAR AS product_category_name,
            product_name_lenght::INTEGER AS product_name_length,
            product_description_lenght::INTEGER AS product_description_length,
            product_photos_qty::INTEGER AS product_photos_qty,
            product_weight_g::DOUBLE AS product_weight_g,
            product_length_cm::DOUBLE AS product_length_cm,
            product_height_cm::DOUBLE AS product_height_cm,
            product_width_cm::DOUBLE AS product_width_cm
        FROM read_csv_auto('{RAW_DIR}/olist_products_dataset.csv');
    """)
    print("Created raw_products")

    # 8. Category Translations
    con.execute(f"""
        CREATE TABLE raw_category_translation AS 
        SELECT 
            product_category_name::VARCHAR AS product_category_name,
            product_category_name_english::VARCHAR AS product_category_name_english
        FROM read_csv_auto('{RAW_DIR}/product_category_name_translation.csv');
    """)
    print("Created raw_category_translation")

    print("\n--- 2. Building Analytics Mart: Deduplicated Reviews & Order Items Aggregations ---")
    
    # Deduplicate reviews to 1 review per order_id (taking the most recent answer timestamp)
    con.execute("""
        CREATE TABLE mart_order_reviews_deduped AS
        SELECT 
            review_id,
            order_id,
            review_score,
            review_comment_title,
            review_comment_message,
            review_creation_date,
            review_answer_timestamp
        FROM (
            SELECT 
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY order_id 
                    ORDER BY review_answer_timestamp DESC, review_id DESC
                ) as rn
            FROM raw_order_reviews
        )
        WHERE rn = 1;
    """)
    print("Created mart_order_reviews_deduped")

    # Order financial aggregates (grain: order_id)
    con.execute("""
        CREATE TABLE mart_order_financials AS
        SELECT 
            order_id,
            COUNT(order_item_id) AS total_items,
            COUNT(DISTINCT seller_id) AS distinct_sellers,
            ROUND(SUM(price), 2) AS total_items_value,
            ROUND(SUM(freight_value), 2) AS total_freight_value,
            ROUND(SUM(price + freight_value), 2) AS total_order_value,
            MIN(shipping_limit_date) AS min_shipping_limit_date,
            MAX(shipping_limit_date) AS max_shipping_limit_date
        FROM raw_order_items
        GROUP BY order_id;
    """)
    print("Created mart_order_financials")

    print("\n--- 3. Building Core Analytical Fact Table: fact_orders ---")
    # Mapping Brazilian States to Official Macro-Regions:
    # SE (Southeast): SP, RJ, MG, ES
    # S (South): PR, SC, RS
    # NE (Northeast): BA, PE, CE, MA, PB, RN, AL, PI, SE
    # CW (Central-West): GO, MT, MS, DF
    # N (North): AM, PA, RO, TO, AC, AP, RR
    con.execute("""
        CREATE TABLE fact_orders AS
        SELECT 
            o.order_id,
            o.customer_id,
            c.customer_unique_id,
            o.order_status,
            o.order_purchase_timestamp,
            o.order_approved_at,
            o.order_delivered_carrier_date,
            o.order_delivered_customer_date,
            o.order_estimated_delivery_date,
            
            -- Date parts
            CAST(o.order_purchase_timestamp AS DATE) AS purchase_date,
            STRFTIME(o.order_purchase_timestamp, '%Y-%m') AS purchase_year_month,
            
            -- Customer geography
            c.customer_city,
            c.customer_state,
            CASE 
                WHEN c.customer_state IN ('SP', 'RJ', 'MG', 'ES') THEN 'Southeast'
                WHEN c.customer_state IN ('PR', 'SC', 'RS') THEN 'South'
                WHEN c.customer_state IN ('BA', 'PE', 'CE', 'MA', 'PB', 'RN', 'AL', 'PI', 'SE') THEN 'Northeast'
                WHEN c.customer_state IN ('GO', 'MT', 'MS', 'DF') THEN 'Central-West'
                WHEN c.customer_state IN ('AM', 'PA', 'RO', 'TO', 'AC', 'AP', 'RR') THEN 'North'
                ELSE 'Other'
            END AS customer_macro_region,
            
            -- Operational flags
            CASE WHEN o.order_status = 'delivered' THEN 1 ELSE 0 END AS is_delivered,
            CASE WHEN o.order_status = 'canceled' THEN 1 ELSE 0 END AS is_canceled,
            CASE 
                WHEN o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL 
                     AND o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 
                ELSE 0 
            END AS is_late,
            CASE 
                WHEN o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL 
                     AND o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 1 
                ELSE 0 
            END AS is_on_time,
            
            -- Duration metrics (in decimal days)
            CASE 
                WHEN o.order_delivered_customer_date IS NOT NULL 
                THEN ROUND(DATE_DIFF('second', o.order_purchase_timestamp, o.order_delivered_customer_date) / 86400.0, 2)
                ELSE NULL 
            END AS actual_delivery_days,
            
            ROUND(DATE_DIFF('second', o.order_purchase_timestamp, o.order_estimated_delivery_date) / 86400.0, 2) AS estimated_delivery_days,
            
            -- Delay vs Promised Date (Positive means late, negative means arrived early)
            CASE 
                WHEN o.order_delivered_customer_date IS NOT NULL 
                THEN ROUND(DATE_DIFF('second', o.order_estimated_delivery_date, o.order_delivered_customer_date) / 86400.0, 2)
                ELSE NULL 
            END AS delay_days,
            
            -- Seller to carrier transit time (dispatch time)
            CASE 
                WHEN o.order_delivered_carrier_date IS NOT NULL 
                THEN ROUND(DATE_DIFF('second', o.order_purchase_timestamp, o.order_delivered_carrier_date) / 86400.0, 2)
                ELSE NULL 
            END AS carrier_dispatch_days,
            
            -- Carrier transit time
            CASE 
                WHEN o.order_delivered_customer_date IS NOT NULL AND o.order_delivered_carrier_date IS NOT NULL
                THEN ROUND(DATE_DIFF('second', o.order_delivered_carrier_date, o.order_delivered_customer_date) / 86400.0, 2)
                ELSE NULL 
            END AS carrier_transit_days,
            
            -- Review data
            r.review_id,
            r.review_score,
            r.review_comment_title,
            r.review_comment_message,
            
            -- Financial data
            COALESCE(f.total_items, 0) AS total_items,
            COALESCE(f.distinct_sellers, 0) AS distinct_sellers,
            COALESCE(f.total_items_value, 0.0) AS total_items_value,
            COALESCE(f.total_freight_value, 0.0) AS total_freight_value,
            COALESCE(f.total_order_value, 0.0) AS total_order_value
            
        FROM raw_orders o
        LEFT JOIN raw_customers c ON o.customer_id = c.customer_id
        LEFT JOIN mart_order_reviews_deduped r ON o.order_id = r.order_id
        LEFT JOIN mart_order_financials f ON o.order_id = f.order_id;
    """)
    print("Created fact_orders")

    print("\n--- 4. Building Item-Level Fact Table: fact_order_items ---")
    con.execute("""
        CREATE TABLE fact_order_items AS
        SELECT 
            oi.order_id,
            oi.order_item_id,
            oi.product_id,
            oi.seller_id,
            oi.shipping_limit_date,
            oi.price,
            oi.freight_value,
            
            -- Product details with English categories
            p.product_category_name,
            COALESCE(t.product_category_name_english, p.product_category_name, 'Unknown') AS product_category_name_english,
            p.product_weight_g,
            p.product_length_cm,
            p.product_height_cm,
            p.product_width_cm,
            
            -- Seller details
            s.seller_city,
            s.seller_state,
            CASE 
                WHEN s.seller_state IN ('SP', 'RJ', 'MG', 'ES') THEN 'Southeast'
                WHEN s.seller_state IN ('PR', 'SC', 'RS') THEN 'South'
                WHEN s.seller_state IN ('BA', 'PE', 'CE', 'MA', 'PB', 'RN', 'AL', 'PI', 'SE') THEN 'Northeast'
                WHEN s.seller_state IN ('GO', 'MT', 'MS', 'DF') THEN 'Central-West'
                WHEN s.seller_state IN ('AM', 'PA', 'RO', 'TO', 'AC', 'AP', 'RR') THEN 'North'
                ELSE 'Other'
            END AS seller_macro_region,
            
            -- Order & Customer link for cross-region comparison
            fo.customer_state,
            fo.customer_macro_region,
            fo.order_purchase_timestamp,
            fo.order_delivered_carrier_date,
            fo.order_delivered_customer_date,
            fo.order_estimated_delivery_date,
            fo.order_status,
            fo.is_delivered,
            fo.is_late,
            fo.delay_days,
            fo.review_score,
            
            -- Same-state fulfillment flag
            CASE WHEN s.seller_state = fo.customer_state THEN 1 ELSE 0 END AS is_intra_state_order,
            
            -- Seller shipping dispatch compliance
            CASE 
                WHEN fo.order_delivered_carrier_date IS NOT NULL 
                     AND fo.order_delivered_carrier_date > oi.shipping_limit_date THEN 1 
                ELSE 0 
            END AS is_carrier_handoff_late
            
        FROM raw_order_items oi
        LEFT JOIN raw_products p ON oi.product_id = p.product_id
        LEFT JOIN raw_category_translation t ON p.product_category_name = t.product_category_name
        LEFT JOIN raw_sellers s ON oi.seller_id = s.seller_id
        LEFT JOIN fact_orders fo ON oi.order_id = fo.order_id;
    """)
    print("Created fact_order_items")

    # Create Indexes for lightning-fast queries
    print("\n--- 5. Creating Performance Indexes ---")
    con.execute("CREATE INDEX idx_fact_orders_id ON fact_orders(order_id);")
    con.execute("CREATE INDEX idx_fact_orders_date ON fact_orders(purchase_date);")
    con.execute("CREATE INDEX idx_fact_orders_state ON fact_orders(customer_state);")
    con.execute("CREATE INDEX idx_fact_items_seller ON fact_order_items(seller_id);")

    # Validation summary
    total_orders = con.execute("SELECT COUNT(*) FROM fact_orders").fetchone()[0]
    total_delivered = con.execute("SELECT COUNT(*) FROM fact_orders WHERE is_delivered = 1").fetchone()[0]
    total_late = con.execute("SELECT COUNT(*) FROM fact_orders WHERE is_late = 1").fetchone()[0]
    late_rate = (total_late / total_delivered) * 100
    avg_review = con.execute("SELECT ROUND(AVG(review_score), 2) FROM fact_orders WHERE review_score IS NOT NULL").fetchone()[0]
    
    print(f"\n================ INGESTION COMPLETE ================")
    print(f"Total Fact Orders: {total_orders:,}")
    print(f"Delivered Orders: {total_delivered:,}")
    print(f"Late Deliveries: {total_late:,} ({late_rate:.2f}%)")
    print(f"Average Review Score: {avg_review} / 5.0")
    print(f"Database successfully saved to: {DB_PATH}")
    con.close()

if __name__ == "__main__":
    run_ingestion()

