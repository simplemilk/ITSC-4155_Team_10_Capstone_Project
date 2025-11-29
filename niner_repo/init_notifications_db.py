"""
Initialize Notifications Database Tables
Run this script to set up the notifications system
"""

import sqlite3
import os

def init_notifications_db():
    """Initialize the notifications database tables"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'niner_finance.sqlite')
    
    print(f"📂 Initializing notifications database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute the schema
    print("📝 Creating notifications tables...")
    
    # First, drop all existing notification-related objects
    print("🗑️  Dropping existing notification objects...")
    try:
        cursor.execute('DROP TRIGGER IF EXISTS create_default_notification_settings')
        cursor.execute('DROP TRIGGER IF EXISTS prevent_duplicate_notifications')
        cursor.execute('DROP VIEW IF EXISTS v_unread_notification_counts')
        cursor.execute('DROP VIEW IF EXISTS v_notification_summary')
        cursor.execute('DROP INDEX IF EXISTS idx_notifications_user_unread')
        cursor.execute('DROP TABLE IF EXISTS notifications')
        cursor.execute('DROP TABLE IF EXISTS notification_settings')
        conn.commit()
        print("✓ Existing objects dropped")
    except Exception as e:
        print(f"⚠️  Warning dropping objects: {e}")
    
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notifications_schema.sql')
    
    if os.path.exists(schema_path):
        try:
            with open(schema_path, 'r') as f:
                # Read the schema file
                schema_sql = f.read()
                
                # Execute the schema
                conn.executescript(schema_sql)
                conn.commit()
                print("✓ Schema file executed successfully")
        except Exception as e:
            print(f"❌ Error executing schema file: {e}")
            print("Falling back to inline table creation...")
            create_tables_inline(cursor, conn)
    else:
        # If schema file doesn't exist, create tables directly
        print("Schema file not found, creating tables directly...")
        create_tables_inline(cursor, conn)
    
    # Verify tables were created
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%notification%')"
    ).fetchall()
    
    conn.close()
    
    if len(tables) >= 2:
        print(f"✓ Notifications database initialized successfully!")
        print(f"  Created tables: {', '.join([t[0] for t in tables])}")
        return True
    else:
        print(f"❌ Failed to create notifications tables")
        print(f"  Only created: {', '.join([t[0] for t in tables]) if tables else 'none'}")
        return False

def create_tables_inline(cursor, conn):
    """Create notification tables inline (fallback method)"""
    
    # Notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
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
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
    ''')
    
    # Create index
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_notifications_user_unread 
        ON notifications(user_id, is_read, created_at DESC)
    ''')
    
    # Notification Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_settings (
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
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
    ''')
    
    # Create views
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS v_unread_notification_counts AS
        SELECT 
            user_id,
            type,
            COUNT(*) as count
        FROM notifications
        WHERE is_read = 0
        GROUP BY user_id, type
    ''')
    
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS v_notification_summary AS
        SELECT 
            n.user_id,
            COUNT(*) as total_notifications,
            SUM(CASE WHEN n.is_read = 0 THEN 1 ELSE 0 END) as unread_count,
            SUM(CASE WHEN n.severity = 'critical' AND n.is_read = 0 THEN 1 ELSE 0 END) as critical_unread,
            SUM(CASE WHEN n.severity = 'warning' AND n.is_read = 0 THEN 1 ELSE 0 END) as warning_unread,
            MAX(n.created_at) as last_notification_at
        FROM notifications n
        GROUP BY n.user_id
    ''')
    
    # Create default settings for existing users
    cursor.execute('''
        INSERT OR IGNORE INTO notification_settings (user_id)
        SELECT id FROM user
    ''')
    
    conn.commit()
    print("✓ Tables created successfully")

if __name__ == '__main__':
    init_notifications_db()