import sqlite3
import os

def init_priorities_db():
    """Initialize the priorities tables"""
    db_path = os.path.join('instance', 'niner_finance.sqlite')
    
    # Read and execute the priorities schema
    with open('priorities_schema.sql', 'r') as f:
        schema = f.read()
    
    conn = sqlite3.connect(db_path)
    conn.executescript(schema)
    conn.commit()
    conn.close()
    
    print("Priorities database initialized successfully!")

if __name__ == '__main__':
    init_priorities_db()