"""
trend_analysis.py
Year-over-Year (YoY) growth analysis with database storage.
"""

import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "db/nifty100.db")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "output")
os.makedirs(OUTPUT_PATH, exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def calculate_and_store_yoy_growth():
    conn = get_connection()
    cursor = conn.cursor()

    # Create yoy_growth table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS yoy_growth (
            company_id TEXT,
            company_name TEXT,
            year TEXT,
            sales_growth REAL,
            profit_growth REAL,
            eps_growth REAL,
            PRIMARY KEY (company_id, year)
        )
    """)

    # Get data with previous year values
    query = """
        SELECT 
            p1.company_id,
            c.company_name,
            p1.year AS current_year,
            p1.sales AS current_sales,
            p1.net_profit AS current_net_profit,
            p1.eps AS current_eps,
            p2.sales AS prev_sales,
            p2.net_profit AS prev_net_profit,
            p2.eps AS prev_eps
        FROM profitandloss p1
        LEFT JOIN profitandloss p2 
            ON p1.company_id = p2.company_id 
            AND CAST(SUBSTR(p1.year, 1, 4) AS INTEGER) = CAST(SUBSTR(p2.year, 1, 4) AS INTEGER) + 1
        JOIN companies c ON p1.company_id = c.id
        ORDER BY p1.company_id, p1.year DESC
    """

    df = pd.read_sql(query, conn)

    # Calculate YoY Growth
    df['sales_growth'] = ((df['current_sales'] - df['prev_sales']) / df['prev_sales']) * 100
    df['profit_growth'] = ((df['current_net_profit'] - df['prev_net_profit']) / df['prev_net_profit']) * 100
    df['eps_growth'] = ((df['current_eps'] - df['prev_eps']) / df['prev_eps']) * 100

    df = df.round(2)

    # Final DataFrame
    final_df = df[[
        'company_id', 'company_name', 'current_year',
        'sales_growth', 'profit_growth', 'eps_growth'
    ]].copy()

    final_df.columns = ['company_id', 'company_name', 'year', 
                        'sales_growth', 'profit_growth', 'eps_growth']

    # Save to database
    final_df.to_sql("yoy_growth", conn, if_exists="replace", index=False)

    # Also save as CSV
    csv_path = os.path.join(OUTPUT_PATH, "yoy_growth.csv")
    final_df.to_csv(csv_path, index=False)

    print(" YoY Growth data saved to database and CSV.")
    print(f" File saved to: {csv_path}")
    print(f"Total records: {len(final_df)}")

    conn.close()


if __name__ == "__main__":
    calculate_and_store_yoy_growth()