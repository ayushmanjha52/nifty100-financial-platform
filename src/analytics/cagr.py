"""
cagr.py
CAGR Engine with 3-year, 5-year, and 10-year support + Edge Cases
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


def calculate_cagr(start_value, end_value, years):
    """Calculate CAGR with edge case handling"""
    if pd.isna(start_value) or pd.isna(end_value) or years <= 0:
        return None, "INSUFFICIENT"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value > 0 and end_value > 0:
        cagr = ((end_value / start_value) ** (1 / years) - 1) * 100
        return round(cagr, 2), "NORMAL"

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    return None, "INSUFFICIENT"


def calculate_multi_period_cagr():
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

    periods = [3, 5, 10]

    for company in df['company_id'].unique():
        company_data = df[df['company_id'] == company].sort_values('year').reset_index(drop=True)
        n_years = len(company_data)

        for period in periods:
            if n_years < period + 1:
                continue

            # Take last 'period' years
            recent_data = company_data.tail(period + 1)
            start = recent_data.iloc[0]
            end = recent_data.iloc[-1]
            years = period

            # Revenue CAGR
            rev_cagr, rev_flag = calculate_cagr(start['sales'], end['sales'], years)

            # PAT CAGR
            pat_cagr, pat_flag = calculate_cagr(start['net_profit'], end['net_profit'], years)

            # EPS CAGR
            eps_cagr, eps_flag = calculate_cagr(start['eps'], end['eps'], years)

            results.append({
                'company_id': company,
                'company_name': start['company_name'],
                'period_years': years,
                'revenue_cagr': rev_cagr,
                'revenue_cagr_flag': rev_flag,
                'pat_cagr': pat_cagr,
                'pat_cagr_flag': pat_flag,
                'eps_cagr': eps_cagr,
                'eps_cagr_flag': eps_flag
            })

    result_df = pd.DataFrame(results)

    # Save to CSV
    output_file = os.path.join(OUTPUT_PATH, "cagr_multi_period.csv")
    result_df.to_csv(output_file, index=False)

    print(" Multi-period CAGR analysis completed.")
    print(f" Saved to: {output_file}")
    print(f"Total records: {len(result_df)}")

    conn.close()
    return result_df


if __name__ == "__main__":
    calculate_multi_period_cagr()