import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    """Get database connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Initialize database with Flask app."""
    app.teardown_appcontext(close_db)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database with schema files."""
    db_path = current_app.config['DATABASE']
    
    # Create database if it doesn't exist
    if not os.path.exists(db_path):
        # Read and execute schema.sql
        with open('niner_repo/schema.sql', 'r') as f:
            schema = f.read()
        
        with sqlite3.connect(db_path) as conn:
            conn.executescript(schema)
        
        # Read and execute budget_schema.sql if it exists
        try:
            with open('niner_repo/budget_schema.sql', 'r') as f:
                budget_schema = f.read()
            with sqlite3.connect(db_path) as conn:
                conn.executescript(budget_schema)
        except FileNotFoundError:
            pass

    click.echo('Initialized the database.')

def init_app(app):
    """Initialize database with Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

