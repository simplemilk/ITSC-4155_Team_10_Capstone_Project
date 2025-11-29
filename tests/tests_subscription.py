def test_cancel_subscription(client, auth, app):
    """Test cancelling an active subscription"""
    auth.login()
    
    # Add subscription first
    with app.app_context():
        from db import get_db
        db = get_db()
        
        next_billing = (datetime.now() + timedelta(days=30)).date().isoformat()
        
        db.execute(
            '''INSERT INTO subscriptions 
               (user_id, name, amount, frequency, next_billing_date, start_date, is_active)
               VALUES (?, ?, ?, ?, ?, ?, 1)''',
            (1, 'Test Service', 10.99, 'monthly', 
             next_billing, datetime.now().date().isoformat())
        )
        db.commit()
        
        sub_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # Cancel it
    response = client.post(f'/subscriptions/{sub_id}/cancel', follow_redirects=True)
    assert response.status_code == 200
    assert b'cancelled successfully' in response.data
    
    # Verify it's cancelled in database
    with app.app_context():
        db = get_db()
        subscription = db.execute(
            'SELECT is_active, end_date FROM subscriptions WHERE id = ?',
            (sub_id,)
        ).fetchone()
        
        assert subscription['is_active'] == 0
        assert subscription['end_date'] is not None

def test_cancel_nonexistent_subscription(client, auth):
    """Test cancelling a subscription that doesn't exist"""
    auth.login()
    
    response = client.post('/subscriptions/99999/cancel', follow_redirects=True)
    assert response.status_code == 200
    assert b'not found' in response.data

def test_cancel_already_cancelled_subscription(client, auth, app):
    """Test cancelling a subscription that's already cancelled"""
    auth.login()
    
    # Add and cancel subscription
    with app.app_context():
        from db import get_db
        db = get_db()
        
        db.execute(
            '''INSERT INTO subscriptions 
               (user_id, name, amount, frequency, next_billing_date, start_date, is_active, end_date)
               VALUES (?, ?, ?, ?, ?, ?, 0, ?)''',
            (1, 'Cancelled Service', 5.99, 'monthly', 
             datetime.now().date().isoformat(),
             datetime.now().date().isoformat(),
             datetime.now().date().isoformat())
        )
        db.commit()
        sub_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # Try to cancel again
    response = client.post(f'/subscriptions/{sub_id}/cancel', follow_redirects=True)
    assert response.status_code == 200
    assert b'already cancelled' in response.data