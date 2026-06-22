"""
db_utils.py
Database utility functions for SQLite operations.
"""
import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "db/nifty100.db")


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables():
    """Create all tables from schema.sql if they don't exist."""
    schema_path = os.path.join("db", "schema.sql")
    
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    conn = get_connection()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Database tables created successfully.")


def insert_dataframe(df: pd.DataFrame, table_name: str):
    """Insert DataFrame into SQLite table (with foreign key checks disabled)."""
    conn = get_connection()
    
    # Temporarily disable foreign key checks
    conn.execute("PRAGMA foreign_keys = OFF;")
    
    df.to_sql(table_name, conn, if_exists="append", index=False)
    
    # Re-enable foreign key checks
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()
    
    print(f"Inserted {len(df)} rows into {table_name}.")