"""
cashflow_kpis.py
Cash Flow KPIs & Capital Allocation Pattern Classifier
"""

import pandas as pd
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "db/nifty100.db")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "output")
os.makedirs(OUTPUT_PATH, exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def classify_capital_allocation(cfo, cfi, cff):
    """Classify capital allocation pattern based on signs of CFO, CFI, CFF"""
    cfo_sign = '+' if cfo > 0 else '-'
    cfi_sign = '+' if cfi > 0 else '-'
    cff_sign = '+' if cff > 0 else '-'

    pattern = f"({cfo_sign},{cfi_sign},{cff_sign})"

    if pattern == "(+,-,-)":
        return "Reinvestor"
    elif pattern == "(+,-,+)":
        return "Shareholder Returns"
    elif pattern == "(+,+,-)":
        return "Liquidating Assets"
    elif pattern == "(-,+,+)":
        return "Distress Signal"
    elif pattern == "(-,-,+)":
        return "Growth Funded by Debt"
    elif pattern == "(+,+,+)":
        return "Cash Accumulator"
    elif pattern == "(-,-,-)":
        return "Pre-Revenue"
    else:
        return "Mixed"


def calculate_cashflow_kpis():
    conn = get_connection()

    query = """
        SELECT 
            cf.company_id,
            c.company_name,
            cf.year,
            cf.operating_activity,
            cf.investing_activity,
            cf.financing_activity,
            p.net_profit,
            p.operating_profit,
            p.sales
        FROM cashflow cf
        JOIN companies c ON cf.company_id = c.id
        JOIN profitandloss p 
            ON cf.company_id = p.company_id 
            AND cf.year = p.year
        ORDER BY cf.company_id, cf.year
    """

    df = pd.read_sql(query, conn)

    # Free Cash Flow (FCF)
    df['free_cash_flow_cr'] = df['operating_activity'] + df['investing_activity']

    # CFO Quality Score
    df['cfo_quality_score'] = df.apply(
        lambda x: round(x['operating_activity'] / x['net_profit'], 2) if x['net_profit'] != 0 else None, axis=1
    )

    # CapEx Intensity
    df['capex_intensity'] = df.apply(
        lambda x: round(abs(x['investing_activity']) / x['sales'] * 100, 2) if x['sales'] != 0 else None, axis=1
    )

    # FCF Conversion Rate
    df['fcf_conversion_rate'] = df.apply(
        lambda x: round(x['free_cash_flow_cr'] / x['operating_profit'] * 100, 2) if x['operating_profit'] != 0 else None, axis=1
    )

    # Capital Allocation Pattern
    df['capital_allocation_pattern'] = df.apply(
        lambda x: classify_capital_allocation(
            x['operating_activity'], 
            x['investing_activity'], 
            x['financing_activity']
        ), axis=1
    )

    # Final DataFrame
    final_df = df[[
        'company_id', 'company_name', 'year',
        'free_cash_flow_cr', 'cfo_quality_score', 'capex_intensity',
        'fcf_conversion_rate', 'capital_allocation_pattern'
    ]].copy()

    # Save to CSV
    output_file = os.path.join(OUTPUT_PATH, "capital_allocation.csv")
    final_df.to_csv(output_file, index=False)

    print(" Cash Flow KPIs and Capital Allocation patterns calculated.")
    print(f" Saved to: {output_file}")
    print(f"Total records: {len(final_df)}")

    conn.close()
    return final_df


if __name__ == "__main__":
    calculate_cashflow_kpis()