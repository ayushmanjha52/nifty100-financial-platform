# Nifty 100 Financial Intelligence Platform

A comprehensive data foundation and analytics platform for Nifty 100 companies, built as part of a fintech capstone project.

## Project Overview

This project focuses on building a robust data pipeline for financial analysis of Nifty 100 companies, including:

- Data ingestion from multiple Excel sources
- Data cleaning and normalization
- SQLite database creation
- Data Quality validation (16 rules)
- Unit testing
- Load auditing

## Project Structure

nifty100_platform/
├── data/
│   ├── raw/                  # Original Excel files
│   └── processed/            # Cleaned data (if any)
├── src/
│   ├── etl/
│   │   ├── loader.py         # Main data loading script
│   │   ├── normaliser.py     # Data cleaning functions
│   │   ├── db_utils.py       # Database helper functions
│   │   └── validator.py      # Data Quality checks (16 rules)
│   └── analytics/            # Future analytics modules
├── tests/
│   └── etl/
│       ├── test_normaliser.py
│       └── test_loader.py
├── db/
│   ├── schema.sql
│   └── nifty100.db
├── output/
│   ├── load_audit.csv
│   └── validation_failures.csv
├── requirements.txt
├── Makefile
└── README.md


## Features Completed (Sprint 1)

- Full data loading from 12 source files
- Automatic generation of `load_audit.csv`
- 16 Data Quality rules with automatic cleaning of invalid values
- 39 unit tests (Normaliser + Loader)
- Proper project structure following best practices

## How to Run

### 1. Setup Environment

```bash
python -m venv venv
source venv/bin/activate          # On Windows: venv\Scripts\activate
pip install -r requirements.txt

2. Load Data

python src/etl/loader.py

3. Run Data Quality Checks

python src/etl/validator.py


4. Run Unit Tests

set PYTHONPATH=src && python -m pytest tests/ -v


Deliverables 
nifty100.db — Complete SQLite database
output/load_audit.csv — Data loading summary
output/validation_failures.csv — Data quality issues
39 passing unit tests

Tech Stack

Python 3.11+
pandas, numpy, openpyxl
SQLite
pytest
Next Steps
Build analytics and reporting layer
Add more advanced Data Quality rules
Create dashboard / API layer


Author

Ayushman Jha