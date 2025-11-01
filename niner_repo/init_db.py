import os
import sqlite3

# Simple database setup
instance_dir = 'instance'
os.makedirs(instance_dir, exist_ok=True)
db_path = os.path.join(instance_dir, 'niner_finance.db')

print(f"Setting up database at: {db_path}")

with sqlite3.connect(db_path) as conn:
    # Essential tables only
    tables_sql = [
        '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        
        '''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'expense',
            date DATE NOT NULL DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            category TEXT NOT NULL,
            date DATE NOT NULL DEFAULT CURRENT_DATE,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )'''
    ]
    
    for sql in tables_sql:
        try:
            conn.execute(sql)
            print("✅ Table created/verified")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Views
    try:
        conn.execute('DROP VIEW IF EXISTS v_active_income')
        conn.execute('CREATE VIEW v_active_income AS SELECT * FROM income WHERE is_active = 1')
        print("✅ View created")
    except Exception as e:
        print(f"❌ View error: {e}")
    
    conn.commit()

print("Database setup complete!")