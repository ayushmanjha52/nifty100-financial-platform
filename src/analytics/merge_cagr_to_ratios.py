"""
merge_cagr_to_ratios.py
Merge CAGR data into financial_ratios table
"""

import pandas as pd
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "db/nifty100.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def merge_cagr_data():
    conn = get_connection()

    # Read CAGR data generated from cagr.py
    cagr_df = pd.read_csv("output/cagr_with_flags.csv")

    # Rename columns to match financial_ratios table
    cagr_df = cagr_df.rename(columns={
        'revenue_cagr': 'revenue_cagr_5yr',
        'revenue_cagr_flag': 'revenue_cagr_flag',
        'pat_cagr': 'pat_cagr_5yr',
        'pat_cagr_flag': 'pat_cagr_flag',
        'eps_cagr': 'eps_cagr_5yr',
        'eps_cagr_flag': 'eps_cagr_flag'
    })

    # Update financial_ratios table with CAGR data
    for _, row in cagr_df.iterrows():
        conn.execute("""
            UPDATE financial_ratios
            SET 
                revenue_cagr_5yr = ?,
                revenue_cagr_flag = ?,
                pat_cagr_5yr = ?,
                pat_cagr_flag = ?,
                eps_cagr_5yr = ?,
                eps_cagr_flag = ?
            WHERE company_id = ?
        """, (
            row['revenue_cagr_5yr'],
            row['revenue_cagr_flag'],
            row['pat_cagr_5yr'],
            row['pat_cagr_flag'],
            row['eps_cagr_5yr'],
            row['eps_cagr_flag'],
            row['company_id']
        ))

    conn.commit()
    print(" CAGR data merged into financial_ratios table successfully.")

    # Verify
    count = pd.read_sql("SELECT COUNT(*) as total FROM financial_ratios WHERE revenue_cagr_5yr IS NOT NULL", conn)
    print(f"Companies with 5-year CAGR data: {count.iloc[0]['total']}")

    conn.close()


if __name__ == "__main__":
    merge_cagr_data()