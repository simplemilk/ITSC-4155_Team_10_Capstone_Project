"""Tests for transaction functionality."""

import pytest
from datetime import datetime, date
from db import get_db

class TestTransactions:
    """Test cases for transaction management."""
    
    def test_transactions_index(self, logged_in_user):
        """Test transactions index page."""
        response = logged_in_user.get('/transactions')
        assert response.status_code == 200
        assert b'Transactions' in response.data
    
    def test_add_transaction_get(self, logged_in_user):
        """Test GET request to add transaction."""
        response = logged_in_user.get('/transactions/add')
        assert response.status_code == 200
        assert b'Add Transaction' in response.data
    
    def test_add_expense_transaction(self, logged_in_user, app):
        """Test adding an expense transaction."""
        response = logged_in_user.post('/transactions/add', data={
            'type': 'expense',
            'amount': '25.50',
            'category': 'Food',
            'description': 'Lunch',
            'date': date.today().isoformat()
        })
        
        assert response.status_code == 302  # Redirect after creation
        
        # Verify transaction was created
        with app.app_context():
            db = get_db()
            transaction = db.execute('''
                SELECT * FROM transactions 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                AND description = 'Lunch'
            ''').fetchone()
            assert transaction is not None
            assert float(transaction['amount']) == 25.50
            assert transaction['type'] == 'expense'
    
    def test_add_income_transaction(self, logged_in_user, app):
        """Test adding an income transaction."""
        response = logged_in_user.post('/transactions/add', data={
            'type': 'income',
            'amount': '500.00',
            'category': 'Income',
            'description': 'Part-time job',
            'date': date.today().isoformat()
        })
        
        assert response.status_code == 302
        
        # Verify transaction was created
        with app.app_context():
            db = get_db()
            transaction = db.execute('''
                SELECT * FROM transactions 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                AND description = 'Part-time job'
            ''').fetchone()
            assert transaction is not None
            assert transaction['type'] == 'income'
    
    def test_transaction_validation(self, logged_in_user):
        """Test transaction form validation."""
        # Test negative amount
        response = logged_in_user.post('/transactions/add', data={
            'type': 'expense',
            'amount': '-10.00',
            'category': 'Food',
            'description': 'Invalid',
            'date': date.today().isoformat()
        })
        assert response.status_code == 200  # Should stay on form
        
        # Test zero amount
        response = logged_in_user.post('/transactions/add', data={
            'type': 'expense',
            'amount': '0.00',
            'category': 'Food',
            'description': 'Invalid',
            'date': date.today().isoformat()
        })
        assert response.status_code == 200
    
    def test_edit_transaction(self, logged_in_user, sample_data, app):
        """Test editing a transaction."""
        # First, get a transaction ID
        with app.app_context():
            db = get_db()
            transaction = db.execute('''
                SELECT id FROM transactions 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                LIMIT 1
            ''').fetchone()
            transaction_id = transaction['id']
        
        # Test GET request
        response = logged_in_user.get(f'/transactions/{transaction_id}/edit')
        assert response.status_code == 200
        
        # Test POST request
        response = logged_in_user.post(f'/transactions/{transaction_id}/edit', data={
            'type': 'expense',
            'amount': '35.00',
            'category': 'Food',
            'description': 'Updated lunch',
            'date': date.today().isoformat()
        })
        assert response.status_code == 302
        
        # Verify update
        with app.app_context():
            db = get_db()
            updated = db.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,)).fetchone()
            assert updated['description'] == 'Updated lunch'
            assert float(updated['amount']) == 35.00
    
    def test_delete_transaction(self, logged_in_user, sample_data, app):
        """Test deleting a transaction."""
        # Get a transaction ID
        with app.app_context():
            db = get_db()
            transaction = db.execute('''
                SELECT id FROM transactions 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                LIMIT 1
            ''').fetchone()
            transaction_id = transaction['id']
        
        # Delete transaction
        response = logged_in_user.post(f'/transactions/{transaction_id}/delete')
        assert response.status_code == 302
        
        # Verify deletion
        with app.app_context():
            db = get_db()
            deleted = db.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,)).fetchone()
            assert deleted is None
    
    def test_transaction_filtering(self, logged_in_user, sample_data):
        """Test transaction filtering functionality."""
        # Test filter by type
        response = logged_in_user.get('/transactions?type=expense')
        assert response.status_code == 200
        
        # Test filter by category
        response = logged_in_user.get('/transactions?category=Food')
        assert response.status_code == 200
        
        # Test date range filter
        response = logged_in_user.get('/transactions?start_date=2024-01-01&end_date=2024-12-31')
        assert response.status_code == 200
    
    def test_transaction_api(self, logged_in_user, sample_data):
        """Test transaction API endpoints."""
        # Test monthly totals API
        response = logged_in_user.get('/api/transactions/monthly-totals')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data is not None
        assert 'income' in data
        assert 'expenses' in data