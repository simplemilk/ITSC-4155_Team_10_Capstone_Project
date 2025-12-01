import pytest
from datetime import datetime, timedelta

def test_view_subscriptions(client, auth):
    """Test viewing subscriptions page"""
    auth.login()
    response = client.get('/subscriptions/')
    assert response.status_code == 200
    assert b'Subscriptions' in response.data

def test_add_subscription(client, auth):
    """Test adding a new subscription"""
    auth.login()
    
    next_billing = (datetime.now() + timedelta(days=30)).date().isoformat()
    
    response = client.post('/subscriptions/add', data={
        'name': 'Netflix',
        'amount': '15.99',
        'frequency': 'monthly',
        'category': 'Streaming',
        'next_billing_date': next_billing,
        'notes': 'Premium plan'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Netflix' in response.data
    assert b'added successfully' in response.data

def test_cancel_subscription(client, auth, app):
    """Test cancelling a subscription"""
    auth.login()
    
    # Add subscription first
    with app.app_context():
        db = get_db()
        db.execute(
            '''INSERT INTO subscriptions 
               (user_id, name, amount, frequency, next_billing_date, start_date)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (1, 'Test Service', 10.99, 'monthly', 
             datetime.now().date().isoformat(), 
             datetime.now().date().isoformat())
        )
        db.commit()
        
        sub_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # Cancel it
    response = client.post(f'/subscriptions/{sub_id}/cancel', follow_redirects=True)
    assert b'cancelled' in response.data

def test_auto_detect_recurring(client, auth, app):
    """Test auto-detection of recurring payments"""
    auth.login()
    
    # Create recurring transactions
    with app.app_context():
        db = get_db()
        base_date = datetime.now()
        
        for i in range(4):  # Create 4 monthly transactions
            transaction_date = (base_date - timedelta(days=30*i)).date().isoformat()
            db.execute(
                '''INSERT INTO transactions 
                   (user_id, type, category, amount, description, date)
                   VALUES (?, 'expense', 'Entertainment', 9.99, 'Spotify Premium', ?)''',
                (1, transaction_date)
            )
        db.commit()
    
    # Run auto-detect
    response = client.post('/subscriptions/detect', follow_redirects=True)
    assert b'Detected' in response.data or b'recurring' in response.data

def test_calculate_monthly_cost(client, auth, app):
    """Test monthly cost calculation"""
    auth.login()
    
    with app.app_context():
        db = get_db()
        # Add various frequency subscriptions
        subscriptions = [
            ('Daily', 1.00, 'daily'),
            ('Weekly', 5.00, 'weekly'),
            ('Monthly', 10.00, 'monthly'),
            ('Yearly', 120.00, 'yearly')
        ]
        
        for name, amount, freq in subscriptions:
            db.execute(
                '''INSERT INTO subscriptions 
                   (user_id, name, amount, frequency, next_billing_date, start_date)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (1, name, amount, freq, 
                 datetime.now().date().isoformat(),
                 datetime.now().date().isoformat())
            )
        db.commit()
    
    response = client.get('/subscriptions/')
    # Total should be: 1*30 + 5*4 + 10 + 120/12 = 30 + 20 + 10 + 10 = 70
    assert b'70.00' in response.data