"""
Test Runner for DeliveryLens.
Executes all test functions across query logic and dashboard views, reporting exact pass/fail counts.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_queries import (
    test_delivered_orders_balance,
    test_no_double_counting_in_fact_orders,
    test_late_delivery_definition,
    test_executive_kpis_consistency
)
from tests.test_views import test_metrics_and_charts

tests = [
    ("test_delivered_orders_balance", test_delivered_orders_balance),
    ("test_no_double_counting_in_fact_orders", test_no_double_counting_in_fact_orders),
    ("test_late_delivery_definition", test_late_delivery_definition),
    ("test_executive_kpis_consistency", test_executive_kpis_consistency),
    ("test_metrics_and_charts", test_metrics_and_charts)
]

print("=" * 65)
print("RUNNING AUTOMATED TEST SUITE: DELIVERYLENS")
print("=" * 65)

passed = 0
failed = 0

for name, test_fn in tests:
    print(f"\n>> Executing: {name}")
    try:
        test_fn()
        passed += 1
        print(f"   RESULT: PASS")
    except Exception as e:
        failed += 1
        print(f"   RESULT: FAIL -> {e}")

print("\n" + "=" * 65)
print(f"TEST EXECUTION SUMMARY: Total Tests: {len(tests)} | Passed: {passed} | Failed: {failed}")
print("=" * 65)

if failed > 0:
    sys.exit(1)

