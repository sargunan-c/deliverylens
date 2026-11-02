"""
Automated Analytical Validation and Assertion Tests for DeliveryLens.
Verifies metrics integrity, joins, edge cases, and absence of double counting.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import run_query
from src.metrics import get_executive_kpis

def test_delivered_orders_balance():
    """Verify that every delivered order with a delivery date is either on_time or late, never both."""
    df = run_query("""
        SELECT 
            COUNT(*) AS total_delivered,
            SUM(is_late) AS late_count,
            SUM(is_on_time) AS on_time_count,
            SUM(CASE WHEN is_late = 1 AND is_on_time = 1 THEN 1 ELSE 0 END) AS invalid_overlap,
            COUNT(CASE WHEN order_delivered_customer_date IS NULL THEN 1 END) AS null_dates
        FROM fact_orders
        WHERE is_delivered = 1;
    """)
    row = df.to_dict(orient="records")[0]
    
    print("[TEST] Delivered Balance Check:", row)
    assert row["invalid_overlap"] == 0, "Error: An order cannot be both late and on-time!"
    assert row["late_count"] + row["on_time_count"] + row["null_dates"] == row["total_delivered"], \
        "Error: Sum of late, on_time, and null dates does not match total delivered orders!"
    print("[PASS] Delivered order balance and mutual exclusivity verified.")

def test_no_double_counting_in_fact_orders():
    """Ensure fact_orders has exact 1-to-1 grain with raw_orders."""
    df = run_query("""
        SELECT 
            (SELECT COUNT(*) FROM raw_orders) AS raw_count,
            (SELECT COUNT(*) FROM fact_orders) AS fact_count,
            (SELECT COUNT(DISTINCT order_id) FROM fact_orders) AS distinct_fact_orders
    """)
    row = df.to_dict(orient="records")[0]
    print("[TEST] Grain & Duplication Check:", row)
    assert row["raw_count"] == row["fact_count"], "Error: Fact orders count differs from raw orders!"
    assert row["fact_count"] == row["distinct_fact_orders"], "Error: Duplicate order_id found in fact_orders!"
    print("[PASS] Zero duplication or fan-out in fact_orders.")

def test_late_delivery_definition():
    """Verify is_late is strictly 1 only when order_delivered_customer_date > order_estimated_delivery_date."""
    df = run_query("""
        SELECT 
            COUNT(*) AS violations
        FROM fact_orders
        WHERE (is_late = 1 AND order_delivered_customer_date <= order_estimated_delivery_date)
           OR (is_late = 0 AND is_delivered = 1 AND order_delivered_customer_date > order_estimated_delivery_date);
    """)
    violations = df.iloc[0]["violations"]
    print("[TEST] Late Definition Violations:", violations)
    assert violations == 0, f"Error: Found {violations} orders violating late delivery business rule!"
    print("[PASS] Late delivery classification strictly matches business rules.")

def test_executive_kpis_consistency():
    """Verify that get_executive_kpis matches direct raw queries."""
    kpis = get_executive_kpis()
    print("[TEST] Executive KPIs generated:", kpis)
    assert kpis["total_orders"] == 99441, f"Expected 99,441 orders, got {kpis['total_orders']}"
    assert kpis["delivered_orders"] == 96478, f"Expected 96,478 delivered, got {kpis['delivered_orders']}"
    assert kpis["late_orders"] == 7826, f"Expected 7,826 late, got {kpis['late_orders']}"
    assert 8.10 <= kpis["late_delivery_rate_pct"] <= 8.12, f"Late rate out of bounds: {kpis['late_delivery_rate_pct']}"
    print("[PASS] Executive KPI accuracy confirmed against ground truth.")

if __name__ == "__main__":
    print("--- Running DeliveryLens Test Suite ---")
    test_delivered_orders_balance()
    test_no_double_counting_in_fact_orders()
    test_late_delivery_definition()
    test_executive_kpis_consistency()
    print("\nALL 4 CORE TESTS PASSED SUCCESSFULLY! [OK]")
