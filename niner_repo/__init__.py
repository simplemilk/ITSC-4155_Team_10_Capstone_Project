import os
import sqlite3
from flask import Flask

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # Set default configuration
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'niner_finance.sqlite'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize the database
    from . import db
    db.init_app(app)

    # Register blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    from . import transactions
    app.register_blueprint(transactions.bp)
    
    # Add URL rules
    app.add_url_rule('/', endpoint='index', view_func=transactions.show_visuals)

    return app

def init_db_command(app):
    """Initialize the database with schema files."""
    with app.app_context():
        db_path = app.config['DATABASE']
        
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
            
            print("Database initialized successfully!")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)