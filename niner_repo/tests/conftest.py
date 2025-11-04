"""Pytest configuration and fixtures for Niner Finance tests."""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from db import get_db, init_db

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
                    password='testpassword', student_id='801234567'):
            """Register a new user."""
            return self._client.post('/auth/register', data={
                'username': username,
                'email': email,
                'password': password,
                'confirm_password': password,
                'student_id': student_id,
                'security_question_1': 'What is your favorite color?',
                'security_answer_1': 'Blue',
                'security_question_2': 'What is your pet\'s name?',
                'security_answer_2': 'Max'
            })
            
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