"""Integration tests for the Niner Finance application."""

import pytest
from datetime import datetime, date, timedelta
from db import get_db

class TestIntegration:
    """Test cases for integration between modules."""
    
    def test_complete_user_workflow(self, client, auth, app):
        """Test complete user workflow from registration to goal achievement."""
        # Register user
        auth.register()
        
        # Login
        auth.login()
        
        # Create budget
        response = client.post('/budget/create', data={
            'total_amount': '500.00',
            'food_budget': '200.00',
            'transportation_budget': '150.00',
            'entertainment_budget': '100.00',
            'other_budget': '50.00'
        })
        assert response.status_code == 302
        
        # Add income
        response = client.post('/income/add', data={
            'source': 'Part-time Job',
            'amount': '800.00',
            'frequency': 'monthly',
            'start_date': date.today().isoformat()
        })
        assert response.status_code == 302
        
        # Create financial goal
        target_date = (date.today() + timedelta(days=365)).isoformat()
        response = client.post('/goals/create', data={
            'goal_name': 'Emergency Fund',
            'description': 'Save for emergencies',
            'category': 'emergency',
            'target_amount': '1000.00',
            'current_amount': '0.00',
            'target_date': target_date,
            'priority': 'high'
        })
        assert response.status_code == 302
        
        # Add some transactions
        transactions = [
            {'type': 'expense', 'amount': '25.50', 'category': 'Food', 'description': 'Lunch'},
            {'type': 'expense', 'amount': '45.00', 'category': 'Transportation', 'description': 'Gas'},
            {'type': 'income', 'amount': '200.00', 'category': 'Income', 'description': 'Work'},
        ]
        
        for transaction in transactions:
            response = client.post('/transactions/add', data={
                **transaction,
                'date': date.today().isoformat()
            })
            assert response.status_code == 302
        
        # Add contribution to goal
        with app.app_context():
            db = get_db()
            goal = db.execute('''
                SELECT id FROM financial_goals 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                LIMIT 1
            ''').fetchone()
            goal_id = goal['id']
        
        response = client.post(f'/goals/{goal_id}/contribute', data={
            'contribution': '100.00'
        })
        assert response.status_code == 302
        
        # Check dashboard shows all data
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Emergency Fund' in response.data
        assert b'$100' in response.data  # Goal contribution
    
    def test_budget_transaction_integration(self, logged_in_user, app):
        """Test integration between budget and transactions."""
        # Create budget
        logged_in_user.post('/budget/create', data={
            'total_amount': '500.00',
            'food_budget': '200.00',
            'transportation_budget': '150.00',
            'entertainment_budget': '100.00',
            'other_budget': '50.00'
        })
        
        # Add transactions that affect budget
        logged_in_user.post('/transactions/add', data={
            'type': 'expense',
            'amount': '50.00',
            'category': 'Food',
            'description': 'Groceries',
            'date': date.today().isoformat()
        })
        
        # Check budget page shows spending
        response = logged_in_user.get('/budget')
        assert response.status_code == 200
        assert b'50' in response.data  # Should show the spending
    
    def test_goal_transaction_integration(self, logged_in_user, app):
        """Test integration between goals and transactions."""
        # Create goal
        target_date = (date.today() + timedelta(days=365)).isoformat()
        logged_in_user.post('/goals/create', data={
            'goal_name': 'Laptop Fund',
            'category': 'technology',
            'target_amount': '1000.00',
            'current_amount': '0.00',
            'target_date': target_date,
            'priority': 'medium'
        })
        
        # Get goal ID
        with app.app_context():
            db = get_db()
            goal = db.execute('''
                SELECT id FROM financial_goals 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                AND goal_name = 'Laptop Fund'
            ''').fetchone()
            goal_id = goal['id']
        
        # Add contribution (which should create transaction)
        logged_in_user.post(f'/goals/{goal_id}/contribute', data={
            'contribution': '200.00'
        })
        
        # Verify transaction was created
        with app.app_context():
            db = get_db()
            transaction = db.execute('''
                SELECT * FROM transactions 
                WHERE goal_id = ? AND type = 'income'
            ''', (goal_id,)).fetchone()
            assert transaction is not None
            assert float(transaction['amount']) == 200.00
    
    def test_error_handling(self, logged_in_user):
        """Test error handling across the application."""
        # Test accessing non-existent goal
        response = logged_in_user.get('/goals/999/edit')
        assert response.status_code == 404 or response.status_code == 302
        
        # Test accessing non-existent transaction
        response = logged_in_user.get('/transactions/999/edit')
        assert response.status_code == 404 or response.status_code == 302
        
        # Test accessing non-existent income
        response = logged_in_user.get('/income/999/edit')
        assert response.status_code == 404 or response.status_code == 302