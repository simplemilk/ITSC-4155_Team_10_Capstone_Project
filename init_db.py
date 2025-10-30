import os
import sqlite3
from niner_repo import create_app

def init_database():
    app = create_app()
    
    with app.app_context():
        db_path = app.config['DATABASE']
        
        # Ensure instance directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Read and execute schema.sql
        with open('niner_repo/schema.sql', 'r') as f:
            schema = f.read()
        
        with sqlite3.connect(db_path) as conn:
            conn.executescript(schema)
        
        # Read and execute budget_schema.sql
        try:
            with open('niner_repo/budget_schema.sql', 'r') as f:
                budget_schema = f.read()
            
            with sqlite3.connect(db_path) as conn:
                conn.executescript(budget_schema)
        except FileNotFoundError:
            print("budget_schema.sql not found, skipping...")
        
        print(f"Database initialized at: {db_path}")

if __name__ == '__main__':
    init_database()