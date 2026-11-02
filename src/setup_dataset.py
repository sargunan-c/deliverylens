"""
Dataset Setup & Health Verification Script for DeliveryLens.
Verifies presence of raw Olist CSVs or provides actionable download instructions.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

REQUIRED_FILES = [
    "olist_orders_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_products_dataset.csv",
    "product_category_name_translation.csv"
]

def verify_dataset() -> bool:
    print("=" * 60)
    print("DELIVERYLENS DATASET VERIFICATION")
    print(f"Target Directory: {RAW_DIR}")
    print("=" * 60)
    
    missing = []
    found = []
    for filename in REQUIRED_FILES:
        filepath = os.path.join(RAW_DIR, filename)
        if os.path.exists(filepath):
            found.append((filename, os.path.getsize(filepath)))
        else:
            missing.append(filename)
            
    if found:
        print(f"\n[FOUND] {len(found)} core dataset files verified:")
        for fn, size in found:
            print(f"  + {fn:38} ({size / (1024*1024):.2f} MB)")
            
    if missing:
        print(f"\n[MISSING] {len(missing)} files not found:")
        for fn in missing:
            print(f"  - {fn}")
        print("\n" + "=" * 60)
        print("SETUP INSTRUCTIONS:")
        print("1. Download the Brazilian E-Commerce dataset directly from Kaggle:")
        print("   URL: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce")
        print(f"2. Extract the downloaded zip file into: {RAW_DIR}")
        print("3. Run the DuckDB ingestion pipeline:")
        print("   python src/loader.py")
        print("=" * 60)
        return False
        
    print("\n[SUCCESS] All core Olist CSV files are present and ready!")
    print("You can now run: python src/loader.py to build the analytical database.")
    return True

if __name__ == "__main__":
    success = verify_dataset()
    if not success:
        sys.exit(1)
