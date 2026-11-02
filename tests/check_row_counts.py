import os
import duckdb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
RAW_DIR = f"{BASE_DIR}/data/raw"
DB_PATH = f"{BASE_DIR}/data/processed/deliverylens.duckdb"

con = duckdb.connect(DB_PATH, read_only=True)

files_and_tables = [
    ("olist_orders_dataset.csv", "raw_orders"),
    ("olist_customers_dataset.csv", "raw_customers"),
    ("olist_order_items_dataset.csv", "raw_order_items"),
    ("olist_order_payments_dataset.csv", "raw_order_payments"),
    ("olist_order_reviews_dataset.csv", "raw_order_reviews"),
    ("olist_sellers_dataset.csv", "raw_sellers"),
    ("olist_products_dataset.csv", "raw_products"),
    ("product_category_name_translation.csv", "raw_category_translation"),
    ("olist_geolocation_dataset.csv", "raw_geolocation")
]

print(f"{'Source CSV File':38} | {'CSV Rows':>10} | {'DuckDB Table':24} | {'Table Rows':>12} | Status")
print("-" * 98)

db_tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]

for csv_file, tbl in files_and_tables:
    csv_path = f"{RAW_DIR}/{csv_file}"
    csv_rows = con.execute(f"SELECT COUNT(*) FROM read_csv_auto('{csv_path}')").fetchone()[0]
    if tbl in db_tables:
        tbl_rows = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        status = "MATCH" if csv_rows == tbl_rows else "MISMATCH"
        print(f"{csv_file:38} | {csv_rows:>10,d} | {tbl:24} | {tbl_rows:>12,d} | {status}")
    else:
        print(f"{csv_file:38} | {csv_rows:>10,d} | {tbl:24} | {'NOT INGESTED':>12} | UNINGESTED (Omitted by design)")
con.close()

