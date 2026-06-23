import sqlite3

conn = sqlite3.connect('db/nifty100.db')
cursor = conn.cursor()

# Delete orphan records from profitandloss
query = """
    DELETE FROM profitandloss 
    WHERE company_id NOT IN (SELECT id FROM companies)
"""

cursor.execute(query)
deleted = cursor.rowcount
conn.commit()
conn.close()

print(f" Successfully removed {deleted} orphan records from profitandloss table.")