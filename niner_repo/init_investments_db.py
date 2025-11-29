import sqlite3
import os

def init_investments_db():
    """Initialize the investments database tables"""
    # Get the correct database path from the app directory
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'niner_finance.sqlite')
    
    print(f"📂 Initializing investments database at: {db_path}")
    
    # Create instance directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # Execute the schema directly
    print("📝 Creating investments tables...")
    conn.executescript('''
        -- Investment Portfolio Schema

        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            asset_name TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            ticker_symbol TEXT,
            quantity REAL NOT NULL,
            purchase_price REAL NOT NULL,
            purchase_date TEXT NOT NULL,
            current_price REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
            CHECK (quantity > 0),
            CHECK (purchase_price > 0)
        );

        CREATE INDEX IF NOT EXISTS idx_investments_user_id ON investments(user_id);
        CREATE INDEX IF NOT EXISTS idx_investments_asset_type ON investments(asset_type);
        CREATE INDEX IF NOT EXISTS idx_investments_ticker ON investments(ticker_symbol);

        CREATE TABLE IF NOT EXISTS investment_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            icon TEXT,
            color TEXT,
            description TEXT
        );

        INSERT OR IGNORE INTO investment_types (name, icon, color, description) VALUES
        ('stock', 'fa-chart-line', '#3498db', 'Individual company stocks'),
        ('bond', 'fa-landmark', '#9b59b6', 'Government and corporate bonds'),
        ('crypto', 'fa-bitcoin', '#f39c12', 'Cryptocurrency'),
        ('etf', 'fa-layer-group', '#1abc9c', 'Exchange-Traded Funds'),
        ('mutual_fund', 'fa-coins', '#27ae60', 'Mutual Funds'),
        ('real_estate', 'fa-home', '#e67e22', 'Real Estate Investment'),
        ('commodity', 'fa-gem', '#e74c3c', 'Gold, Silver, Oil, etc.'),
        ('other', 'fa-ellipsis-h', '#95a5a6', 'Other investments');

        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            snapshot_date TEXT NOT NULL,
            total_value REAL NOT NULL,
            total_cost REAL NOT NULL,
            total_gain_loss REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_user_date ON portfolio_snapshots(user_id, snapshot_date);
    ''')
    
    conn.commit()
    
    # Verify tables were created
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%investment%'"
    ).fetchall()
    
    conn.close()
    
    if len(tables) >= 2:
        print(f"✓ Investments database initialized successfully!")
        print(f"  Created tables: {', '.join([t[0] for t in tables])}")
        return True
    else:
        print(f"❌ Failed to create investments tables")
        return False

if __name__ == '__main__':
    init_investments_db()