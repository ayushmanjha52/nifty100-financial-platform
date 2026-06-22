"""
normaliser.py
Helper functions to clean and standardise company tickers and year labels.
"""

import re
from typing import Optional


def normalize_ticker(ticker: str) -> str:
    """
    Clean and standardise company ticker (NSE symbol).
    
    Args:
        ticker: Raw ticker string from dataset
        
    Returns:
        Cleaned uppercase ticker without whitespace
    """
    if not isinstance(ticker, str):
        return ""
    
    # Remove whitespace and convert to uppercase
    cleaned = ticker.strip().upper()
    return cleaned


def normalize_year(year_label: str) -> Optional[str]:
    """
    Convert various year formats to standard 'YYYY-MM' format.
    
    Examples:
        'Mar-23' -> '2023-03'
        'FY23'   -> '2023-03'
        '2023'   -> '2023-03'
    
    Args:
        year_label: Raw year string from dataset
        
    Returns:
        Standardised year in 'YYYY-MM' format or None if invalid
    """
    if not isinstance(year_label, str):
        return None
    
    year_label = year_label.strip()
    
    # Pattern for 'Mar-23', 'FY23', etc.
    pattern = r'(?:FY|Mar|Dec)?[\s-]*(\d{2,4})'
    match = re.search(pattern, year_label, re.IGNORECASE)
    
    if not match:
        return None
    
    year_str = match.group(1)
    
    # Convert 2-digit year to 4-digit
    if len(year_str) == 2:
        year = int(year_str)
        if year >= 50:  # Assume 1950-2049 range
            year += 1900
        else:
            year += 2000
    else:
        year = int(year_str)
    
    # Default to March (financial year end for most Indian companies)
    return f"{year}-03"