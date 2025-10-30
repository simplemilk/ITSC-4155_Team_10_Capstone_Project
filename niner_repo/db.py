import sqlite3
import click
import os
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    """Get database connection."""
    if 'db' not in g:
        # Use the instance path for the database
        db_path = current_app.config.get('DATABASE')
        if not db_path:
            # Fallback to instance path
            db_path = os.path.join(current_app.instance_path, 'niner_finance.db')
        
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database with schema files."""
    # Get the database path
    db_path = current_app.config.get('DATABASE')
    if not db_path:
        db_path = os.path.join(current_app.instance_path, 'niner_finance.db')
    
    # Ensure the instance directory exists
    os.makedirs(current_app.instance_path, exist_ok=True)
    
    try:
        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema = f.read()
            
            with sqlite3.connect(db_path) as conn:
                conn.executescript(schema)
            click.echo('Main schema loaded.')
        else:
            click.echo('Warning: schema.sql not found.')
        
        # Read and execute budget_schema.sql if it exists
        budget_schema_path = os.path.join(os.path.dirname(__file__), 'budget_schema.sql')
        if os.path.exists(budget_schema_path):
            with open(budget_schema_path, 'r') as f:
                budget_schema = f.read()
            with sqlite3.connect(db_path) as conn:
                conn.executescript(budget_schema)
            click.echo('Budget schema loaded.')
        
        click.echo(f'Database initialized at: {db_path}')
        
    except Exception as e:
        click.echo(f'Error initializing database: {e}')

def init_db():
    """Initialize the database programmatically."""
    db_path = current_app.config.get('DATABASE')
    if not db_path:
        db_path = os.path.join(current_app.instance_path, 'niner_finance.db')
    
    # Ensure the instance directory exists
    os.makedirs(current_app.instance_path, exist_ok=True)
    
    try:
        # Create basic tables if schema files don't exist
        with sqlite3.connect(db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    category TEXT NOT NULL,
                    type TEXT NOT NULL DEFAULT 'expense',
                    date DATE NOT NULL DEFAULT CURRENT_DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS income (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    category TEXT NOT NULL,
                    date DATE NOT NULL DEFAULT CURRENT_DATE,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.execute('''
                CREATE VIEW IF NOT EXISTS v_active_income AS
                SELECT * FROM income WHERE is_active = 1
            ''')
            
            conn.commit()
        
        print(f'Database initialized successfully at: {db_path}')
        
    except Exception as e:
        print(f'Error initializing database: {e}')

def init_app(app):
    """Initialize database with Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    
    # Set the database path in config if not already set
    if 'DATABASE' not in app.config:
        app.config['DATABASE'] = os.path.join(app.instance_path, 'niner_finance.db')

# Remove the problematic lines that were at module level