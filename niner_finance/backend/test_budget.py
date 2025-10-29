import json
from app import app, db
from models import WeeklyBudget

def setup_module(module):
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()

def test_set_budget():
    client = app.test_client()
    payload = {
        'user_id': 1,
        'amount': 100.0,
        'week_start_date': '2025-10-27'
    }
    response = client.post('/api/budget', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Budget set successfully'
    assert data['budget']['amount'] == 100.0
