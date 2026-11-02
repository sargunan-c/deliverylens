"""
Database Manager for DeliveryLens using DuckDB.
Provides read-only connection pooling and query helper methods.
"""

import os
import duckdb
import pandas as pd

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data", "processed", "deliverylens.duckdb"
).replace("\\", "/")

def get_connection(read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """Returns a DuckDB connection."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found at {DB_PATH}. Run src/loader.py first.")
    return duckdb.connect(DB_PATH, read_only=read_only)

def run_query(query: str, params=None) -> pd.DataFrame:
    """Executes a SQL query and returns a pandas DataFrame."""
    con = get_connection(read_only=True)
    try:
        if params:
            df = con.execute(query, params).df()
        else:
            df = con.execute(query).df()
        return df
    finally:
        con.close()

