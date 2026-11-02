-- Monthly Order Volume, Delivery Performance, and CX Trends
-- Filters out sparse edge months (e.g., 2016 pilot test) where relevant
SELECT 
    purchase_year_month,
    COUNT(*) AS total_orders,
    SUM(is_delivered) AS delivered_orders,
    SUM(is_late) AS late_orders,
    ROUND(SUM(is_late) * 100.0 / NULLIF(SUM(is_delivered), 0), 2) AS late_delivery_rate_pct,
    ROUND(AVG(CASE WHEN is_late = 1 THEN delay_days END), 2) AS avg_delay_days,
    ROUND(AVG(CASE WHEN is_delivered = 1 THEN actual_delivery_days END), 2) AS avg_actual_delivery_days,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    SUM(is_canceled) AS canceled_orders,
    ROUND(SUM(total_order_value), 2) AS monthly_gmv_brl
FROM fact_orders
WHERE purchase_year_month >= '2017-01' AND purchase_year_month <= '2018-08'
GROUP BY purchase_year_month
ORDER BY purchase_year_month ASC;

