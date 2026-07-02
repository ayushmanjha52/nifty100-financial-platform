"""
populate_financial_ratios.py
Populate financial_ratios table with all KPIs + CAGR + Flags
"""

import pandas as pd
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "db/nifty100.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def populate_financial_ratios_table():
    conn = get_connection()

    # Create comprehensive table (with CAGR flag columns)
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
            revenue_cagr_flag TEXT,
            pat_cagr_5yr REAL,
            pat_cagr_flag TEXT,
            eps_cagr_5yr REAL,
            eps_cagr_flag TEXT,
            PRIMARY KEY (company_id, year)
        )
    """)

    # Get base data
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
        JOIN companies c ON p.company_id = c.id
        JOIN balancesheet b 
            ON p.company_id = b.company_id 
            AND p.year = b.year
        LEFT JOIN cashflow cf 
            ON p.company_id = cf.company_id 
            AND p.year = cf.year
    """

    df = pd.read_sql(query, conn)

    # Calculate Profitability + Leverage + Cash Flow KPIs
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

    # Add CAGR columns (we'll fill them from cagr.py output later)
    df['revenue_cagr_5yr'] = None
    df['revenue_cagr_flag'] = None
    df['pat_cagr_5yr'] = None
    df['pat_cagr_flag'] = None
    df['eps_cagr_5yr'] = None
    df['eps_cagr_flag'] = None

    # Final columns
    final_df = df[[
        'company_id', 'company_name', 'year',
        'net_profit_margin_pct', 'operating_profit_margin_pct',
        'return_on_equity_pct', 'roce_pct', 'roa_pct',
        'debt_to_equity', 'asset_turnover', 'earnings_per_share',
        'free_cash_flow_cr', 'cfo_quality_score', 'capex_intensity',
        'revenue_cagr_5yr', 'revenue_cagr_flag',
        'pat_cagr_5yr', 'pat_cagr_flag',
        'eps_cagr_5yr', 'eps_cagr_flag'
    ]].copy()

    # Insert into database
    final_df.to_sql("financial_ratios", conn, if_exists="replace", index=False)

    print(" financial_ratios table updated with CAGR flag columns.")
    print(f"Total rows: {len(final_df)}")

    conn.close()


if __name__ == "__main__":
    populate_financial_ratios_table()