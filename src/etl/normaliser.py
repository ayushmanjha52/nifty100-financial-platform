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
        Cleaned uppercase ticker without leading/trailing whitespace
    """
    if not isinstance(ticker, str):
        return ""
    
    cleaned = ticker.strip().upper()
    return cleaned


def normalize_year(year_label: str) -> Optional[str]:
    """
    Convert various year formats to standard 'YYYY-MM' format.
    Supports months like Mar, Dec, FY, etc.
    
    Only accepts years between 1950 and 2050.
    
    Examples:
        "Mar-23"   -> "2023-03"
        "Dec-22"   -> "2022-12"
        "FY23"     -> "2023-03"
        "2022-03"  -> "2022-03"
        "FY2023"   -> "2023-03"
    
    Args:
        year_label: Raw year string from dataset
        
    Returns:
        Standardised year in 'YYYY-MM' format or None if invalid
    """
    if not isinstance(year_label, str):
        return None
    
    text = year_label.strip().upper()
    
    if not text:
        return None
    
    # Month mapping
    month_map = {
        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
        'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12',
        'FY': '03'
    }
    
    # Find month (optional)
    month_match = re.search(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|FY)', text)
    
    # Find year (2 or 4 digits)
    year_match = re.search(r'(\d{2,4})', text)
    
    if not year_match:
        return None
    
    year_str = year_match.group(1)
    
    # Convert 2-digit year to 4-digit
    if len(year_str) == 2:
        year = int(year_str)
        if year >= 50:
            year += 1900
        else:
            year += 2000
    else:
        year = int(year_str)
    
    # Only accept years between 1950 and 2050
    if year < 1950 or year > 2050:
        return None
    
    # Get month
    if month_match:
        month_key = month_match.group(1)
        month = month_map.get(month_key, '03')
    else:
        month = '03'  # Default to March
    
    return f"{year}-{month}"