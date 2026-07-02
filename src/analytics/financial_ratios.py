"""
financial_ratios.py
Calculate and store key financial ratios in the database.
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


def calculate_and_store_ratios():
    conn = get_connection()
    cursor = conn.cursor()

    # Create financial_ratios table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_ratios (
            company_id TEXT,
            company_name TEXT,
            year TEXT,
            net_profit_margin REAL,
            roe REAL,
            roce REAL,
            debt_to_equity REAL,
            eps REAL,
            PRIMARY KEY (company_id, year)
        )
    """)

    # Get latest data for each company
    query = """
        SELECT 
            p.company_id,
            c.company_name,
            p.year,
            p.sales,
            p.net_profit,
            p.eps,
            b.equity_capital,
            b.reserves,
            b.borrowings,
            b.total_assets
        FROM profitandloss p
        JOIN companies c ON p.company_id = c.id
        JOIN balancesheet b 
            ON p.company_id = b.company_id 
            AND p.year = b.year
        WHERE p.year = (
            SELECT MAX(year) 
            FROM profitandloss 
            WHERE company_id = p.company_id
        )
    """

    df = pd.read_sql(query, conn)

    # Calculate Ratios
    df['net_profit_margin'] = (df['net_profit'] / df['sales']) * 100
    df['roe'] = (df['net_profit'] / (df['equity_capital'] + df['reserves'])) * 100
    df['roce'] = (df['net_profit'] / df['total_assets']) * 100
    df['debt_to_equity'] = df['borrowings'] / (df['equity_capital'] + df['reserves'])

    # Select final columns
    final_df = df[[
        'company_id', 'company_name', 'year',
        'net_profit_margin', 'roe', 'roce', 
        'debt_to_equity', 'eps'
    ]].copy()

    final_df = final_df.round(2)

    # Insert into database (replace if exists)
    final_df.to_sql("financial_ratios", conn, if_exists="replace", index=False)

    # Also save as CSV
    csv_path = os.path.join(OUTPUT_PATH, "financial_ratios.csv")
    final_df.to_csv(csv_path, index=False)

    print(" Financial ratios calculated and stored in database.")
    print(f" Also saved to: {csv_path}")
    print(f"Total companies: {len(final_df)}")

    conn.close()


if __name__ == "__main__":
    calculate_and_store_ratios()