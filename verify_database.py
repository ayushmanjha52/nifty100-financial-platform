"""
verify_database.py
Verify all tables in nifty100.db
"""

import sqlite3
import pandas as pd

DB_PATH = "db/nifty100.db"

def verify_database():
    conn = sqlite3.connect(DB_PATH)
    
    # Get list of all tables
    tables = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """).fetchall()
    
    tables = [t[0] for t in tables]
    
    print("=" * 60)
    print("DATABASE VERIFICATION REPORT")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"Total Tables: {len(tables)}")
    print("-" * 60)
    
    # Show row counts
    print("\n ROW COUNTS:")
    print("-" * 40)
    for table in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:25} → {count:6} rows")
    
    # Show sample data from key tables
    print("\n" + "=" * 60)
    print(" SAMPLE DATA FROM KEY TABLES")
    print("=" * 60)
    
    key_tables = ["companies", "profitandloss", "sectors", "stock_prices"]
    
    for table in key_tables:
        if table in tables:
            print(f"\n🔹 {table.upper()} (First 3 rows):")
            df = pd.read_sql(f"SELECT * FROM {table} LIMIT 3", conn)
            print(df.to_string(index=False))
            print("-" * 60)
    
    conn.close()
    print("\n Database verification completed!")

if __name__ == "__main__":
    verify_database()