-- Delivery Performance by Customer State and Macro-Region
SELECT 
    customer_macro_region,
    customer_state,
    COUNT(*) AS total_orders,
    SUM(is_delivered) AS delivered_orders,
    SUM(is_late) AS late_orders,
    ROUND(SUM(is_late) * 100.0 / NULLIF(SUM(is_delivered), 0), 2) AS late_delivery_rate_pct,
    ROUND(AVG(CASE WHEN is_delivered = 1 THEN actual_delivery_days END), 2) AS avg_delivery_time_days,
    ROUND(AVG(estimated_delivery_days), 2) AS avg_estimated_days,
    ROUND(AVG(CASE WHEN is_late = 1 THEN delay_days END), 2) AS avg_delay_days,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(AVG(total_freight_value), 2) AS avg_freight_cost
FROM fact_orders
GROUP BY customer_macro_region, customer_state
ORDER BY late_delivery_rate_pct DESC;
