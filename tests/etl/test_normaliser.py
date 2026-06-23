"""
test_normaliser.py
Comprehensive Unit Tests for normaliser.py
Target: 35+ tests for Sprint 1
"""

import pytest
from etl.normaliser import normalize_ticker, normalize_year


# ============================================================
# normalize_ticker() - Basic & Edge Cases
# ============================================================

def test_normalize_ticker_basic():
    assert normalize_ticker("reliance") == "RELIANCE"
    assert normalize_ticker("TCS") == "TCS"


def test_normalize_ticker_whitespace():
    assert normalize_ticker("  reliance  ") == "RELIANCE"
    assert normalize_ticker("\tTCS\n") == "TCS"
    assert normalize_ticker("   ") == ""


def test_normalize_ticker_empty_and_none():
    assert normalize_ticker("") == ""
    assert normalize_ticker(None) == ""


def test_normalize_ticker_mixed_case():
    assert normalize_ticker("ReLiAnCe") == "RELIANCE"
    assert normalize_ticker("tcs India Ltd") == "TCS INDIA LTD"


def test_normalize_ticker_with_numbers_and_symbols():
    assert normalize_ticker("RELIANCE123") == "RELIANCE123"
    assert normalize_ticker("TCS@2023") == "TCS@2023"
    assert normalize_ticker("ADANI!") == "ADANI!"


def test_normalize_ticker_non_string_input():
    assert normalize_ticker(12345) == ""
    assert normalize_ticker([]) == ""
    assert normalize_ticker({}) == ""
    assert normalize_ticker(3.14) == ""


# ============================================================
# normalize_year() - Various Formats
# ============================================================

def test_normalize_year_standard_formats():
    assert normalize_year("Mar-23") == "2023-03"
    assert normalize_year("Dec-22") == "2022-12"
    assert normalize_year("FY23") == "2023-03"
    assert normalize_year("2023-03") == "2023-03"


def test_normalize_year_two_digit_years():
    assert normalize_year("Dec-05") == "2005-12"
    assert normalize_year("FY19") == "2019-03"
    assert normalize_year("Mar-99") == "1999-03"


def test_normalize_year_full_year_formats():
    assert normalize_year("Dec-2022") == "2022-12"
    assert normalize_year("FY2023") == "2023-03"


def test_normalize_year_invalid_inputs():
    assert normalize_year("invalid") is None
    assert normalize_year("") is None
    assert normalize_year("   ") is None
    assert normalize_year(None) is None
    assert normalize_year("abc123") is None


def test_normalize_year_edge_years():
    assert normalize_year("FY50") == "1950-03"
    assert normalize_year("FY49") == "2049-03"
    assert normalize_year("Jan-00") == "2000-01"


def test_normalize_year_whitespace():
    assert normalize_year("  Mar-23  ") == "2023-03"
    assert normalize_year("\tFY22\n") == "2022-03"


def test_normalize_year_case_insensitive():
    assert normalize_year("dec-22") == "2022-12"
    assert normalize_year("fy23") == "2023-03"
    assert normalize_year("MAR-23") == "2023-03"


def test_normalize_year_various_months():
    assert normalize_year("Jan-23") == "2023-01"
    assert normalize_year("Jun-22") == "2022-06"
    assert normalize_year("Dec-21") == "2021-12"


def test_normalize_year_non_string():
    assert normalize_year(2023) is None
    assert normalize_year([]) is None
    assert normalize_year({}) is None


# ============================================================
# Integration Style Tests
# ============================================================

def test_normalize_ticker_and_year_combined():
    ticker = normalize_ticker("  reliance  ")
    year = normalize_year("Mar-23")
    assert ticker == "RELIANCE"
    assert year == "2023-03"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])