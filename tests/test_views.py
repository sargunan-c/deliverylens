"""
Smoke test to execute all metric pipelines and view functions.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metrics import (
    get_executive_kpis,
    get_monthly_trends,
    get_regional_performance,
    get_delay_buckets_vs_review,
    get_seller_performance,
    get_cancellation_analysis,
    get_drilldown_records
)
from app.components.charts import (
    plot_monthly_volume_and_late_rate,
    plot_ontime_vs_late_donut,
    plot_regional_late_rates,
    plot_delay_cliff_vs_review,
    plot_seller_handoff_vs_delivery_late
)

def test_metrics_and_charts():
    filters = {
        "start_date": "2017-01-01",
        "end_date": "2018-08-31",
        "macro_region": "All",
        "state": "All",
        "order_status": "All"
    }
    
    print("[1] Testing Executive KPIs...")
    kpis = get_executive_kpis(filters)
    assert kpis["total_orders"] > 0
    donut_fig = plot_ontime_vs_late_donut(int(kpis["delivered_orders"]), int(kpis["late_orders"]))
    assert donut_fig is not None
    print(f"    Total Orders: {kpis['total_orders']:,}, Delivered: {kpis['delivered_orders']:,}, Late: {kpis['late_orders']:,}")

    print("[2] Testing Monthly Trends...")
    trends_df = get_monthly_trends(filters)
    assert not trends_df.empty
    trend_fig = plot_monthly_volume_and_late_rate(trends_df)
    assert trend_fig is not None
    print(f"    Months evaluated: {len(trends_df)}")

    print("[3] Testing Regional Performance...")
    regional_df = get_regional_performance(filters)
    assert not regional_df.empty
    reg_fig = plot_regional_late_rates(regional_df)
    assert reg_fig is not None
    print(f"    States evaluated: {len(regional_df)}")

    print("[4] Testing Delay Cliff & Reviews...")
    cliff_df = get_delay_buckets_vs_review(filters)
    assert not cliff_df.empty
    cliff_fig = plot_delay_cliff_vs_review(cliff_df)
    assert cliff_fig is not None
    print(f"    Buckets evaluated: {len(cliff_df)}")

    print("[5] Testing Seller Performance...")
    sellers_df = get_seller_performance(filters, min_orders=20)
    assert not sellers_df.empty
    seller_fig = plot_seller_handoff_vs_delivery_late(sellers_df)
    assert seller_fig is not None
    print(f"    Sellers evaluated (>=20 orders): {len(sellers_df)}")

    print("[6] Testing Cancellation Analysis...")
    cancel_df = get_cancellation_analysis(filters)
    assert not cancel_df.empty
    print(f"    Regions evaluated: {len(cancel_df)}")

    print("[7] Testing Drilldown Records & Export...")
    drill_df = get_drilldown_records(filters, limit=100)
    assert len(drill_df) == 100
    print(f"    Drilldown sample loaded: {len(drill_df)} rows")

    print("\nALL METRICS, QUERIES, AND PLOTLY CHARTS VALIDATED SUCCESSFULLY! [OK]")

if __name__ == "__main__":
    test_metrics_and_charts()

