"""
normaliser.py
Helper functions to clean and standardise company tickers and year labels.
"""

import re
from typing import Optional


def normalize_ticker(ticker: str) -> str:
    """
    Clean and standardise company ticker (NSE symbol).
    """
    if not isinstance(ticker, str):
        return ""
    
    return ticker.strip().upper()

def normalize_year(year_label: str) -> Optional[str]:
    """
    Convert various year formats to standard 'YYYY-MM' format.
    Only accepts reasonable years (1950-2050).
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
    
    # Find 2 or 4 digit year
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
        month = '03'
    
    return f"{year}-{month}"