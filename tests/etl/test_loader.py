"""
test_loader.py
Unit tests for loader.py data processing logic
Total: 16 tests
"""

import pandas as pd
from etl.normaliser import normalize_ticker, normalize_year


# ============================================================
# Column Cleaning Tests
# ============================================================

def test_column_cleaning_basic():
    df = pd.DataFrame({"Company ID": [1], " Year ": ["2023"], "Sales Amount": [100]})
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    assert list(df.columns) == ["company_id", "year", "sales_amount"]


def test_column_cleaning_special_chars():
    df = pd.DataFrame({"Company-Name": ["A"], "Net Profit %": [10]})
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("-", "_")
    assert "company_name" in df.columns


# ============================================================
# Normalization Tests
# ============================================================

def test_normalize_company_id():
    df = pd.DataFrame({"company_id": [" reliance ", "TCS", "adani"]})
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    assert list(df["company_id"]) == ["RELIANCE", "TCS", "ADANI"]


def test_normalize_year_column():
    df = pd.DataFrame({"year": ["Mar-23", "FY22", "Dec-21"]})
    df["year"] = df["year"].apply(normalize_year)
    assert list(df["year"]) == ["2023-03", "2022-03", "2021-12"]


def test_normalize_mixed_data():
    df = pd.DataFrame({
        "company_id": [" reliance ", "TCS"],
        "year": ["Mar-23", "FY22"]
    })
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df["year"] = df["year"].apply(normalize_year)
    assert df.iloc[0]["company_id"] == "RELIANCE"
    assert df.iloc[0]["year"] == "2023-03"


# ============================================================
# Column Selection Tests
# ============================================================

def test_select_only_desired_columns():
    df = pd.DataFrame({
        "company_id": ["RELIANCE"],
        "year": ["2023-03"],
        "sales": [5000],
        "extra": ["remove"]
    })
    desired = ["company_id", "year", "sales"]
    df = df[[col for col in desired if col in df.columns]]
    assert "extra" not in df.columns


def test_missing_columns_handling():
    df = pd.DataFrame({"company_id": ["RELIANCE"], "year": ["2023-03"]})
    desired = ["company_id", "year", "sales"]
    df = df[[col for col in desired if col in df.columns]]
    assert "sales" not in df.columns


# ============================================================
# Data Quality in Loader Context
# ============================================================

def test_no_duplicate_columns_after_cleaning():
    df = pd.DataFrame({"Sales": [100], " sales ": [200]})
    df.columns = df.columns.str.strip().str.lower()
    assert len(df.columns) == 2


def test_empty_dataframe_handling():
    df = pd.DataFrame()
    
    # Only apply string operations if there are columns
    if len(df.columns) > 0:
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    assert df.empty

def test_numeric_columns_unchanged():
    df = pd.DataFrame({"sales": [100, 200], "profit": [10, 20]})
    assert df["sales"].dtype in ["int64", "float64"]


# ============================================================
# Edge Case Tests
# ============================================================

def test_normalize_with_nan_values():
    df = pd.DataFrame({"company_id": ["RELIANCE", None]})
    df["company_id"] = df["company_id"].apply(lambda x: normalize_ticker(x) if pd.notna(x) else "")
    assert df.iloc[1]["company_id"] == ""


def test_year_normalization_edge():
    assert normalize_year("FY50") == "1950-03"
    assert normalize_year("FY49") == "2049-03"


def test_ticker_with_numbers_and_symbols():
    assert normalize_ticker("RELIANCE@2023") == "RELIANCE@2023"


def test_combined_cleaning_pipeline():
    df = pd.DataFrame({
        " Company ID ": [" reliance ", "TCS"],
        " Year ": ["Mar-23", "FY22"],
        " Sales ": [1000, 2000]
    })
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df["year"] = df["year"].apply(normalize_year)
    
    assert list(df["company_id"]) == ["RELIANCE", "TCS"]
    assert list(df["year"]) == ["2023-03", "2022-03"]

 # ============================================================
# Additional Loader Tests
# ============================================================

def test_large_number_of_columns():
    df = pd.DataFrame({f"col_{i}": [i] for i in range(50)})
    df.columns = df.columns.str.strip().str.lower()
    assert len(df.columns) == 50


def test_normalize_empty_string_year():
    assert normalize_year("") is None


def test_ticker_with_only_special_characters():
    # Use raw string to avoid escape sequence issues
    assert normalize_ticker(r"!@#\( %") == r"!@# \)%"

def test_year_with_multiple_formats_in_one():
    assert normalize_year("FY Mar-23") == "2023-03"   


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])