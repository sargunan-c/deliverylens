-- Correlation between Delivery Delay and Customer Review Score
-- Grouped by review score rating (1 to 5)
SELECT 
    review_score,
    COUNT(*) AS total_reviews,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_of_reviews,
    SUM(is_late) AS late_orders,
    ROUND(SUM(is_late) * 100.0 / NULLIF(SUM(is_delivered), 0), 2) AS late_delivery_rate_pct,
    ROUND(AVG(CASE WHEN is_delivered = 1 THEN actual_delivery_days END), 2) AS avg_delivery_time_days,
    ROUND(AVG(CASE WHEN is_late = 1 THEN delay_days END), 2) AS avg_delay_days_when_late,
    ROUND(AVG(delay_days), 2) AS avg_days_diff_from_estimate
FROM fact_orders
WHERE review_score IS NOT NULL AND is_delivered = 1
GROUP BY review_score
ORDER BY review_score ASC;
