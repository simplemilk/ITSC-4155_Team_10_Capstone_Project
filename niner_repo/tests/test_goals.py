"""Tests for financial goals functionality."""

import pytest
from datetime import datetime, date, timedelta
from db import get_db

class TestFinancialGoals:
    """Test cases for financial goals management."""
    
    def test_goals_index(self, logged_in_user):
        """Test financial goals index page."""
        response = logged_in_user.get('/goals')
        assert response.status_code == 200
        assert b'Financial Goals' in response.data
    
    def test_create_goal_get(self, logged_in_user):
        """Test GET request to create goal."""
        response = logged_in_user.get('/goals/create')
        assert response.status_code == 200
        assert b'Create' in response.data and b'Goal' in response.data
    
    def test_create_goal_success(self, logged_in_user, app):
        """Test successful goal creation."""
        target_date = (date.today() + timedelta(days=365)).isoformat()
        
        response = logged_in_user.post('/goals/create', data={
            'goal_name': 'Emergency Fund',
            'description': 'Save for emergencies',
            'category': 'emergency',
            'target_amount': '1000.00',
            'current_amount': '100.00',
            'target_date': target_date,
            'priority': 'high'
        })
        
        assert response.status_code == 302  # Redirect after creation
        
        # Verify goal was created
        with app.app_context():
            db = get_db()
            goal = db.execute('''
                SELECT * FROM financial_goals 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                AND goal_name = 'Emergency Fund'
            ''').fetchone()
            assert goal is not None
            assert float(goal['target_amount']) == 1000.00
            assert goal['category'] == 'emergency'
    
    def test_create_goal_validation(self, logged_in_user):
        """Test goal creation validation."""
        # Test current amount > target amount
        response = logged_in_user.post('/goals/create', data={
            'goal_name': 'Invalid Goal',
            'category': 'other',
            'target_amount': '100.00',
            'current_amount': '200.00',
            'priority': 'medium'
        })
        assert response.status_code == 200  # Should stay on form with error
        
        # Test negative target amount
        response = logged_in_user.post('/goals/create', data={
            'goal_name': 'Invalid Goal',
            'category': 'other',
            'target_amount': '-100.00',
            'current_amount': '0.00',
            'priority': 'medium'
        })
        assert response.status_code == 200
        
        # Test short goal name
        response = logged_in_user.post('/goals/create', data={
            'goal_name': 'Ab',  # Too short
            'category': 'other',
            'target_amount': '100.00',
            'current_amount': '0.00',
            'priority': 'medium'
        })
        assert response.status_code == 200
    
    def test_add_contribution(self, logged_in_user, sample_data, app):
        """Test adding contribution to goal."""
        # Get goal ID
        with app.app_context():
            db = get_db()
            goal = db.execute('''
                SELECT id FROM financial_goals 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                LIMIT 1
            ''').fetchone()
            goal_id = goal['id']
        
        # Add contribution
        response = logged_in_user.post(f'/goals/{goal_id}/contribute', data={
            'contribution': '50.00'
        })
        assert response.status_code == 302
        
        # Verify contribution was added
        with app.app_context():
            db = get_db()
            updated_goal = db.execute('SELECT * FROM financial_goals WHERE id = ?', (goal_id,)).fetchone()
            assert float(updated_goal['current_amount']) == 300.00  # 250 + 50
    
    def test_edit_goal(self, logged_in_user, sample_data, app):
        """Test editing a goal."""
        # Get goal ID
        with app.app_context():
            db = get_db()
            goal = db.execute('''
                SELECT id FROM financial_goals 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                LIMIT 1
            ''').fetchone()
            goal_id = goal['id']
        
        # Test GET request
        response = logged_in_user.get(f'/goals/{goal_id}/edit')
        assert response.status_code == 200
        
        # Test POST request
        response = logged_in_user.post(f'/goals/{goal_id}/edit', data={
            'goal_name': 'Updated Emergency Fund',
            'description': 'Updated description',
            'category': 'emergency',
            'target_amount': '1500.00',
            'current_amount': '250.00',
            'priority': 'high'
        })
        assert response.status_code == 302
        
        # Verify update
        with app.app_context():
            db = get_db()
            updated = db.execute('SELECT * FROM financial_goals WHERE id = ?', (goal_id,)).fetchone()
            assert updated['goal_name'] == 'Updated Emergency Fund'
            assert float(updated['target_amount']) == 1500.00
    
    def test_toggle_goal_completion(self, logged_in_user, sample_data, app):
        """Test toggling goal completion status."""
        # Get goal ID
        with app.app_context():
            db = get_db()
            goal = db.execute('''
                SELECT id FROM financial_goals 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                LIMIT 1
            ''').fetchone()
            goal_id = goal['id']
        
        # Toggle completion
        response = logged_in_user.post(f'/goals/{goal_id}/toggle-completion')
        assert response.status_code == 302
        
        # Verify toggle
        with app.app_context():
            db = get_db()
            updated = db.execute('SELECT * FROM financial_goals WHERE id = ?', (goal_id,)).fetchone()
            assert updated['is_completed'] == 1  # Should be completed now
    
    def test_delete_goal(self, logged_in_user, sample_data, app):
        """Test deleting a goal."""
        # Get goal ID
        with app.app_context():
            db = get_db()
            goal = db.execute('''
                SELECT id FROM financial_goals 
                WHERE user_id = (SELECT id FROM users WHERE username = 'testuser')
                LIMIT 1
            ''').fetchone()
            goal_id = goal['id']
        
        # Delete goal
        response = logged_in_user.post(f'/goals/{goal_id}/delete')
        assert response.status_code == 302
        
        # Verify deletion
        with app.app_context():
            db = get_db()
            deleted = db.execute('SELECT * FROM financial_goals WHERE id = ?', (goal_id,)).fetchone()
            assert deleted is None
    
    def test_goal_progress_calculation(self, logged_in_user, app):
        """Test goal progress calculation."""
        # Create a goal
        response = logged_in_user.post('/goals/create', data={
            'goal_name': 'Test Progress',
            'category': 'other',
            'target_amount': '100.00',
            'current_amount': '25.00',
            'priority': 'medium'
        })
        
        # Check the goals page shows correct progress
        response = logged_in_user.get('/goals')
        assert response.status_code == 200
        assert b'25%' in response.data or b'25.0%' in response.data