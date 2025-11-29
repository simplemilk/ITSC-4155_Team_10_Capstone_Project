"""Tests for income functionality."""

import pytest
from datetime import datetime, date
from db import get_db

class TestIncome:
    """Test cases for income management."""
    
    def test_income_index(self, logged_in_user):
        """Test income index page."""
        response = logged_in_user.get('/income')
        assert response.status_code == 200
        assert b'Income' in response.data
    
    def test_add_income_get(self, logged_in_user):
        """Test GET request to add income."""
        response = logged_in_user.get('/income/add')
        assert response.status_code == 200
        assert b'Add Income' in response.data
    
    def test_add_income_success(self, logged_in_user, app):
        """Test successful income addition."""
        response = logged_in_user.post('/income/add', data={
            'source': 'Part-time Job',
            'amount': '800.00',
            'frequency': 'monthly',
            'start_date': date.today().isoformat()
        })
        
        assert response.status_code == 302  # Redirect after creation
        
        # Verify income was created
        with app.app_context():
            db = get_db()
            income = db.execute('''
                SELECT * FROM income 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                AND source = 'Part-time Job'
            ''').fetchone()
            assert income is not None
            assert float(income['amount']) == 800.00
            assert income['frequency'] == 'monthly'
    
    def test_income_validation(self, logged_in_user):
        """Test income form validation."""
        # Test negative amount
        response = logged_in_user.post('/income/add', data={
            'source': 'Invalid Income',
            'amount': '-100.00',
            'frequency': 'monthly',
            'start_date': date.today().isoformat()
        })
        assert response.status_code == 200  # Should stay on form
        
        # Test zero amount
        response = logged_in_user.post('/income/add', data={
            'source': 'Invalid Income',
            'amount': '0.00',
            'frequency': 'monthly',
            'start_date': date.today().isoformat()
        })
        assert response.status_code == 200
    
    def test_edit_income(self, logged_in_user, sample_data, app):
        """Test editing income."""
        # Get income ID
        with app.app_context():
            db = get_db()
            income = db.execute('''
                SELECT id FROM income 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                LIMIT 1
            ''').fetchone()
            income_id = income['id']
        
        # Test GET request
        response = logged_in_user.get(f'/income/{income_id}/edit')
        assert response.status_code == 200
        
        # Test POST request
        response = logged_in_user.post(f'/income/{income_id}/edit', data={
            'source': 'Updated Job',
            'amount': '900.00',
            'frequency': 'monthly',
            'start_date': date.today().isoformat()
        })
        assert response.status_code == 302
        
        # Verify update
        with app.app_context():
            db = get_db()
            updated = db.execute('SELECT * FROM income WHERE id = ?', (income_id,)).fetchone()
            assert updated['source'] == 'Updated Job'
            assert float(updated['amount']) == 900.00
    
    def test_delete_income(self, logged_in_user, sample_data, app):
        """Test deleting income."""
        # Get income ID
        with app.app_context():
            db = get_db()
            income = db.execute('''
                SELECT id FROM income 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                LIMIT 1
            ''').fetchone()
            income_id = income['id']
        
        # Delete income
        response = logged_in_user.post(f'/income/{income_id}/delete')
        assert response.status_code == 302
        
        # Verify deletion
        with app.app_context():
            db = get_db()
            deleted = db.execute('SELECT * FROM income WHERE id = ?', (income_id,)).fetchone()
            assert deleted is None
    
    def test_toggle_income_status(self, logged_in_user, sample_data, app):
        """Test toggling income active status."""
        # Get income ID
        with app.app_context():
            db = get_db()
            income = db.execute('''
                SELECT id FROM income 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                LIMIT 1
            ''').fetchone()
            income_id = income['id']
        
        # Toggle status
        response = logged_in_user.post(f'/income/{income_id}/toggle')
        assert response.status_code == 302
        
        # Verify toggle
        with app.app_context():
            db = get_db()
            updated = db.execute('SELECT * FROM income WHERE id = ?', (income_id,)).fetchone()
            assert updated['is_active'] == 0  # Should be inactive now