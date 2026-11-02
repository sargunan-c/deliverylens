"""
Metrics and Analytics Service Layer for DeliveryLens.
Executes parameterized SQL queries against DuckDB based on user filters.
"""

from typing import Dict, Any, Optional
import pandas as pd
from .db import run_query

def build_where_clause(filters: Optional[Dict[str, Any]] = None) -> str:
    """Builds dynamic SQL WHERE clause safely for fact_orders."""
    conditions = ["1=1"]
    if not filters:
        return "WHERE 1=1"
        
    if filters.get("start_date"):
        conditions.append(f"purchase_date >= '{filters['start_date']}'")
    if filters.get("end_date"):
        conditions.append(f"purchase_date <= '{filters['end_date']}'")
    if filters.get("macro_region") and filters["macro_region"] != "All":
        conditions.append(f"customer_macro_region = '{filters['macro_region']}'")
    if filters.get("state") and filters["state"] != "All":
        conditions.append(f"customer_state = '{filters['state']}'")
    if filters.get("order_status") and filters["order_status"] != "All":
        conditions.append(f"order_status = '{filters['order_status']}'")
        
    return "WHERE " + " AND ".join(conditions)

def get_executive_kpis(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Computes high-level executive cards."""
    where = build_where_clause(filters)
    query = f"""
    SELECT 
        COUNT(*) AS total_orders,
        COALESCE(SUM(is_delivered), 0) AS delivered_orders,
        COALESCE(SUM(is_late), 0) AS late_orders,
        COALESCE(ROUND(SUM(is_late) * 100.0 / NULLIF(SUM(is_delivered), 0), 2), 0.0) AS late_delivery_rate_pct,
        COALESCE(ROUND(AVG(CASE WHEN is_late = 1 THEN delay_days END), 2), 0.0) AS avg_delay_days_late,
        COALESCE(ROUND(AVG(CASE WHEN is_delivered = 1 THEN actual_delivery_days END), 2), 0.0) AS avg_transit_days,
        COALESCE(ROUND(AVG(review_score), 2), 0.0) AS avg_review_score,
        COALESCE(SUM(is_canceled), 0) AS canceled_orders,
        COALESCE(ROUND(SUM(is_canceled) * 100.0 / NULLIF(COUNT(*), 0), 2), 0.0) AS cancellation_rate_pct,
        COALESCE(ROUND(SUM(total_order_value), 2), 0.0) AS total_gmv_brl,
        COALESCE(ROUND(AVG(total_freight_value), 2), 0.0) AS avg_freight_value
    FROM fact_orders
    {where};
    """
    df = run_query(query)
    return df.to_dict(orient="records")[0]

def get_monthly_trends(filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """Returns monthly order counts, late rates, and review scores."""
    where = build_where_clause(filters)
    query = f"""
    SELECT 
        purchase_year_month,
        COUNT(*) AS total_orders,
        SUM(is_delivered) AS delivered_orders,
        SUM(is_late) AS late_orders,
        ROUND(SUM(is_late) * 100.0 / NULLIF(SUM(is_delivered), 0), 2) AS late_delivery_rate_pct,
        ROUND(100.0 - (SUM(is_late) * 100.0 / NULLIF(SUM(is_delivered), 0)), 2) AS on_time_rate_pct,
        ROUND(AVG(CASE WHEN is_late = 1 THEN delay_days END), 2) AS avg_delay_days,
        ROUND(AVG(CASE WHEN is_delivered = 1 THEN actual_delivery_days END), 2) AS avg_transit_days,
        ROUND(AVG(review_score), 2) AS avg_review_score,
        SUM(is_canceled) AS canceled_orders,
        ROUND(SUM(total_order_value), 2) AS monthly_gmv_brl
    FROM fact_orders
    {where}
    GROUP BY purchase_year_month
    ORDER BY purchase_year_month ASC;
    """
    return run_query(query)

def get_regional_performance(filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """Returns delivery KPIs grouped by customer macro-region and state."""
    where = build_where_clause(filters)
    query = f"""
    SELECT 
        customer_macro_region,
        customer_state,
        COUNT(*) AS total_orders,
        SUM(is_delivered) AS delivered_orders,
        SUM(is_late) AS late_orders,
        ROUND(SUM(is_late) * 100.0 / NULLIF(SUM(is_delivered), 0), 2) AS late_delivery_rate_pct,
        ROUND(AVG(CASE WHEN is_delivered = 1 THEN actual_delivery_days END), 2) AS avg_transit_days,
        ROUND(AVG(estimated_delivery_days), 2) AS avg_estimated_days,
        ROUND(AVG(CASE WHEN is_late = 1 THEN delay_days END), 2) AS avg_delay_days,
        ROUND(AVG(review_score), 2) AS avg_review_score,
        ROUND(AVG(total_freight_value), 2) AS avg_freight_cost
    FROM fact_orders
    {where}
    GROUP BY customer_macro_region, customer_state
    ORDER BY late_delivery_rate_pct DESC;
    """
    return run_query(query)

def get_delay_buckets_vs_review(filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """Categorizes delivery performance into granular buckets and tracks satisfaction cliff."""
    where = build_where_clause(filters)
    query = f"""
    WITH bucketed AS (
        SELECT 
            review_score,
            CASE 
                WHEN delay_days <= -10 THEN '1. >10 Days Early'
                WHEN delay_days > -10 AND delay_days <= -3 THEN '2. 3-10 Days Early'
                WHEN delay_days > -3 AND delay_days <= 0 THEN '3. On-Time (0-3 Days Early)'
                WHEN delay_days > 0 AND delay_days <= 3 THEN '4. 1-3 Days Late'
                WHEN delay_days > 3 AND delay_days <= 7 THEN '5. 4-7 Days Late'
                WHEN delay_days > 7 AND delay_days <= 14 THEN '6. 1-2 Weeks Late'
                ELSE '7. >2 Weeks Late'
            END AS delivery_performance_bucket
        FROM fact_orders
        {where} AND is_delivered = 1 AND delay_days IS NOT NULL AND review_score IS NOT NULL
    )
    SELECT 
        delivery_performance_bucket,
        COUNT(*) AS order_count,
        ROUND(AVG(review_score), 2) AS avg_review_score,
        ROUND(COUNT(CASE WHEN review_score = 1 THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_1_star_reviews,
        ROUND(COUNT(CASE WHEN review_score = 5 THEN 1 END) * 100.0 / COUNT(*), 2) AS pct_5_star_reviews
    FROM bucketed
    GROUP BY delivery_performance_bucket
    ORDER BY delivery_performance_bucket ASC;
    """
    return run_query(query)

def get_seller_performance(filters: Optional[Dict[str, Any]] = None, min_orders: int = 20) -> pd.DataFrame:
    """Calculates fulfillment and shipping compliance by seller."""
    where_conditions = ["1=1"]
    if filters:
        if filters.get("start_date"):
            where_conditions.append(f"fo.purchase_date >= '{filters['start_date']}'")
        if filters.get("end_date"):
            where_conditions.append(f"fo.purchase_date <= '{filters['end_date']}'")
        if filters.get("macro_region") and filters["macro_region"] != "All":
            where_conditions.append(f"fo.customer_macro_region = '{filters['macro_region']}'")
        if filters.get("state") and filters["state"] != "All":
            where_conditions.append(f"fo.customer_state = '{filters['state']}'")
            
    where = "WHERE " + " AND ".join(where_conditions)
    
    query = f"""
    SELECT 
        foi.seller_id,
        foi.seller_city,
        foi.seller_state,
        foi.seller_macro_region,
        COUNT(DISTINCT foi.order_id) AS total_orders,
        COUNT(foi.order_item_id) AS total_items,
        ROUND(SUM(foi.price), 2) AS total_sales_brl,
        SUM(foi.is_delivered) AS delivered_items,
        SUM(foi.is_late) AS late_items,
        ROUND(SUM(foi.is_late) * 100.0 / NULLIF(SUM(foi.is_delivered), 0), 2) AS late_delivery_rate_pct,
        SUM(foi.is_carrier_handoff_late) AS late_carrier_handoff_items,
        ROUND(SUM(foi.is_carrier_handoff_late) * 100.0 / NULLIF(COUNT(foi.order_item_id), 0), 2) AS late_handoff_rate_pct,
        ROUND(AVG(foi.review_score), 2) AS avg_review_score
    FROM fact_order_items foi
    JOIN fact_orders fo ON foi.order_id = fo.order_id
    {where}
    GROUP BY foi.seller_id, foi.seller_city, foi.seller_state, foi.seller_macro_region
    HAVING COUNT(DISTINCT foi.order_id) >= {min_orders}
    ORDER BY late_delivery_rate_pct DESC;
    """
    return run_query(query)

def get_cancellation_analysis(filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """Analyzes cancellation rates by stage and region."""
    where = build_where_clause(filters)
    query = f"""
    SELECT 
        customer_macro_region,
        COUNT(*) AS total_orders,
        SUM(is_canceled) AS canceled_orders,
        ROUND(SUM(is_canceled) * 100.0 / NULLIF(COUNT(*), 0), 2) AS cancellation_rate_pct,
        COUNT(CASE WHEN is_canceled = 1 AND order_delivered_carrier_date IS NOT NULL THEN 1 END) AS canceled_in_transit,
        COUNT(CASE WHEN is_canceled = 1 AND order_delivered_carrier_date IS NULL THEN 1 END) AS canceled_before_dispatch,
        ROUND(AVG(CASE WHEN is_canceled = 1 THEN total_order_value END), 2) AS avg_canceled_order_value
    FROM fact_orders
    {where}
    GROUP BY customer_macro_region
    ORDER BY cancellation_rate_pct DESC;
    """
    return run_query(query)

def get_drilldown_records(filters: Optional[Dict[str, Any]] = None, limit: int = 1000) -> pd.DataFrame:
    """Fetches granular records for investigation and CSV export."""
    where = build_where_clause(filters)
    query = f"""
    SELECT 
        order_id,
        customer_id,
        order_status,
        purchase_date,
        customer_state,
        customer_macro_region,
        is_delivered,
        is_late,
        actual_delivery_days,
        estimated_delivery_days,
        delay_days,
        review_score,
        total_items,
        total_order_value,
        total_freight_value
    FROM fact_orders
    {where}
    ORDER BY purchase_date DESC
    LIMIT {limit};
    """
    return run_query(query)

