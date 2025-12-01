import pytest
from flask import session
from db import get_db

def test_get_priorities_empty(client, auth):
    """Test getting priorities when none exist"""
    auth.login()
    response = client.get('/finance/priorities')
    assert response.status_code == 200
    assert response.json == []

def test_save_priority(client, auth):
    """Test saving a new priority"""
    auth.login()
    response = client.post(
        '/finance/priorities',
        json={
            'priority': 'Save More',
            'importance_level': 4,
            'target_amount': 5000.00,
            'notes': 'Emergency fund goal'
        }
    )
    
    assert response.status_code == 200
    data = response.json
    assert 'priority_id' in data
    assert 'suggestions' in data
    assert len(data['suggestions']) > 0

def test_invalid_priority_type(client, auth):
    """Test saving with invalid priority type"""
    auth.login()
    response = client.post(
        '/finance/priorities',
        json={
            'priority': 'Invalid Type',
            'importance_level': 3
        }
    )
    
    assert response.status_code == 400
    assert 'error' in response.json

def test_update_existing_priority(client, auth):
    """Test updating an existing priority"""
    auth.login()
    
    # Create initial priority
    client.post(
        '/finance/priorities',
        json={'priority': 'Save More', 'importance_level': 3}
    )
    
    # Update it
    response = client.post(
        '/finance/priorities',
        json={'priority': 'Save More', 'importance_level': 5}
    )
    
    assert response.status_code == 200
    assert 'updated' in response.json['message'].lower()

def test_get_suggestions(client, auth):
    """Test getting personalized suggestions"""
    auth.login()
    
    # Set a priority first
    client.post(
        '/finance/priorities',
        json={'priority': 'Control Spending', 'importance_level': 4}
    )
    
    response = client.get('/finance/priorities/suggestions')
    assert response.status_code == 200
    data = response.json
    assert 'Control Spending' in data

def test_delete_priority(client, auth, app):
    """Test deleting a priority"""
    auth.login()
    
    # Create a priority
    response = client.post(
        '/finance/priorities',
        json={'priority': 'Invest More', 'importance_level': 3}
    )
    priority_id = response.json['priority_id']
    
    # Delete it
    response = client.delete(f'/finance/priorities/{priority_id}')
    assert response.status_code == 200
    
    # Verify it's gone
    with app.app_context():
        db = get_db()
        priority = db.execute(
            'SELECT * FROM user_priorities WHERE id = ?',
            (priority_id,)
        ).fetchone()
        assert priority is None

def test_log_priority_action(client, auth):
    """Test logging an action towards a priority"""
    auth.login()
    
    # Create a priority
    response = client.post(
        '/finance/priorities',
        json={'priority': 'Reduce Debt', 'importance_level': 5}
    )
    priority_id = response.json['priority_id']
    
    # Log an action
    response = client.post(
        '/finance/priorities/actions',
        json={
            'priority_id': priority_id,
            'action': 'Made extra payment of $500',
            'notes': 'Applied bonus to debt'
        }
    )
    
    assert response.status_code == 200

def test_unauthorized_access(client):
    """Test that unauthorized users cannot access priorities"""
    response = client.get('/finance/priorities')
    assert response.status_code == 302  # Redirect to login