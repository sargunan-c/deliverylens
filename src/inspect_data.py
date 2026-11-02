"""
Data Inspection & Profiling Script for Brazilian Olist E-commerce Dataset.
Inspects real CSV files, collects row counts, column names, null counts, and key uniqueness.
"""

import os
import json
import duckdb

DATA_DIR = r"C:\Users\csarg\.gemini\antigravity\scratch\deliverylens\data\raw"

csv_files = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}

con = duckdb.connect()

profile_results = {}

for name, filename in csv_files.items():
    filepath = os.path.join(DATA_DIR, filename).replace("\\", "/")
    print(f"--- Profiling {name} ({filename}) ---")
    
    # 1. Total row count
    row_count = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{filepath}')").fetchone()[0]
    
    # 2. Schema and columns
    df_sample = con.execute(f"DESCRIBE SELECT * FROM read_csv_auto('{filepath}') LIMIT 1").fetchall()
    columns_info = [{"column": row[0], "type": row[1]} for row in df_sample]
    
    # 3. Missing values per column
    null_checks = ", ".join([f"COUNT(*) - COUNT({col['column']}) AS null_{col['column']}" for col in columns_info])
    null_counts_row = con.execute(f"SELECT {null_checks} FROM read_csv_auto('{filepath}')").fetchone()
    null_counts = {columns_info[i]["column"]: null_counts_row[i] for i in range(len(columns_info))}
    
    profile_results[name] = {
        "filename": filename,
        "row_count": row_count,
        "columns": columns_info,
        "null_counts": null_counts
    }
    print(f"Rows: {row_count:,}")

# Output summary to JSON for reproducibility
out_path = r"C:\Users\csarg\.gemini\antigravity\scratch\deliverylens\docs\dataset_profile.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(profile_results, f, indent=2)

print(f"\nProfile successfully saved to {out_path}")

