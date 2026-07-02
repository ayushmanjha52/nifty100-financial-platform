"""
company_scoring.py
Company scoring + ranking system with database storage.
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


def calculate_and_store_scores():
    conn = get_connection()
    cursor = conn.cursor()

    # Create company_ranking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_ranking (
            rank INTEGER,
            company_id TEXT PRIMARY KEY,
            company_name TEXT,
            final_score REAL,
            net_profit_margin REAL,
            roe REAL,
            roce REAL,
            debt_to_equity REAL,
            eps REAL
        )
    """)

    # Get latest financial ratios
    query = """
        SELECT 
            company_id,
            company_name,
            net_profit_margin,
            roe,
            roce,
            debt_to_equity,
            eps
        FROM financial_ratios
    """

    df = pd.read_sql(query, conn)

    # Scoring
    df['score_profit_margin'] = df['net_profit_margin'].rank(pct=True) * 100
    df['score_roe'] = df['roe'].rank(pct=True) * 100
    df['score_roce'] = df['roce'].rank(pct=True) * 100
    df['score_eps'] = df['eps'].rank(pct=True) * 100
    df['score_debt'] = (1 - df['debt_to_equity'].rank(pct=True)) * 100

    df['final_score'] = (
        df['score_profit_margin'] * 0.25 +
        df['score_roe'] * 0.25 +
        df['score_roce'] * 0.20 +
        df['score_eps'] * 0.15 +
        df['score_debt'] * 0.15
    ).round(2)

    df['rank'] = df['final_score'].rank(ascending=False, method='min').astype(int)

    # Final DataFrame
    final_df = df[[
        'rank', 'company_id', 'company_name', 'final_score',
        'net_profit_margin', 'roe', 'roce', 'debt_to_equity', 'eps'
    ]].sort_values('rank')

    # Save to database
    final_df.to_sql("company_ranking", conn, if_exists="replace", index=False)

    # Also save as CSV
    csv_path = os.path.join(OUTPUT_PATH, "company_ranking.csv")
    final_df.to_csv(csv_path, index=False)

    print(" Company ranking calculated and stored in database.")
    print(f" Also saved to: {csv_path}")
    print(f"\nTop 5 Companies:\n{final_df.head().to_string(index=False)}")

    conn.close()


if __name__ == "__main__":
    calculate_and_store_scores()