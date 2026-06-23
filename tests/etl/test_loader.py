"""
test_loader.py
Unit tests for loader.py data processing logic
"""

import pandas as pd
from etl.normaliser import normalize_ticker, normalize_year


def test_column_cleaning():
    """Test basic column name cleaning logic used in loader"""
    df = pd.DataFrame({
        "Company ID": ["RELIANCE"],
        " Year ": ["2023-03"],
        "  Sales Amount ": [5000]
    })
    
    # Simulate what the loader does
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    assert list(df.columns) == ["company_id", "year", "sales_amount"]


def test_normalize_company_id_column():
    """Test that company_id column gets normalized"""
    df = pd.DataFrame({"company_id": [" reliance ", "TCS", "adani"]})
    
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    
    assert list(df["company_id"]) == ["RELIANCE", "TCS", "ADANI"]


def test_normalize_year_column():
    """Test that year column gets normalized"""
    df = pd.DataFrame({"year": ["Mar-23", "FY22", "Dec-21"]})
    
    df["year"] = df["year"].apply(normalize_year)
    
    assert list(df["year"]) == ["2023-03", "2022-03", "2021-12"]


def test_select_desired_columns():
    """Test keeping only required columns"""
    df = pd.DataFrame({
        "company_id": ["RELIANCE"],
        "year": ["2023-03"],
        "sales": [10000],
        "extra_column": ["remove me"]
    })
    
    desired = ["company_id", "year", "sales"]
    df = df[[col for col in desired if col in df.columns]]
    
    assert "extra_column" not in df.columns
    assert list(df.columns) == ["company_id", "year", "sales"]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])