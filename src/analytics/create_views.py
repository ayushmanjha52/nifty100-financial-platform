"""
create_views.py
Create useful analytics views in the database.
"""

import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "db/nifty100.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_analytics_views():
    conn = get_connection()
    cursor = conn.cursor()

    print("Creating analytics views...")

    # View 1: Latest Company Summary
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS vw_company_summary AS
        SELECT 
            c.id AS company_id,
            c.company_name,
            r.year,
            r.net_profit_margin,
            r.roe,
            r.roce,
            r.debt_to_equity,
            r.eps,
            rk.rank,
            rk.final_score
        FROM companies c
        LEFT JOIN financial_ratios r ON c.id = r.company_id
        LEFT JOIN company_ranking rk ON c.id = rk.company_id
    """)

    # View 2: Top 10 Companies by ROE
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS vw_top_companies_by_roe AS
        SELECT 
            rank,
            company_name,
            roe,
            final_score
        FROM company_ranking
        ORDER BY roe DESC
        LIMIT 10
    """)

    # View 3: Companies with Low Debt (Conservative)
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS vw_low_debt_companies AS
        SELECT 
            company_name,
            debt_to_equity,
            roe,
            final_score
        FROM company_ranking
        WHERE debt_to_equity < 0.5
        ORDER BY final_score DESC
    """)

    # View 4: High Profit Margin Companies
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS vw_high_margin_companies AS
        SELECT 
            company_name,
            net_profit_margin,
            roe,
            final_score
        FROM company_ranking
        WHERE net_profit_margin > 15
        ORDER BY final_score DESC
    """)

    conn.commit()
    print(" Analytics views created successfully!")

    # Show created views
    views = cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type = 'view'
    """).fetchall()

    print("\nCreated Views:")
    for view in views:
        print(f"  - {view[0]}")

    conn.close()


if __name__ == "__main__":
    create_analytics_views()