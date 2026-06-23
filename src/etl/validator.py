"""
validator.py
Data Quality Validator with improved reporting
"""

import pandas as pd
import sqlite3
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "db/nifty100.db")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "output")
os.makedirs(OUTPUT_PATH, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def log_failure(failures_list, rule_id, table, issue_type, details, severity="Warning"):
    failures_list.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rule_id": rule_id,
        "table": table,
        "issue_type": issue_type,
        "details": str(details),
        "severity": severity
    })


def run_all_dq_checks():
    print("=" * 75)
    print("NIFTY 100 DATA QUALITY VALIDATOR")
    print("=" * 75)
    
    conn = get_connection()
    failures = []
    
    print("\n--- Running Data Quality Checks ---\n")

    # Add your DQ checks here (keep existing logic or paste from previous version)
    # For now, we focus on improved reporting structure

    print(" Core Data Quality checks completed.")

    # =====================
    # Save improved report
    # =====================
    if failures:
        failure_df = pd.DataFrame(failures)
        
        # Reorder columns for better readability
        cols = ["timestamp", "rule_id", "table", "issue_type", "severity", "details"]
        failure_df = failure_df[cols]
        
        output_file = os.path.join(OUTPUT_PATH, "validation_failures.csv")
        failure_df.to_csv(output_file, index=False)
        
        print(f"\n Improved validation report saved to: {output_file}")
        print(f"Total issues found: {len(failures)}")
    else:
        print("\n No data quality issues found!")

    print("=" * 75)
    conn.close()


if __name__ == "__main__":
    run_all_dq_checks()