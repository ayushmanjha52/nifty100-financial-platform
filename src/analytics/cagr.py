"""
cagr.py
CAGR Engine with Full Edge Case Handling (as per Sprint 2 plan)
"""

import pandas as pd

from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "db/nifty100.db")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "output")
os.makedirs(OUTPUT_PATH, exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def calculate_cagr_with_flag(start, end, years):
    """
    Calculate CAGR and return value + flag based on edge cases.
    """
    if pd.isna(start) or pd.isna(end) or years <= 0:
        return None, "INSUFFICIENT"

    if start == 0:
        return None, "ZERO_BASE"

    # Both positive
    if start > 0 and end > 0:
        try:
            cagr = ((end / start) ** (1 / years) - 1) * 100
            return round(cagr, 2), "NORMAL"
        except Exception:
            return None, "INSUFFICIENT"

    # Positive to Negative (Decline to Loss)
    if start > 0 and end < 0:
        return None, "DECLINE_TO_LOSS"

    # Negative to Positive (Turnaround)
    if start < 0 and end > 0:
        return None, "TURNAROUND"

    # Both Negative
    if start < 0 and end < 0:
        return None, "BOTH_NEGATIVE"

    return None, "INSUFFICIENT"


def calculate_cagr_for_all_companies():
    conn = get_connection()

    query = """
        SELECT 
            p.company_id,
            c.company_name,
            p.year,
            p.sales,
            p.net_profit,
            p.eps
        FROM profitandloss p
        JOIN companies c ON p.company_id = c.id
        ORDER BY p.company_id, p.year
    """

    df = pd.read_sql(query, conn)
    results = []

    for company in df['company_id'].unique():
        company_data = df[df['company_id'] == company].sort_values('year').reset_index(drop=True)
        n_years = len(company_data)

        if n_years < 6:  # Need at least 6 years for 5-year CAGR
            continue

        # Use last 6 years for 5-year CAGR
        recent_data = company_data.tail(6)
        start = recent_data.iloc[0]
        end = recent_data.iloc[-1]
        years = 5

        # Revenue CAGR
        rev_cagr, rev_flag = calculate_cagr_with_flag(start['sales'], end['sales'], years)

        # PAT CAGR
        pat_cagr, pat_flag = calculate_cagr_with_flag(start['net_profit'], end['net_profit'], years)

        # EPS CAGR
        eps_cagr, eps_flag = calculate_cagr_with_flag(start['eps'], end['eps'], years)

        results.append({
            'company_id': company,
            'company_name': start['company_name'],
            'period': '5yr',
            'revenue_cagr': rev_cagr,
            'revenue_cagr_flag': rev_flag,
            'pat_cagr': pat_cagr,
            'pat_cagr_flag': pat_flag,
            'eps_cagr': eps_cagr,
            'eps_cagr_flag': eps_flag
        })

    result_df = pd.DataFrame(results)

    # Save to CSV
    output_file = os.path.join(OUTPUT_PATH, "cagr_with_flags.csv")
    result_df.to_csv(output_file, index=False)

    print(" CAGR with edge case flags generated.")
    print(f" Saved to: {output_file}")
    print(f"Total companies processed: {len(result_df)}")

    conn.close()
    return result_df


if __name__ == "__main__":
    calculate_cagr_for_all_companies()