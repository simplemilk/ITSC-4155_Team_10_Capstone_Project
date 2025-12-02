#!/usr/bin/env python3
"""
Apply investments schema to the project's sqlite database and insert sample data.
"""
import os
import sqlite3
import sys


def get_db_path():
    # Use instance folder to match the app's database location
    base = os.path.dirname(os.path.abspath(__file__))
    instance_dir = os.path.join(base, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    return os.path.join(instance_dir, 'niner_finance.sqlite')


def apply_schema(db_path):
    print(f"Applying investments schema to: {db_path}")
    
    # Create the database if it doesn't exist
    if not os.path.exists(db_path):
        print("Database not found; creating new database...")
        # Will be created when we connect

    # Support both 'investments_schema.sql' and legacy 'investments_schema' filenames
    schema_dir = os.path.dirname(__file__)
    candidates = ['investments_schema.sql', 'investments_schema']
    schema_file = None
    for c in candidates:
        p = os.path.join(schema_dir, c)
        if os.path.exists(p):
            schema_file = p
            break
    
    if not schema_file:
        print(f"Schema file not found. Looked for: {candidates}")
        print("Creating tables manually...")
        # Fallback: create tables manually
        return create_tables_manually(db_path)

    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        # Enable foreign keys
        conn.execute('PRAGMA foreign_keys = ON;')
        conn.executescript(schema_sql)
        conn.commit()
        print("✓ Schema applied successfully.")
    except Exception as e:
        print(f"❌ Error applying schema: {e}")
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
        print("✓ Inserted sample asset types and investments.")
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        return False
    finally:
        conn.close()

    return True


def create_tables_manually(db_path):
    """Fallback method to create tables if schema file is missing"""
    print("Creating investment tables manually...")
    
    conn = sqlite3.connect(db_path)
    try:
        conn.execute('PRAGMA foreign_keys = ON;')
        
        # Create asset_types table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS asset_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create investments table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                asset_type_id INTEGER,
                exchange TEXT,
                currency TEXT DEFAULT 'USD',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asset_type_id) REFERENCES asset_types (id)
            )
        ''')
        
        # Create positions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                investment_id INTEGER NOT NULL,
                quantity REAL NOT NULL DEFAULT 0,
                avg_cost REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (investment_id) REFERENCES investments (id),
                UNIQUE(user_id, investment_id)
            )
        ''')
        
        # Create investment_transactions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS investment_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                investment_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('buy', 'sell')),
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (investment_id) REFERENCES investments (id)
            )
        ''')
        
        conn.commit()
        
        # Insert sample data
        cursor = conn.cursor()
        asset_types = [
            ('Equity', 'Individual company stocks'),
            ('Bond', 'Fixed income securities'),
            ('ETF', 'Exchange-traded funds'),
            ('Crypto', 'Cryptocurrencies'),
            ('Cash', 'Cash and money market')
        ]
        
        for name, desc in asset_types:
            cursor.execute('INSERT OR IGNORE INTO asset_types (name, description) VALUES (?, ?)', (name, desc))
        
        # Get asset type IDs and insert sample investments
        cursor.execute("SELECT id FROM asset_types WHERE name = 'Equity'")
        equity_row = cursor.fetchone()
        if equity_row:
            equity_id = equity_row[0]
            cursor.execute('''
                INSERT OR IGNORE INTO investments (ticker, name, asset_type_id, exchange, currency) 
                VALUES (?, ?, ?, ?, ?)
            ''', ('AAPL', 'Apple Inc.', equity_id, 'NASDAQ', 'USD'))
            
            cursor.execute('''
                INSERT OR IGNORE INTO investments (ticker, name, asset_type_id, exchange, currency) 
                VALUES (?, ?, ?, ?, ?)
            ''', ('GOOGL', 'Alphabet Inc.', equity_id, 'NASDAQ', 'USD'))
        
        cursor.execute("SELECT id FROM asset_types WHERE name = 'ETF'")
        etf_row = cursor.fetchone()
        if etf_row:
            etf_id = etf_row[0]
            cursor.execute('''
                INSERT OR IGNORE INTO investments (ticker, name, asset_type_id, exchange, currency) 
                VALUES (?, ?, ?, ?, ?)
            ''', ('VOO', 'Vanguard S&P 500 ETF', etf_id, 'NYSE', 'USD'))
        
        cursor.execute("SELECT id FROM asset_types WHERE name = 'Crypto'")
        crypto_row = cursor.fetchone()
        if crypto_row:
            crypto_id = crypto_row[0]
            cursor.execute('''
                INSERT OR IGNORE INTO investments (ticker, name, asset_type_id, exchange, currency) 
                VALUES (?, ?, ?, ?, ?)
            ''', ('BTC', 'Bitcoin', crypto_id, 'Coinbase', 'USD'))
        
        conn.commit()
        conn.close()
        
        print("✓ Tables created and sample data inserted successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False


def init_investments_db():
    """Compatibility wrapper expected by app.py: returns True on success."""
    db_path = get_db_path()
    return apply_schema(db_path)


if __name__ == '__main__':
    db_path = get_db_path()
    print(f"\n📊 Initializing investments database...")
    print(f"Database path: {db_path}")
    ok = apply_schema(db_path)
    if ok:
        print('\n✅ Investments schema installation complete')
        sys.exit(0)
    else:
        print('\n❌ Investments schema installation failed')
        sys.exit(1)
