-- Seller Performance & Fulfillment Compliance Analysis
-- Aggregates orders and item-level dispatch compliance by seller
SELECT 
    oi.seller_id,
    s.seller_city,
    s.seller_state,
    s.seller_macro_region,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(oi.order_item_id) AS total_items_sold,
    ROUND(SUM(oi.price), 2) AS total_sales_volume,
    SUM(oi.is_delivered) AS delivered_items,
    SUM(oi.is_late) AS late_delivery_items,
    ROUND(SUM(oi.is_late) * 100.0 / NULLIF(SUM(oi.is_delivered), 0), 2) AS late_delivery_rate_pct,
    SUM(oi.is_carrier_handoff_late) AS late_carrier_handoff_items,
    ROUND(SUM(oi.is_carrier_handoff_late) * 100.0 / NULLIF(COUNT(oi.order_item_id), 0), 2) AS late_handoff_rate_pct,
    ROUND(AVG(oi.review_score), 2) AS avg_review_score,
    ROUND(AVG(oi.freight_value), 2) AS avg_freight_value
FROM fact_order_items oi
JOIN raw_sellers s ON oi.seller_id = s.seller_id
GROUP BY oi.seller_id, s.seller_city, s.seller_state, s.seller_macro_region
HAVING COUNT(DISTINCT oi.order_id) >= 30 -- Statistically relevant sample
ORDER BY late_delivery_rate_pct DESC;

