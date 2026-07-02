"""
ratios.py
Profitability + Leverage & Efficiency Ratios Engine
"""

import pandas as pd
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "db/nifty100.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def calculate_and_store_profitability_ratios():
    conn = get_connection()
    cursor = conn.cursor()

    # Create / Update financial_ratios table with all required columns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_ratios (
            company_id TEXT,
            company_name TEXT,
            year TEXT,
            net_profit_margin_pct REAL,
            operating_profit_margin_pct REAL,
            return_on_equity_pct REAL,
            roce_pct REAL,
            roa_pct REAL,
            opm_cross_check_diff REAL,
            debt_to_equity REAL,
            interest_coverage REAL,
            icr_label TEXT,
            high_leverage_flag BOOLEAN,
            icr_warning_flag BOOLEAN,
            net_debt_cr REAL,
            asset_turnover REAL,
            PRIMARY KEY (company_id, year)
        )
    """)

    # Fetch required data
    query = """
        SELECT 
            p.company_id,
            c.company_name,
            p.year,
            p.sales,
            p.net_profit,
            p.operating_profit,
            p.other_income,
            p.opm_percentage,
            p.interest,
            b.equity_capital,
            b.reserves,
            b.borrowings,
            b.total_assets,
            b.investments
        FROM profitandloss p
        JOIN companies c ON p.company_id = c.id
        JOIN balancesheet b 
            ON p.company_id = b.company_id 
            AND p.year = b.year
    """

    df = pd.read_sql(query, conn)

    # =====================
    # Profitability Ratios
    # =====================
    df['net_profit_margin_pct'] = df.apply(
        lambda x: round((x['net_profit'] / x['sales']) * 100, 2) if x['sales'] != 0 else None, axis=1
    )

    df['operating_profit_margin_pct'] = df.apply(
        lambda x: round((x['operating_profit'] / x['sales']) * 100, 2) if x['sales'] != 0 else None, axis=1
    )

    df['opm_cross_check_diff'] = df.apply(
        lambda x: abs(x['operating_profit_margin_pct'] - x['opm_percentage'])
        if pd.notna(x['opm_percentage']) and pd.notna(x['operating_profit_margin_pct']) else None, axis=1
    )

    df['return_on_equity_pct'] = df.apply(
        lambda x: round((x['net_profit'] / (x['equity_capital'] + x['reserves'])) * 100, 2)
        if (x['equity_capital'] + x['reserves']) > 0 else None, axis=1
    )

    df['roce_pct'] = df.apply(
        lambda x: round((x['operating_profit'] / (x['equity_capital'] + x['reserves'] + x['borrowings'])) * 100, 2)
        if (x['equity_capital'] + x['reserves'] + x['borrowings']) > 0 else None, axis=1
    )

    df['roa_pct'] = df.apply(
        lambda x: round((x['net_profit'] / x['total_assets']) * 100, 2)
        if x['total_assets'] != 0 else None, axis=1
    )

    # =====================
    # Leverage & Efficiency Ratios
    # =====================
    df['debt_to_equity'] = df.apply(
        lambda x: round(x['borrowings'] / (x['equity_capital'] + x['reserves']), 2)
        if (x['equity_capital'] + x['reserves']) > 0 else 0, axis=1
    )

    df['high_leverage_flag'] = df['debt_to_equity'].apply(lambda x: True if x > 5 else False)

    df['interest_coverage'] = df.apply(
        lambda x: round((x['operating_profit'] + x['other_income']) / x['interest'], 2)
        if x['interest'] != 0 else None, axis=1
    )

    df['icr_label'] = df['interest_coverage'].apply(
        lambda x: "Debt Free" if x is None else None
    )

    df['icr_warning_flag'] = df['interest_coverage'].apply(
        lambda x: True if x is not None and x < 1.5 else False
    )

    df['net_debt_cr'] = df.apply(
        lambda x: round(x['borrowings'] - x['investments'], 2) if pd.notna(x['investments']) else x['borrowings'], axis=1
    )

    df['asset_turnover'] = df.apply(
        lambda x: round(x['sales'] / x['total_assets'], 2) if x['total_assets'] != 0 else None, axis=1
    )

    # Final DataFrame
    final_df = df[[
        'company_id', 'company_name', 'year',
        'net_profit_margin_pct', 'operating_profit_margin_pct',
        'return_on_equity_pct', 'roce_pct', 'roa_pct',
        'opm_cross_check_diff',
        'debt_to_equity', 'interest_coverage', 'icr_label',
        'high_leverage_flag', 'icr_warning_flag',
        'net_debt_cr', 'asset_turnover'
    ]].copy()

    # Insert into database (replace old data)
    final_df.to_sql("financial_ratios", conn, if_exists="replace", index=False)

    print(" Profitability + Leverage ratios calculated and stored successfully.")
    print(f"Total rows: {len(final_df)}")

    conn.close()
    return final_df


if __name__ == "__main__":
    calculate_and_store_profitability_ratios()