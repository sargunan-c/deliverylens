-- Executive Dashboard KPIs
-- Grain: High-level executive aggregates with safe handling of nulls and cancelled orders
SELECT 
    COUNT(*) AS total_orders,
    SUM(is_delivered) AS delivered_orders,
    SUM(is_late) AS late_orders,
    ROUND(SUM(is_late) * 100.0 / NULLIF(SUM(is_delivered), 0), 2) AS late_delivery_rate_pct,
    ROUND(AVG(CASE WHEN is_late = 1 THEN delay_days END), 2) AS avg_delay_days_late_orders,
    ROUND(AVG(CASE WHEN is_delivered = 1 THEN actual_delivery_days END), 2) AS avg_transit_time_days,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    SUM(is_canceled) AS canceled_orders,
    ROUND(SUM(is_canceled) * 100.0 / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
    ROUND(SUM(total_order_value), 2) AS total_gmv_brl,
    ROUND(AVG(total_freight_value), 2) AS avg_freight_per_order
FROM fact_orders;
