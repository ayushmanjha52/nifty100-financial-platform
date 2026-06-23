"""
loader.py
Complete data loading with Load Audit report
"""

import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
from etl.normaliser import normalize_ticker, normalize_year
from etl.db_utils import create_tables, insert_dataframe

load_dotenv()

RAW_DATA_PATH = os.getenv("RAW_DATA_PATH", "data/raw")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "output")
os.makedirs(OUTPUT_PATH, exist_ok=True)


def load_and_insert_companies():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "companies.xlsx"), header=1)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    desired = ["id", "company_name", "face_value", "book_value", "roce_percentage", "roe_percentage"]
    df = df[[col for col in desired if col in df.columns]]
    df["id"] = df["id"].apply(normalize_ticker)
    insert_dataframe(df, "companies")
    return len(df)


def load_and_insert_profit_and_loss():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "profitandloss.xlsx"), header=1)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    desired = ["company_id", "year", "sales", "expenses", "operating_profit", "opm_percentage",
               "other_income", "interest", "depreciation", "profit_before_tax", "tax_percentage",
               "net_profit", "eps", "dividend_payout"]
    df = df[[col for col in desired if col in df.columns]]
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df["year"] = df["year"].apply(normalize_year)
    insert_dataframe(df, "profitandloss")
    return len(df)


def load_and_insert_balancesheet():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "balancesheet.xlsx"), header=1)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    desired = ["company_id", "year", "equity_capital", "reserves", "borrowings", "other_liabilities",
               "total_liabilities", "fixed_assets", "cwip", "investments", "other_asset", "total_assets"]
    df = df[[col for col in desired if col in df.columns]]
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df["year"] = df["year"].apply(normalize_year)
    insert_dataframe(df, "balancesheet")
    return len(df)


def load_and_insert_cashflow():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "cashflow.xlsx"), header=1)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    desired = ["company_id", "year", "operating_activity", "investing_activity",
               "financing_activity", "net_cash_flow"]
    df = df[[col for col in desired if col in df.columns]]
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df["year"] = df["year"].apply(normalize_year)
    insert_dataframe(df, "cashflow")
    return len(df)


def load_and_insert_sectors():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "supporting datasets", "sectors.xlsx"))
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    desired = ["company_id", "broad_sector", "sub_sector"]
    df = df[[col for col in desired if col in df.columns]]
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    insert_dataframe(df, "sectors")
    return len(df)


def load_and_insert_stock_prices():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "supporting datasets", "stock_prices.xlsx"))
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    desired = ["company_id", "date", "open_price", "high_price", "low_price", "close_price", "volume"]
    df = df[[col for col in desired if col in df.columns]]
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    insert_dataframe(df, "stock_prices")
    return len(df)


def load_and_insert_market_cap():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "supporting datasets", "market_cap.xlsx"))
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    desired = ["company_id", "year", "market_cap_crore", "pe_ratio", "pb_ratio", "ev_ebitda", "dividend_yield_pct"]
    df = df[[col for col in desired if col in df.columns]]
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    insert_dataframe(df, "market_cap")
    return len(df)


def generate_load_audit(audit_data):
    audit_df = pd.DataFrame(audit_data)
    audit_df["load_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_file = os.path.join(OUTPUT_PATH, "load_audit.csv")
    audit_df.to_csv(output_file, index=False)
    print(f"\n📄 Load audit saved to: {output_file}")


def main():
    print("Deleting old database (if exists)...")
    db_path = os.getenv("DB_PATH", "db/nifty100.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Old database deleted.")

    print("\nCreating database tables...")
    create_tables()

    print("\nLoading data into database...\n")
    
    audit_data = []
    
    count = load_and_insert_companies()
    audit_data.append({"table": "companies", "rows_loaded": count})
    
    count = load_and_insert_profit_and_loss()
    audit_data.append({"table": "profitandloss", "rows_loaded": count})
    
    count = load_and_insert_balancesheet()
    audit_data.append({"table": "balancesheet", "rows_loaded": count})
    
    count = load_and_insert_cashflow()
    audit_data.append({"table": "cashflow", "rows_loaded": count})
    
    count = load_and_insert_sectors()
    audit_data.append({"table": "sectors", "rows_loaded": count})
    
    count = load_and_insert_stock_prices()
    audit_data.append({"table": "stock_prices", "rows_loaded": count})
    
    count = load_and_insert_market_cap()
    audit_data.append({"table": "market_cap", "rows_loaded": count})

    print("\nData loading completed successfully!")
    generate_load_audit(audit_data)


if __name__ == "__main__":
    main()