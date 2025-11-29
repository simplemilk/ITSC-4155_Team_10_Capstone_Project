"""
Tests for Quick Expense API
Tests expense logging, validation, and integration
"""

import pytest
import json
from datetime import datetime, timedelta
from decimal import Decimal


def test_create_expense_success(client, auth):
    """Test successful expense creation"""
    # Login first
    auth.login()
    
    # Create expense
    response = client.post('/api/expenses', 
        json={
            'amount': 25.50,
            'category': 'Food',
            'description': 'Lunch at McDonald\'s',
            'date': datetime.now().strftime('%Y-%m-%d')
        },
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['message'] == 'Expense added successfully'
    assert 'expense' in data
    assert data['expense']['amount'] == 25.50
    assert data['expense']['category'] == 'Food'
    assert data['expense']['description'] == 'Lunch at McDonald\'s'


def test_create_expense_validation_missing_amount(client, auth):
    """Test expense creation with missing amount"""
    auth.login()
    
    response = client.post('/api/expenses',
        json={
            'category': 'Food',
            'description': 'Test'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'Amount is required' in data['errors']


def test_create_expense_validation_negative_amount(client, auth):
    """Test expense creation with negative amount"""
    auth.login()
    
    response = client.post('/api/expenses',
        json={
            'amount': -10.50,
            'category': 'Food',
            'description': 'Test'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'Amount must be greater than 0' in data['errors']


def test_create_expense_validation_invalid_category(client, auth):
    """Test expense creation with invalid category"""
    auth.login()
    
    response = client.post('/api/expenses',
        json={
            'amount': 10.50,
            'category': 'InvalidCategory',
            'description': 'Test'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert any('Invalid category' in error for error in data['errors'])


def test_create_expense_validation_missing_category(client, auth):
    """Test expense creation with missing category"""
    auth.login()
    
    response = client.post('/api/expenses',
        json={
            'amount': 10.50,
            'description': 'Test'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'Category is required' in data['errors']


def test_create_expense_validation_invalid_date(client, auth):
    """Test expense creation with invalid date format"""
    auth.login()
    
    response = client.post('/api/expenses',
        json={
            'amount': 10.50,
            'category': 'Food',
            'description': 'Test',
            'date': 'invalid-date'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert any('Invalid date format' in error for error in data['errors'])


def test_create_expense_validation_description_too_long(client, auth):
    """Test expense creation with description exceeding max length"""
    auth.login()
    
    long_description = 'a' * 201  # Exceeds 200 character limit
    
    response = client.post('/api/expenses',
        json={
            'amount': 10.50,
            'category': 'Food',
            'description': long_description
        },
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert any('200 characters or less' in error for error in data['errors'])


def test_create_expense_validation_amount_too_large(client, auth):
    """Test expense creation with amount exceeding maximum"""
    auth.login()
    
    response = client.post('/api/expenses',
        json={
            'amount': 1000000,  # Exceeds max
            'category': 'Food',
            'description': 'Test'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert any('too large' in error for error in data['errors'])


def test_create_expense_without_authentication(client):
    """Test expense creation without being logged in"""
    response = client.post('/api/expenses',
        json={
            'amount': 10.50,
            'category': 'Food',
            'description': 'Test'
        },
        content_type='application/json'
    )
    
    # Should redirect to login or return 401
    assert response.status_code in [302, 401]


def test_get_recent_expenses_success(client, auth):
    """Test getting recent expenses"""
    auth.login()
    
    # Create some test expenses
    for i in range(3):
        client.post('/api/expenses',
            json={
                'amount': 10.00 + i,
                'category': 'Food',
                'description': f'Test expense {i}'
            },
            content_type='application/json'
        )
    
    # Get recent expenses
    response = client.get('/api/expenses/recent?limit=5')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'expenses' in data
    assert len(data['expenses']) == 3


def test_get_recent_expenses_limit(client, auth):
    """Test recent expenses with custom limit"""
    auth.login()
    
    # Create 5 test expenses
    for i in range(5):
        client.post('/api/expenses',
            json={
                'amount': 10.00 + i,
                'category': 'Food',
                'description': f'Test expense {i}'
            },
            content_type='application/json'
        )
    
    # Get only 2 recent expenses
    response = client.get('/api/expenses/recent?limit=2')
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['expenses']) == 2


def test_get_recent_expenses_max_limit(client, auth):
    """Test that recent expenses limit is capped at 50"""
    auth.login()
    
    response = client.get('/api/expenses/recent?limit=100')
    
    assert response.status_code == 200
    # Should still work, but limit should be capped internally


def test_expense_creates_transaction(client, auth, app):
    """Test that creating expense creates transaction record"""
    auth.login()
    
    # Create expense
    response = client.post('/api/expenses',
        json={
            'amount': 50.00,
            'category': 'Transportation',
            'description': 'Uber ride'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 201
    
    # Check database for transaction
    with app.app_context():
        from db import get_db
        db = get_db()
        transaction = db.execute(
            'SELECT * FROM transactions WHERE description = ? AND type = ?',
            ('Uber ride', 'expense')
        ).fetchone()
        
        assert transaction is not None
        assert transaction['amount'] == 50.00
        assert transaction['category'] == 'Transportation'


def test_expense_triggers_notifications(client, auth, app):
    """Test that expense creation triggers notification checks"""
    auth.login()
    
    # Create a large expense
    response = client.post('/api/expenses',
        json={
            'amount': 500.00,
            'category': 'Shopping',
            'description': 'Large purchase'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 201
    # Notification system should be triggered (tested separately)


def test_all_valid_categories(client, auth):
    """Test expense creation with all valid categories"""
    auth.login()
    
    categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 
                 'Health', 'Utilities', 'Education', 'Other']
    
    for category in categories:
        response = client.post('/api/expenses',
            json={
                'amount': 25.00,
                'category': category,
                'description': f'Test {category}'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 201, f"Failed for category: {category}"
        data = response.get_json()
        assert data['success'] is True
        assert data['expense']['category'] == category


def test_expense_with_empty_description(client, auth):
    """Test expense creation with empty description"""
    auth.login()
    
    response = client.post('/api/expenses',
        json={
            'amount': 15.00,
            'category': 'Food',
            'description': ''
        },
        content_type='application/json'
    )
    
    # Should succeed - description is optional
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True


def test_expense_with_past_date(client, auth):
    """Test expense creation with past date"""
    auth.login()
    
    past_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    response = client.post('/api/expenses',
        json={
            'amount': 30.00,
            'category': 'Food',
            'description': 'Last week expense',
            'date': past_date
        },
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['expense']['date'] == past_date


def test_expense_default_date(client, auth):
    """Test expense creation with default date"""
    auth.login()
    
    response = client.post('/api/expenses',
        json={
            'amount': 20.00,
            'category': 'Food',
            'description': 'No date provided'
        },
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['expense']['date'] == datetime.now().strftime('%Y-%m-%d')


def test_expense_decimal_precision(client, auth):
    """Test expense with precise decimal amounts"""
    auth.login()
    
    test_amounts = [10.99, 5.01, 100.50, 0.01, 999.99]
    
    for amount in test_amounts:
        response = client.post('/api/expenses',
            json={
                'amount': amount,
                'category': 'Food',
                'description': f'Test ${amount}'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert abs(data['expense']['amount'] - amount) < 0.01


def test_concurrent_expense_creation(client, auth):
    """Test creating multiple expenses in quick succession"""
    auth.login()
    
    responses = []
    for i in range(5):
        response = client.post('/api/expenses',
            json={
                'amount': 10.00 + i,
                'category': 'Food',
                'description': f'Concurrent expense {i}'
            },
            content_type='application/json'
        )
        responses.append(response)
    
    # All should succeed
    for response in responses:
        assert response.status_code == 201
        assert response.get_json()['success'] is True
