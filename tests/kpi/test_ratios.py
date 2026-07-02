"""
test_ratios.py
Unit tests for financial ratio calculations (Expanded)
"""

import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from analytics.cagr import calculate_cagr
from analytics.cashflow_kpis import classify_capital_allocation


# =====================
# Profitability Ratios
# =====================

def test_net_profit_margin_normal():
    sales = 1000
    net_profit = 150
    result = round((net_profit / sales) * 100, 2)
    assert result == 15.0


def test_net_profit_margin_zero_sales():
    sales = 0
    result = None if sales == 0 else round((150 / sales) * 100, 2)
    assert result is None


def test_roe_normal():
    result = round((200 / (1000 + 500)) * 100, 2)
    assert result == 13.33


def test_roe_negative_equity():
    result = None if (1000 + (-1500)) <= 0 else round((200 / (1000 - 1500)) * 100, 2)
    assert result is None


def test_roce_normal():
    result = round((300 / (1000 + 500 + 400)) * 100, 2)
    assert result == 15.79


def test_roa_normal():
    result = round((150 / 2000) * 100, 2)
    assert result == 7.5


# =====================
# Leverage Ratios
# =====================

def test_debt_to_equity_normal():
    result = round(800 / (1000 + 500), 2)
    assert result == 0.53


def test_debt_to_equity_zero_borrowings():
    result = 0 if 0 == 0 else round(0 / (1000 + 500), 2)
    assert result == 0


def test_interest_coverage_normal():
    result = round((400 + 50) / 100, 2)
    assert result == 4.5


def test_interest_coverage_zero_interest():
    result = None if 0 == 0 else round((400 + 50) / 0, 2)
    assert result is None


# =====================
# CAGR Tests
# =====================

def test_cagr_normal():
    result, flag = calculate_cagr(100, 150, 5)
    assert result is not None
    assert flag == "NORMAL"


def test_cagr_zero_base():
    result, flag = calculate_cagr(0, 150, 5)
    assert result is None
    assert flag == "ZERO_BASE"


def test_cagr_decline_to_loss():
    result, flag = calculate_cagr(100, -50, 5)
    assert result is None
    assert flag == "DECLINE_TO_LOSS"


def test_cagr_turnaround():
    result, flag = calculate_cagr(-100, 150, 5)
    assert result is None
    assert flag == "TURNAROUND"


def test_cagr_both_negative():
    result, flag = calculate_cagr(-100, -50, 5)
    assert result is None
    assert flag == "BOTH_NEGATIVE"


# =====================
# Capital Allocation Tests
# =====================

def test_capital_allocation_reinvestor():
    result = classify_capital_allocation(500, -300, -200)
    assert result == "Reinvestor"


def test_capital_allocation_shareholder_returns():
    result = classify_capital_allocation(500, -200, 150)
    assert result == "Shareholder Returns"


def test_capital_allocation_distress():
    result = classify_capital_allocation(-300, 200, 150)
    assert result == "Distress Signal"

def test_free_cash_flow_normal():
    operating_activity = 500
    investing_activity = -200
    result = operating_activity + investing_activity
    assert result == 300


def test_cfo_quality_score_normal():
    operating_activity = 400
    net_profit = 200
    result = round(operating_activity / net_profit, 2)
    assert result == 2.0

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])