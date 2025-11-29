
#!/usr/bin/env python3
"""
Apply investments schema to the project's sqlite database and insert sample data.
"""
import os
import sqlite3
import sys


def get_db_path():
    # Default DB used by the app
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'niner_finance.sqlite')


def apply_schema(db_path):
    print(f"Applying investments schema to: {db_path}")
    if not os.path.exists(db_path):
        print("Database not found; please create or run setup_db.py first.")
        return False

    schema_file = os.path.join(os.path.dirname(__file__), 'investments_schema.sql')
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        # Enable foreign keys
        conn.execute('PRAGMA foreign_keys = ON;')
        conn.executescript(schema_sql)
        conn.commit()
        print("Schema applied successfully.")
    except Exception as e:
        print(f"Error applying schema: {e}")
        return False

    # Insert sample asset types and sample investment for demo
    try:
        cur = conn.cursor()
        # Insert asset types if not present
        asset_types = ['Equity', 'Bond', 'ETF', 'Crypto', 'Cash']
        for name in asset_types:
            cur.execute('INSERT OR IGNORE INTO asset_types (name) VALUES (?)', (name,))

        # Insert a few investments (if not exists)
        cur.execute("SELECT id FROM asset_types WHERE name = 'Equity'")
        equity_row = cur.fetchone()
        equity_id = equity_row[0] if equity_row else None
        if equity_id:
            cur.execute("INSERT OR IGNORE INTO investments (ticker, name, asset_type_id, exchange, currency) VALUES (?,?,?,?,?)",
                        ('AAPL', 'Apple Inc.', equity_id, 'NASDAQ', 'USD'))

        cur.execute("SELECT id FROM asset_types WHERE name = 'Crypto'")
        crypto_row = cur.fetchone()
        crypto_id = crypto_row[0] if crypto_row else None
        if crypto_id:
            cur.execute("INSERT OR IGNORE INTO investments (ticker, name, asset_type_id, exchange, currency) VALUES (?,?,?,?,?)",
                        ('BTC', 'Bitcoin', crypto_id, 'Coinbase', 'USD'))

        conn.commit()
        print("Inserted sample asset types and investments (if they were missing).")
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        return False
    finally:
        conn.close()

    return True


if __name__ == '__main__':
    db_path = get_db_path()
    ok = apply_schema(db_path)
    if ok:
        print('\n✓ Investments schema installation complete')
        sys.exit(0)
    else:
        print('\n✗ Investments schema installation failed')
        sys.exit(1)
