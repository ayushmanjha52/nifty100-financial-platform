"""
loader.py
Complete data loading module for Nifty 100 Financial Intelligence Platform.
"""

import pandas as pd
import os
from dotenv import load_dotenv
from etl.normaliser import normalize_ticker, normalize_year
from db_utils import create_tables, insert_dataframe

load_dotenv()

RAW_DATA_PATH = os.getenv("RAW_DATA_PATH", "data/raw")


def _clean_columns(df):
    """Standard column cleaning."""
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def load_and_insert_companies():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "companies.xlsx"), header=1)
    df = _clean_columns(df)
    desired = ["id", "company_name", "face_value", "book_value", "roce_percentage", "roe_percentage"]
    df = df[[c for c in desired if c in df.columns]]
    df["id"] = df["id"].apply(normalize_ticker)
    insert_dataframe(df, "companies")


def load_and_insert_profit_and_loss():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "profitandloss.xlsx"), header=1)
    df = _clean_columns(df)
    desired = ["company_id", "year", "sales", "expenses", "operating_profit", "opm_percentage",
               "other_income", "interest", "depreciation", "profit_before_tax", "tax_percentage",
               "net_profit", "eps", "dividend_payout"]
    df = df[[c for c in desired if c in df.columns]]
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df["year"] = df["year"].apply(normalize_year)
    insert_dataframe(df, "profitandloss")


def load_and_insert_balancesheet():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "balancesheet.xlsx"), header=1)
    df = _clean_columns(df)
    desired = ["company_id", "year", "equity_capital", "reserves", "borrowings", "other_liabilities",
               "total_liabilities", "fixed_assets", "cwip", "investments", "other_asset", "total_assets"]
    df = df[[c for c in desired if c in df.columns]]
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df["year"] = df["year"].apply(normalize_year)
    insert_dataframe(df, "balancesheet")


def load_and_insert_cashflow():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "cashflow.xlsx"), header=1)
    df = _clean_columns(df)
    desired = ["company_id", "year", "operating_activity", "investing_activity",
               "financing_activity", "net_cash_flow"]
    df = df[[c for c in desired if c in df.columns]]
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df["year"] = df["year"].apply(normalize_year)
    insert_dataframe(df, "cashflow")


def load_and_insert_sectors():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "supporting datasets", "sectors.xlsx"))
    df = _clean_columns(df)
    desired = ["company_id", "broad_sector", "sub_sector"]
    df = df[[c for c in desired if c in df.columns]]
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    insert_dataframe(df, "sectors")


def load_and_insert_stock_prices():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "supporting datasets", "stock_prices.xlsx"))
    df = _clean_columns(df)
    desired = ["company_id", "date", "open_price", "high_price", "low_price", "close_price", "volume"]
    df = df[[c for c in desired if c in df.columns]]
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    insert_dataframe(df, "stock_prices")


def load_and_insert_market_cap():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "supporting datasets", "market_cap.xlsx"))
    df = _clean_columns(df)
    desired = ["company_id", "year", "market_cap_crore", "pe_ratio", "pb_ratio", "ev_ebitda", "dividend_yield_pct"]
    df = df[[c for c in desired if c in df.columns]]
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    insert_dataframe(df, "market_cap")


def load_and_insert_analysis():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "analysis.xlsx"))
    df = _clean_columns(df)
    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].apply(normalize_ticker)
    insert_dataframe(df, "analysis")


def load_and_insert_documents():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "documents.xlsx"))
    df = _clean_columns(df)
    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].apply(normalize_ticker)
    insert_dataframe(df, "documents")


def load_and_insert_prosandcons():
    df = pd.read_excel(os.path.join(RAW_DATA_PATH, "prosandcons.xlsx"))
    df = _clean_columns(df)
    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].apply(normalize_ticker)
    insert_dataframe(df, "prosandcons")


def main():
    print("Deleting old database (if exists)...")
    db_path = os.getenv("DB_PATH", "db/nifty100.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Old database deleted.")

    print("\nCreating database tables...")
    create_tables()

    print("\nLoading data into database...\n")
    load_and_insert_companies()
    load_and_insert_profit_and_loss()
    load_and_insert_balancesheet()
    load_and_insert_cashflow()
    load_and_insert_sectors()
    load_and_insert_stock_prices()
    load_and_insert_market_cap()
    load_and_insert_analysis()
    load_and_insert_documents()
    load_and_insert_prosandcons()

    print("\nData loading completed successfully!")


if __name__ == "__main__":
    main()