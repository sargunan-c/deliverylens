-- Order Cancellation Analysis
-- Investigates cancellations by month, customer macro-region, and handoff stage
SELECT 
    customer_macro_region,
    COUNT(*) AS total_orders,
    SUM(is_canceled) AS canceled_orders,
    ROUND(SUM(is_canceled) * 100.0 / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
    COUNT(CASE WHEN is_canceled = 1 AND order_delivered_carrier_date IS NOT NULL THEN 1 END) AS canceled_after_carrier_handoff,
    COUNT(CASE WHEN is_canceled = 1 AND order_delivered_carrier_date IS NULL THEN 1 END) AS canceled_before_carrier_handoff,
    ROUND(AVG(CASE WHEN is_canceled = 1 THEN total_order_value END), 2) AS avg_canceled_order_value
FROM fact_orders
GROUP BY customer_macro_region
ORDER BY cancellation_rate_pct DESC;
