"""
populate_financial_ratios.py
Populate financial_ratios table with full KPIs + 5-year CAGR
"""

import pandas as pd

import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "db/nifty100.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def calculate_cagr(start, end, years):
    if pd.isna(start) or pd.isna(end) or years <= 0 or start == 0:
        return None
    try:
        return round(((end / start) ** (1 / years) - 1) * 100, 2)
    except Exception:
        return None


def populate_financial_ratios_table():
    conn = get_connection()

    # Create table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS financial_ratios (
            company_id TEXT,
            company_name TEXT,
            year TEXT,
            net_profit_margin_pct REAL,
            operating_profit_margin_pct REAL,
            return_on_equity_pct REAL,
            roce_pct REAL,
            roa_pct REAL,
            debt_to_equity REAL,
            asset_turnover REAL,
            earnings_per_share REAL,
            free_cash_flow_cr REAL,
            cfo_quality_score REAL,
            capex_intensity REAL,
            revenue_cagr_5yr REAL,
            pat_cagr_5yr REAL,
            eps_cagr_5yr REAL,
            PRIMARY KEY (company_id, year)
        )
    """)

    # Get all data
    query = """
        SELECT 
            p.company_id,
            c.company_name,
            p.year,
            p.sales,
            p.net_profit,
            p.operating_profit,
            p.eps,
            b.equity_capital,
            b.reserves,
            b.borrowings,
            b.total_assets,
            cf.operating_activity,
            cf.investing_activity
        FROM profitandloss p
        LEFT JOIN companies c ON p.company_id = c.id
        LEFT JOIN balancesheet b 
            ON p.company_id = b.company_id AND p.year = b.year
        LEFT JOIN cashflow cf 
            ON p.company_id = cf.company_id AND p.year = cf.year
        ORDER BY p.company_id, p.year
    """

    df = pd.read_sql(query, conn)

    # Calculate basic ratios
    df['net_profit_margin_pct'] = (df['net_profit'] / df['sales'] * 100).round(2)
    df['operating_profit_margin_pct'] = (df['operating_profit'] / df['sales'] * 100).round(2)
    df['return_on_equity_pct'] = (df['net_profit'] / (df['equity_capital'] + df['reserves']) * 100).round(2)
    df['roce_pct'] = (df['operating_profit'] / (df['equity_capital'] + df['reserves'] + df['borrowings']) * 100).round(2)
    df['roa_pct'] = (df['net_profit'] / df['total_assets'] * 100).round(2)
    df['debt_to_equity'] = (df['borrowings'] / (df['equity_capital'] + df['reserves'])).round(2)
    df['asset_turnover'] = (df['sales'] / df['total_assets']).round(2)
    df['earnings_per_share'] = df['eps']
    df['free_cash_flow_cr'] = df['operating_activity'] + df['investing_activity']
    df['cfo_quality_score'] = df.apply(lambda x: round(x['operating_activity'] / x['net_profit'], 2) if x['net_profit'] != 0 else None, axis=1)
    df['capex_intensity'] = df.apply(lambda x: round(abs(x['investing_activity']) / x['sales'] * 100, 2) if x['sales'] != 0 else None, axis=1)

    # Calculate 5-year CAGR per company
    cagr_data = []
    for company in df['company_id'].unique():
        company_df = df[df['company_id'] == company].sort_values('year')
        n = len(company_df)

        if n >= 6:  # At least 6 years for 5-year CAGR
            start = company_df.iloc[0]
            end = company_df.iloc[-1]
            years = n - 1

            revenue_cagr = calculate_cagr(start['sales'], end['sales'], years)
            pat_cagr = calculate_cagr(start['net_profit'], end['net_profit'], years)
            eps_cagr = calculate_cagr(start['eps'], end['eps'], years)
        else:
            revenue_cagr = pat_cagr = eps_cagr = None

        cagr_data.append({
            'company_id': company,
            'revenue_cagr_5yr': revenue_cagr,
            'pat_cagr_5yr': pat_cagr,
            'eps_cagr_5yr': eps_cagr
        })

    cagr_df = pd.DataFrame(cagr_data)

    # Merge CAGR with main data
    final_df = df.merge(cagr_df, on='company_id', how='left')

    # Select final columns
    final_df = final_df[[
        'company_id', 'company_name', 'year',
        'net_profit_margin_pct', 'operating_profit_margin_pct',
        'return_on_equity_pct', 'roce_pct', 'roa_pct',
        'debt_to_equity', 'asset_turnover', 'earnings_per_share',
        'free_cash_flow_cr', 'cfo_quality_score', 'capex_intensity',
        'revenue_cagr_5yr', 'pat_cagr_5yr', 'eps_cagr_5yr'
    ]].copy()

    # Insert into database
    final_df.to_sql("financial_ratios", conn, if_exists="replace", index=False)

    print(" financial_ratios table fully populated with KPIs + 5-year CAGR.")
    print(f"Total rows: {len(final_df)}")

    conn.close()


if __name__ == "__main__":
    populate_financial_ratios_table()