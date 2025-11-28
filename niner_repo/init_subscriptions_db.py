import sqlite3
import os

def init_subscriptions_db():
    """Initialize the subscriptions database tables"""
    # Get the CORRECT database path - same as app.py uses
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'niner_finance.sqlite')
    
    print(f"📂 Initializing subscriptions database at: {db_path}")
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"⚠️  Database file not found at: {db_path}")
        print(f"   Creating new database file...")
    
    conn = sqlite3.connect(db_path)
    
    # Execute the schema directly
    print("📝 Creating subscriptions tables...")
    conn.executescript('''
        -- Subscriptions and Recurring Payments Schema

        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            frequency TEXT NOT NULL,
            category TEXT,
            next_billing_date TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            is_active INTEGER DEFAULT 1,
            auto_detected INTEGER DEFAULT 0,
            transaction_id INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
        CREATE INDEX IF NOT EXISTS idx_subscriptions_next_billing ON subscriptions(next_billing_date);
        CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(is_active);

        CREATE TABLE IF NOT EXISTS subscription_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            icon TEXT,
            color TEXT
        );

        INSERT OR IGNORE INTO subscription_categories (name, icon, color) VALUES
        ('Streaming', 'fa-tv', '#e74c3c'),
        ('Music', 'fa-music', '#9b59b6'),
        ('Software', 'fa-laptop-code', '#3498db'),
        ('Gaming', 'fa-gamepad', '#e67e22'),
        ('Fitness', 'fa-dumbbell', '#27ae60'),
        ('News', 'fa-newspaper', '#34495e'),
        ('Cloud Storage', 'fa-cloud', '#1abc9c'),
        ('Utilities', 'fa-bolt', '#f39c12'),
        ('Insurance', 'fa-shield-alt', '#16a085'),
        ('Other', 'fa-ellipsis-h', '#95a5a6');
    ''')
    
    conn.commit()
    
    # Verify tables were created
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%subscription%'"
    ).fetchall()
    
    conn.close()
    
    if len(tables) >= 2:
        print(f"✓ Subscriptions database initialized successfully!")
        print(f"  Created tables: {', '.join([t[0] for t in tables])}")
        print(f"  Database location: {db_path}")
        return True
    else:
        print(f"❌ Failed to create subscriptions tables")
        return False

if __name__ == '__main__':
    init_subscriptions_db()