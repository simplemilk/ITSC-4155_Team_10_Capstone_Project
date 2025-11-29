"""Pytest configuration and fixtures for Niner Finance tests."""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
import sys
# Ensure repo root is on path so package imports work (tests/ -> niner_repo -> repo root)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from niner_repo import create_app
from db import get_db, init_db
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    """Create and configure a test app instance."""
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        init_db()
        # Register additional blueprints used by tests (investments, portfolio)
        try:
            from niner_repo import investments, portfolio
            app.register_blueprint(investments.bp)
            app.register_blueprint(portfolio.bp)
        except Exception:
            # If those modules aren't available or require extra DB schema, tests will manage schema themselves
            pass
        
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    """Authentication helper fixture."""
    class AuthActions:
        def __init__(self, client):
            self._client = client
            
        def register(self, username='testuser', email='test@uncc.edu', 
                    password='testpassword'):
            """Register a new user."""
            # Directly insert a user into the test database to avoid depending on the
            # application registration form (which requires additional schema fields).
            with self._client.application.app_context():
                db = get_db()
                pw_hash = generate_password_hash(password)
                db.execute('INSERT INTO user (username, email, password) VALUES (?,?,?)', (username, email, pw_hash))
                db.commit()
            return None
            
        def login(self, username='testuser', password='testpassword'):
            """Login a user."""
            return self._client.post('/auth/login', data={
                'username': username,
                'password': password
            })
            
        def logout(self):
            """Logout the current user."""
            return self._client.get('/auth/logout')
            
    return AuthActions(client)

@pytest.fixture
def logged_in_user(client, auth):
    """Create and login a test user."""
    auth.register()
    auth.login()
    return client

@pytest.fixture
def sample_data(app, logged_in_user):
    """Create sample data for testing."""
    with app.app_context():
        db = get_db()
        
        # Get user ID
        user = db.execute('SELECT id FROM users WHERE username = ?', ('testuser',)).fetchone()
        user_id = user['id']
        
        # Create sample budget
        db.execute('''
            INSERT INTO budgets (user_id, total_amount, food_budget, transportation_budget,
                               entertainment_budget, other_budget, week_start_date)
            VALUES (?, 500.00, 200.00, 150.00, 100.00, 50.00, date('now', 'weekday 0', '-7 days'))
        ''', (user_id,))
        
        # Create sample transactions
        transactions = [
            (user_id, 'expense', 25.50, 'Food', 'Lunch at cafeteria', datetime.now().date()),
            (user_id, 'expense', 45.00, 'Transportation', 'Gas for car', datetime.now().date()),
            (user_id, 'income', 200.00, 'Income', 'Part-time job', datetime.now().date()),
            (user_id, 'expense', 12.99, 'Entertainment', 'Movie ticket', datetime.now().date()),
        ]
        
        for transaction in transactions:
            db.execute('''
                INSERT INTO transactions (user_id, type, amount, category, description, date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', transaction)
        
        # Create sample financial goal
        db.execute('''
            INSERT INTO financial_goals (user_id, goal_name, description, category, 
                                       target_amount, current_amount, target_date, priority)
            VALUES (?, 'Emergency Fund', 'Save for emergencies', 'emergency', 
                    1000.00, 250.00, date('now', '+365 days'), 'high')
        ''', (user_id,))
        
        # Create sample income
        db.execute('''
            INSERT INTO income (user_id, source, amount, frequency, start_date, is_active)
            VALUES (?, 'Part-time job', 800.00, 'monthly', date('now'), 1)
        ''', (user_id,))
        
        db.commit()
        
    return user_id