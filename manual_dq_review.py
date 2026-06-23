"""
manual_dq_review.py
Helper script for Data Quality Manual Review (Sprint 1 requirement)
"""

import pandas as pd
import sqlite3


DB_PATH = "db/nifty100.db"

def manual_review_companies(n=5):
    """Randomly select n companies for manual review"""
    conn = sqlite3.connect(DB_PATH)
    
    companies = pd.read_sql("SELECT id, company_name FROM companies", conn)
    
    if len(companies) == 0:
        print("No companies found in database.")
        return
    
    sample = companies.sample(n=min(n, len(companies)), random_state=42)
    
    print(f"\n=== MANUAL DATA QUALITY REVIEW ({n} Companies) ===\n")
    
    for idx, row in sample.iterrows():
        print(f"Company: {row['company_name']} ({row['id']})")
        print("-" * 50)
        
        # Show sample financial data
        pnl = pd.read_sql(f"""
            SELECT year, sales, net_profit, eps 
            FROM profitandloss 
            WHERE company_id = '{row['id']}' 
            ORDER BY year DESC 
            LIMIT 3
        """, conn)
        
        print(pnl.to_string(index=False))
        print("\n" + "=" * 50 + "\n")
    
    conn.close()
    print("Please manually verify the above data for correctness.")


if __name__ == "__main__":
    manual_review_companies(5)