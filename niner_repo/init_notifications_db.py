"""
Initialize Notifications Database Tables
Run this script to set up the notifications system
"""

import sqlite3
import os

def get_db_path():
    """Get the database path"""
    return os.path.join(os.path.dirname(__file__), 'instance', 'niner_finance.sqlite')

def init_notifications_db():
    """Initialize the notifications database tables"""
    db_path = get_db_path()
    
    print("\n🔔 Initializing Notifications Database...")
    print(f"📍 Database: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run init_db.py first.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read and execute schema
        schema_file = os.path.join(os.path.dirname(__file__), 'notifications_schema.sql')
        
        if not os.path.exists(schema_file):
            print(f"❌ Schema file not found: {schema_file}")
            return False
        
        print(f"📄 Loading schema from: {schema_file}")
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
            conn.executescript(schema_sql)
        
        conn.commit()
        conn.close()
        
        print("✅ Notifications database initialized successfully!")
        print("   • notifications table created")
        print("   • notification_settings table created")
        print("   • Views and triggers created")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing notifications database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = init_notifications_db()
    if success:
        print("\n✅ You can now use the notification system!")
        print("   • Notification Center: /notifications")
        print("   • Settings: /notifications/settings")
    else:
        print("\n❌ Initialization failed. Please check the errors above.")