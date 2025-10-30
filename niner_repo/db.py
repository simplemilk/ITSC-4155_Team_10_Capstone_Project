import sqlite3
import click
import os
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

def get_db():
    """Get database connection."""
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE')
        if not db_path:
            db_path = os.path.join(current_app.instance_path, 'niner_finance.db')
        
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def create_demo_user():
    """Create a demo user with sample data"""
    try:
        db_path = current_app.config.get('DATABASE')
        if not db_path:
            db_path = os.path.join(current_app.instance_path, 'niner_finance.db')
        
        # Demo user credentials
        demo_username = "demo"
        demo_email = "demo@ninerfinance.com"
        demo_password = "demo123"
        
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Check if demo user already exists
            existing_user = conn.execute(
                "SELECT id FROM user WHERE username = ?", (demo_username,)
            ).fetchone()
            
            if existing_user:
                print("✅ Demo user already exists!")
                return existing_user['id']
            
            # Create demo user
            password_hash = generate_password_hash(demo_password)
            cursor = conn.execute(
                "INSERT INTO user (username, email, password) VALUES (?, ?, ?)",
                (demo_username, demo_email, password_hash)
            )
            user_id = cursor.lastrowid
            
            conn.commit()
            print("✅ Demo user created successfully!")
            print(f"   Username: {demo_username}")
            print(f"   Password: {demo_password}")
            
            return user_id
            
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        return None

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database with schema files."""
    db_path = current_app.config.get('DATABASE')
    if not db_path:
        db_path = os.path.join(current_app.instance_path, 'niner_finance.db')
    
    # Ensure the instance directory exists
    os.makedirs(current_app.instance_path, exist_ok=True)
    
    # Read and execute schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        with sqlite3.connect(db_path) as conn:
            conn.executescript(schema)
        click.echo('Main schema loaded.')
    
    # Read and execute budget_schema.sql if it exists
    budget_schema_path = os.path.join(os.path.dirname(__file__), 'budget_schema.sql')
    if os.path.exists(budget_schema_path):
        with open(budget_schema_path, 'r') as f:
            budget_schema = f.read()
        with sqlite3.connect(db_path) as conn:
            conn.executescript(budget_schema)
        click.echo('Budget schema loaded.')
    
    click.echo('Initialized the database.')
    
    # Create demo user after initializing
    create_demo_user()

@click.command('create-demo')
@with_appcontext
def create_demo_command():
    """Create demo user with sample data."""
    result = create_demo_user()
    if result:
        click.echo('Demo user created successfully!')
    else:
        click.echo('Failed to create demo user.')

def init_app(app):
    """Initialize database with Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_demo_command)
    
    # Set the database path in config if not already set
    if 'DATABASE' not in app.config:
        app.config['DATABASE'] = os.path.join(app.instance_path, 'niner_finance.db')