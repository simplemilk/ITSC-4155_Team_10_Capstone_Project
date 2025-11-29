"""Tests for budget functionality."""

import pytest
from datetime import datetime, timedelta
from db import get_db

class TestBudget:
    """Test cases for budget management."""
    
    def test_budget_index_get(self, logged_in_user):
        """Test GET request to budget index."""
        response = logged_in_user.get('/budget')
        assert response.status_code == 200
        assert b'Budget' in response.data
    
    def test_budget_create_get(self, logged_in_user):
        """Test GET request to budget create page."""
        response = logged_in_user.get('/budget/create')
        assert response.status_code == 200
        assert b'Create' in response.data and b'Budget' in response.data
    
    def test_budget_create_post_success(self, logged_in_user, app):
        """Test successful budget creation."""
        response = logged_in_user.post('/budget/create', data={
            'total_amount': '500.00',
            'food_budget': '200.00',
            'transportation_budget': '150.00',
            'entertainment_budget': '100.00',
            'other_budget': '50.00'
        })
        
        assert response.status_code == 302  # Redirect after creation
        
        # Verify budget was created
        with app.app_context():
            db = get_db()
            budget = db.execute('''
                SELECT * FROM budgets 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
            ''').fetchone()
            assert budget is not None
            assert float(budget['total_amount']) == 500.00
            assert float(budget['food_budget']) == 200.00
    
    def test_budget_create_validation(self, logged_in_user):
        """Test budget creation validation."""
        # Test mismatched totals
        response = logged_in_user.post('/budget/create', data={
            'total_amount': '500.00',
            'food_budget': '200.00',
            'transportation_budget': '150.00',
            'entertainment_budget': '100.00',
            'other_budget': '100.00'  # Totals to 550, not 500
        })
        assert response.status_code == 200  # Should stay on form with error
        
        # Test negative amounts
        response = logged_in_user.post('/budget/create', data={
            'total_amount': '-100.00',
            'food_budget': '0.00',
            'transportation_budget': '0.00',
            'entertainment_budget': '0.00',
            'other_budget': '0.00'
        })
        assert response.status_code == 200
    
    def test_budget_update(self, logged_in_user, sample_data, app):
        """Test budget update functionality."""
        response = logged_in_user.post('/budget/create', data={
            'total_amount': '600.00',
            'food_budget': '250.00',
            'transportation_budget': '175.00',
            'entertainment_budget': '125.00',
            'other_budget': '50.00'
        })
        
        assert response.status_code == 302
        
        # Verify budget was updated
        with app.app_context():
            db = get_db()
            budget = db.execute('''
                SELECT * FROM budgets 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                ORDER BY created_at DESC LIMIT 1
            ''').fetchone()
            assert float(budget['total_amount']) == 600.00
    
    def test_budget_api_suggestions(self, logged_in_user, sample_data):
        """Test budget suggestions API."""
        response = logged_in_user.get('/budget/api/suggestions')
        assert response.status_code == 200
        
        # Should return JSON
        data = response.get_json()
        assert data is not None
        assert 'total' in data
    
    def test_budget_spending_tracking(self, logged_in_user, sample_data, app):
        """Test budget spending tracking."""
        with app.app_context():
            db = get_db()
            user_id = db.execute('SELECT id FROM users WHERE username = ?', ('testuser',)).fetchone()['id']
            
            # Add some expenses
            db.execute('''
                INSERT INTO transactions (user_id, type, amount, category, description, date)
                VALUES (?, 'expense', 50.00, 'Food', 'Groceries', date('now'))
            ''', (user_id,))
            db.commit()
        
        response = logged_in_user.get('/budget')
        assert response.status_code == 200
        # Should show spending vs budget