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
        )''',
        
        '''CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            food_budget DECIMAL(10,2) DEFAULT 0,
            transportation_budget DECIMAL(10,2) DEFAULT 0,
            entertainment_budget DECIMAL(10,2) DEFAULT 0,
            other_budget DECIMAL(10,2) DEFAULT 0,
            week_start_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type VARCHAR(50) NOT NULL CHECK (type IN ('overspending', 'budget_warning', 'goal_achieved', 'subscription_reminder', 'unusual_spending')),
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
            is_read BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS notification_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            enable_overspending BOOLEAN NOT NULL DEFAULT 1,
            enable_budget_warning BOOLEAN NOT NULL DEFAULT 1,
            enable_goal_achieved BOOLEAN NOT NULL DEFAULT 1,
            enable_subscription_reminder BOOLEAN NOT NULL DEFAULT 1,
            enable_unusual_spending BOOLEAN NOT NULL DEFAULT 1,
            overspending_threshold INTEGER NOT NULL DEFAULT 100 CHECK (overspending_threshold >= 0 AND overspending_threshold <= 100),
            budget_warning_threshold INTEGER NOT NULL DEFAULT 90 CHECK (budget_warning_threshold >= 0 AND budget_warning_threshold <= 100),
            unusual_spending_multiplier DECIMAL(3,1) NOT NULL DEFAULT 2.0 CHECK (unusual_spending_multiplier >= 1.0),
            method_in_app BOOLEAN NOT NULL DEFAULT 1,
            method_email BOOLEAN NOT NULL DEFAULT 0,
            method_push BOOLEAN NOT NULL DEFAULT 0,
            daily_digest BOOLEAN NOT NULL DEFAULT 0,
            max_daily_notifications INTEGER NOT NULL DEFAULT 10 CHECK (max_daily_notifications >= 1 AND max_daily_notifications <= 50),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )'''
    ]
    
    for sql in tables_sql:
        try:
            conn.execute(sql)
            print("✅ Table created/verified")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Create indexes for notifications
    try:
        conn.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, is_read, created_at DESC)')
        print("✅ Notification index created")
    except Exception as e:
        print(f"❌ Index error: {e}")
    
    # Views
    try:
        conn.execute('DROP VIEW IF EXISTS v_active_income')
        conn.execute('CREATE VIEW v_active_income AS SELECT * FROM income WHERE is_active = 1')
        print("✅ View created")
    except Exception as e:
        print(f"❌ View error: {e}")
    
    conn.commit()

print("Database setup complete!")