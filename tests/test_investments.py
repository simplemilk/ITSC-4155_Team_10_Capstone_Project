import pytest
from datetime import datetime, timedelta
from db import get_db

def test_view_investments_page(client, auth):
    """Test accessing the investments page"""
    auth.login()
    response = client.get('/investments/')
    assert response.status_code == 200
    assert b'Investment Portfolio' in response.data
    assert b'Add Investment' in response.data

def test_view_investments_requires_login(client):
    """Test that investments page requires authentication"""
    response = client.get('/investments/')
    assert response.status_code == 302  # Redirect to login
    assert b'login' in response.location.lower().encode()

# ============================================================================
# SUCCESS SCENARIOS - Create Portfolio Entry
# ============================================================================

def test_add_investment_success(client, auth, app):
    """
    SUCCESS SCENARIO: Create Portfolio Entry
    
    Given the user is logged into their account,
    When they add a new investment with valid details,
    Then the system should save the entry and display it in the portfolio list.
    """
    auth.login()
    
    # Add investment with valid data
    response = client.post('/investments/add', data={
        'asset_name': 'Apple Inc.',
        'ticker_symbol': 'AAPL',
        'asset_type': 'Stock',
        'quantity': '10',
        'purchase_price': '150.50',
        'purchase_date': '2024-01-15',
        'notes': 'Tech investment'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Investment added successfully' in response.data or b'Apple Inc.' in response.data
    
    # Verify investment is in database
    with app.app_context():
        db = get_db()
        investment = db.execute(
            'SELECT * FROM investments WHERE asset_name = ? AND user_id = ?',
            ('Apple Inc.', 1)
        ).fetchone()
        
        assert investment is not None
        assert investment['ticker_symbol'] == 'AAPL'
        assert investment['asset_type'] == 'Stock'
        assert float(investment['quantity']) == 10.0
        assert float(investment['purchase_price']) == 150.50
        assert investment['purchase_date'] == '2024-01-15'
        assert investment['notes'] == 'Tech investment'

def test_add_multiple_investments(client, auth, app):
    """Test adding multiple investments to portfolio"""
    auth.login()
    
    investments = [
        {
            'asset_name': 'Tesla Inc.',
            'ticker_symbol': 'TSLA',
            'asset_type': 'Stock',
            'quantity': '5',
            'purchase_price': '200.00',
            'purchase_date': '2024-01-10'
        },
        {
            'asset_name': 'Bitcoin',
            'ticker_symbol': 'BTC',
            'asset_type': 'Cryptocurrency',
            'quantity': '0.5',
            'purchase_price': '45000.00',
            'purchase_date': '2024-01-20'
        },
        {
            'asset_name': 'Gold ETF',
            'ticker_symbol': 'GLD',
            'asset_type': 'ETF',
            'quantity': '20',
            'purchase_price': '180.00',
            'purchase_date': '2024-02-01'
        }
    ]
    
    for inv in investments:
        response = client.post('/investments/add', data=inv, follow_redirects=True)
        assert response.status_code == 200
    
    # Verify all investments are saved
    with app.app_context():
        db = get_db()
        all_investments = db.execute(
            'SELECT * FROM investments WHERE user_id = ?', (1,)
        ).fetchall()
        
        assert len(all_investments) == 3
        assert {inv['asset_name'] for inv in all_investments} == {'Tesla Inc.', 'Bitcoin', 'Gold ETF'}

def test_add_investment_with_optional_fields(client, auth, app):
    """Test adding investment with only required fields"""
    auth.login()
    
    response = client.post('/investments/add', data={
        'asset_name': 'Microsoft',
        'ticker_symbol': 'MSFT',
        'asset_type': 'Stock',
        'quantity': '15',
        'purchase_price': '350.00',
        'purchase_date': '2024-03-01',
        'notes': ''  # Optional field left empty
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    with app.app_context():
        db = get_db()
        investment = db.execute(
            'SELECT * FROM investments WHERE ticker_symbol = ?', ('MSFT',)
        ).fetchone()
        
        assert investment is not None
        assert investment['notes'] == '' or investment['notes'] is None

# ============================================================================
# FAILURE SCENARIOS - Invalid Data Entry
# ============================================================================

def test_add_investment_missing_asset_name(client, auth):
    """
    FAILURE SCENARIO: Invalid Data Entry - Missing Asset Name
    
    Given the user is adding a new investment,
    When they leave the asset name field blank,
    Then the system should reject the input and show a validation error.
    """
    auth.login()
    
    response = client.post('/investments/add', data={
        'asset_name': '',  # Missing required field
        'ticker_symbol': 'AAPL',
        'asset_type': 'Stock',
        'quantity': '10',
        'purchase_price': '150.00',
        'purchase_date': '2024-01-15'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Asset name is required' in response.data or b'required' in response.data.lower()

def test_add_investment_invalid_quantity(client, auth):
    """
    FAILURE SCENARIO: Invalid Data Entry - Text Instead of Number
    
    Given the user is adding a new investment,
    When they enter text instead of a number for quantity,
    Then the system should reject the input and show a validation error.
    """
    auth.login()
    
    response = client.post('/investments/add', data={
        'asset_name': 'Apple Inc.',
        'ticker_symbol': 'AAPL',
        'asset_type': 'Stock',
        'quantity': 'ten',  # Invalid: text instead of number
        'purchase_price': '150.00',
        'purchase_date': '2024-01-15'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'valid' in response.data.lower() or b'number' in response.data.lower()

def test_add_investment_negative_quantity(client, auth):
    """
    FAILURE SCENARIO: Invalid Data Entry - Negative Quantity
    
    Given the user is adding a new investment,
    When they enter a negative number for quantity,
    Then the system should reject the input.
    """
    auth.login()
    
    response = client.post('/investments/add', data={
        'asset_name': 'Apple Inc.',
        'ticker_symbol': 'AAPL',
        'asset_type': 'Stock',
        'quantity': '-10',  # Invalid: negative quantity
        'purchase_price': '150.00',
        'purchase_date': '2024-01-15'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'must be greater than 0' in response.data or b'positive' in response.data.lower()

def test_add_investment_invalid_price(client, auth):
    """
    FAILURE SCENARIO: Invalid Data Entry - Invalid Price
    
    Given the user is adding a new investment,
    When they enter invalid price data,
    Then the system should reject the input.
    """
    auth.login()
    
    response = client.post('/investments/add', data={
        'asset_name': 'Apple Inc.',
        'ticker_symbol': 'AAPL',
        'asset_type': 'Stock',
        'quantity': '10',
        'purchase_price': 'expensive',  # Invalid: text instead of number
        'purchase_date': '2024-01-15'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'valid' in response.data.lower() or b'price' in response.data.lower()

def test_add_investment_zero_price(client, auth):
    """
    FAILURE SCENARIO: Invalid Data Entry - Zero Price
    """
    auth.login()
    
    response = client.post('/investments/add', data={
        'asset_name': 'Apple Inc.',
        'ticker_symbol': 'AAPL',
        'asset_type': 'Stock',
        'quantity': '10',
        'purchase_price': '0',  # Invalid: zero price
        'purchase_date': '2024-01-15'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'must be greater than 0' in response.data or b'valid price' in response.data.lower()

def test_add_investment_invalid_date_format(client, auth):
    """
    FAILURE SCENARIO: Invalid Data Entry - Invalid Date Format
    """
    auth.login()
    
    response = client.post('/investments/add', data={
        'asset_name': 'Apple Inc.',
        'ticker_symbol': 'AAPL',
        'asset_type': 'Stock',
        'quantity': '10',
        'purchase_price': '150.00',
        'purchase_date': 'January 15, 2024'  # Invalid format
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Should either show error or handle gracefully

def test_add_investment_future_date(client, auth):
    """
    FAILURE SCENARIO: Invalid Data Entry - Future Date
    """
    auth.login()
    
    future_date = (datetime.now() + timedelta(days=30)).date().isoformat()
    
    response = client.post('/investments/add', data={
        'asset_name': 'Apple Inc.',
        'ticker_symbol': 'AAPL',
        'asset_type': 'Stock',
        'quantity': '10',
        'purchase_price': '150.00',
        'purchase_date': future_date  # Future date
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'cannot be in the future' in response.data or b'invalid date' in response.data.lower()

def test_add_investment_missing_all_fields(client, auth):
    """
    FAILURE SCENARIO: Invalid Data Entry - All Fields Blank
    """
    auth.login()
    
    response = client.post('/investments/add', data={}, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'required' in response.data.lower()

# ============================================================================
# EDIT INVESTMENT TESTS
# ============================================================================

def test_edit_investment_success(client, auth, app):
    """Test successfully editing an existing investment"""
    auth.login()
    
    # Add investment first
    with app.app_context():
        db = get_db()
        db.execute(
            '''INSERT INTO investments 
               (user_id, asset_name, ticker_symbol, asset_type, quantity, 
                purchase_price, purchase_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (1, 'Apple Inc.', 'AAPL', 'Stock', 10, 150.00, '2024-01-15')
        )
        db.commit()
        inv_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # Edit the investment
    response = client.post(f'/investments/{inv_id}/edit', data={
        'asset_name': 'Apple Inc.',
        'ticker_symbol': 'AAPL',
        'asset_type': 'Stock',
        'quantity': '15',  # Changed from 10 to 15
        'purchase_price': '160.00',  # Changed price
        'purchase_date': '2024-01-15',
        'notes': 'Updated investment'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'updated successfully' in response.data or b'Updated' in response.data
    
    # Verify changes in database
    with app.app_context():
        db = get_db()
        investment = db.execute(
            'SELECT * FROM investments WHERE id = ?', (inv_id,)
        ).fetchone()
        
        assert float(investment['quantity']) == 15.0
        assert float(investment['purchase_price']) == 160.00
        assert investment['notes'] == 'Updated investment'

def test_edit_nonexistent_investment(client, auth):
    """Test editing an investment that doesn't exist"""
    auth.login()
    
    response = client.post('/investments/99999/edit', data={
        'asset_name': 'Apple Inc.',
        'ticker_symbol': 'AAPL',
        'asset_type': 'Stock',
        'quantity': '10',
        'purchase_price': '150.00',
        'purchase_date': '2024-01-15'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'not found' in response.data.lower()

def test_edit_investment_invalid_data(client, auth, app):
    """Test editing investment with invalid data"""
    auth.login()
    
    # Add investment first
    with app.app_context():
        db = get_db()
        db.execute(
            '''INSERT INTO investments 
               (user_id, asset_name, ticker_symbol, asset_type, quantity, 
                purchase_price, purchase_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (1, 'Apple Inc.', 'AAPL', 'Stock', 10, 150.00, '2024-01-15')
        )
        db.commit()
        inv_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # Try to edit with invalid data
    response = client.post(f'/investments/{inv_id}/edit', data={
        'asset_name': 'Apple Inc.',
        'ticker_symbol': 'AAPL',
        'asset_type': 'Stock',
        'quantity': 'invalid',  # Invalid quantity
        'purchase_price': '150.00',
        'purchase_date': '2024-01-15'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'valid' in response.data.lower() or b'error' in response.data.lower()

# ============================================================================
# DELETE INVESTMENT TESTS
# ============================================================================

def test_delete_investment_success(client, auth, app):
    """Test successfully deleting an investment"""
    auth.login()
    
    # Add investment first
    with app.app_context():
        db = get_db()
        db.execute(
            '''INSERT INTO investments 
               (user_id, asset_name, ticker_symbol, asset_type, quantity, 
                purchase_price, purchase_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (1, 'Apple Inc.', 'AAPL', 'Stock', 10, 150.00, '2024-01-15')
        )
        db.commit()
        inv_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # Delete the investment
    response = client.post(f'/investments/{inv_id}/delete', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'deleted' in response.data.lower() or b'removed' in response.data.lower()
    
    # Verify deletion in database
    with app.app_context():
        db = get_db()
        investment = db.execute(
            'SELECT * FROM investments WHERE id = ?', (inv_id,)
        ).fetchone()
        
        assert investment is None

def test_delete_nonexistent_investment(client, auth):
    """Test deleting an investment that doesn't exist"""
    auth.login()
    
    response = client.post('/investments/99999/delete', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'not found' in response.data.lower()

def test_delete_other_user_investment(client, auth, app):
    """Test that user cannot delete another user's investment"""
    auth.login()
    
    # Create investment for different user
    with app.app_context():
        db = get_db()
        db.execute(
            '''INSERT INTO investments 
               (user_id, asset_name, ticker_symbol, asset_type, quantity, 
                purchase_price, purchase_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (999, 'Apple Inc.', 'AAPL', 'Stock', 10, 150.00, '2024-01-15')
        )
        db.commit()
        inv_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # Try to delete as different user
    response = client.post(f'/investments/{inv_id}/delete', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'not found' in response.data.lower() or b'permission' in response.data.lower()

# ============================================================================
# PORTFOLIO SUMMARY TESTS
# ============================================================================

def test_portfolio_summary_calculation(client, auth, app):
    """Test that portfolio summary calculates correctly"""
    auth.login()
    
    # Add multiple investments
    with app.app_context():
        db = get_db()
        investments = [
            (1, 'Apple', 'AAPL', 'Stock', 10, 150.00, '2024-01-15'),
            (1, 'Tesla', 'TSLA', 'Stock', 5, 200.00, '2024-01-20'),
            (1, 'Bitcoin', 'BTC', 'Cryptocurrency', 0.5, 45000.00, '2024-02-01')
        ]
        
        for inv in investments:
            db.execute(
                '''INSERT INTO investments 
                   (user_id, asset_name, ticker_symbol, asset_type, quantity, 
                    purchase_price, purchase_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                inv
            )
        db.commit()
    
    response = client.get('/investments/')
    
    assert response.status_code == 200
    # Total value should be: (10*150) + (5*200) + (0.5*45000) = 1500 + 1000 + 22500 = 25000
    assert b'25000' in response.data or b'25,000' in response.data

def test_empty_portfolio_display(client, auth):
    """Test that empty portfolio displays correctly"""
    auth.login()
    
    response = client.get('/investments/')
    
    assert response.status_code == 200
    assert b'No investments' in response.data or b'empty' in response.data.lower()

def test_portfolio_asset_type_breakdown(client, auth, app):
    """Test portfolio shows breakdown by asset type"""
    auth.login()
    
    # Add investments of different types
    with app.app_context():
        db = get_db()
        investments = [
            (1, 'Apple', 'AAPL', 'Stock', 10, 150.00, '2024-01-15'),
            (1, 'Bitcoin', 'BTC', 'Cryptocurrency', 1, 45000.00, '2024-01-20'),
            (1, 'Gold ETF', 'GLD', 'ETF', 20, 180.00, '2024-02-01')
        ]
        
        for inv in investments:
            db.execute(
                '''INSERT INTO investments 
                   (user_id, asset_name, ticker_symbol, asset_type, quantity, 
                    purchase_price, purchase_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                inv
            )
        db.commit()
    
    response = client.get('/investments/')
    
    assert response.status_code == 200
    assert b'Stock' in response.data
    assert b'Cryptocurrency' in response.data
    assert b'ETF' in response.data

# ============================================================================
# PERFORMANCE TRACKING TESTS
# ============================================================================

def test_investment_current_price_update(client, auth, app):
    """Test updating current price of investment"""
    auth.login()
    
    # Add investment
    with app.app_context():
        db = get_db()
        db.execute(
            '''INSERT INTO investments 
               (user_id, asset_name, ticker_symbol, asset_type, quantity, 
                purchase_price, purchase_date, current_price)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (1, 'Apple', 'AAPL', 'Stock', 10, 150.00, '2024-01-15', 150.00)
        )
        db.commit()
        inv_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # Update current price
    response = client.post(f'/investments/{inv_id}/update-price', data={
        'current_price': '175.00'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify price update
    with app.app_context():
        db = get_db()
        investment = db.execute(
            'SELECT current_price FROM investments WHERE id = ?', (inv_id,)
        ).fetchone()
        
        assert float(investment['current_price']) == 175.00

def test_investment_gain_loss_calculation(client, auth, app):
    """Test that gain/loss is calculated correctly"""
    auth.login()
    
    # Add investment with gain
    with app.app_context():
        db = get_db()
        db.execute(
            '''INSERT INTO investments 
               (user_id, asset_name, ticker_symbol, asset_type, quantity, 
                purchase_price, purchase_date, current_price)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (1, 'Apple', 'AAPL', 'Stock', 10, 150.00, '2024-01-15', 175.00)
        )
        db.commit()
    
    response = client.get('/investments/')
    
    assert response.status_code == 200
    # Gain should be: (175 - 150) * 10 = 250
    assert b'250' in response.data or b'+' in response.data

# ============================================================================
# SECURITY TESTS
# ============================================================================

def test_view_investments_other_user(client, auth, app):
    """Test that users cannot view other users' investments"""
    # Create investment for different user
    with app.app_context():
        db = get_db()
        db.execute(
            '''INSERT INTO investments 
               (user_id, asset_name, ticker_symbol, asset_type, quantity, 
                purchase_price, purchase_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (999, 'Secret Investment', 'SECRET', 'Stock', 100, 1000.00, '2024-01-15')
        )
        db.commit()
    
    # Login as different user
    auth.login()
    
    response = client.get('/investments/')
    
    assert response.status_code == 200
    assert b'Secret Investment' not in response.data

def test_investment_ownership_validation(client, auth, app):
    """Test that investment operations validate ownership"""
    auth.login()
    
    # Create investment for different user
    with app.app_context():
        db = get_db()
        db.execute(
            '''INSERT INTO investments 
               (user_id, asset_name, ticker_symbol, asset_type, quantity, 
                purchase_price, purchase_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (999, 'Apple Inc.', 'AAPL', 'Stock', 10, 150.00, '2024-01-15')
        )
        db.commit()
        inv_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # Try to edit as wrong user
    response = client.post(f'/investments/{inv_id}/edit', data={
        'asset_name': 'Hacked',
        'ticker_symbol': 'HACK',
        'asset_type': 'Stock',
        'quantity': '1000',
        'purchase_price': '1.00',
        'purchase_date': '2024-01-15'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify investment was NOT changed
    with app.app_context():
        db = get_db()
        investment = db.execute(
            'SELECT asset_name FROM investments WHERE id = ?', (inv_id,)
        ).fetchone()
        
        assert investment['asset_name'] == 'Apple Inc.'  # Not 'Hacked'

# ============================================================================
# EDGE CASES
# ============================================================================

def test_add_investment_very_large_quantity(client, auth, app):
    """Test adding investment with very large quantity"""
    auth.login()
    
    response = client.post('/investments/add', data={
        'asset_name': 'Penny Stock',
        'ticker_symbol': 'PENNY',
        'asset_type': 'Stock',
        'quantity': '1000000',  # Very large quantity
        'purchase_price': '0.01',
        'purchase_date': '2024-01-15'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    with app.app_context():
        db = get_db()
        investment = db.execute(
            'SELECT * FROM investments WHERE ticker_symbol = ?', ('PENNY',)
        ).fetchone()
        
        assert investment is not None
        assert float(investment['quantity']) == 1000000.0

def test_add_investment_fractional_quantity(client, auth, app):
    """Test adding investment with fractional quantity (e.g., crypto)"""
    auth.login()
    
    response = client.post('/investments/add', data={
        'asset_name': 'Bitcoin',
        'ticker_symbol': 'BTC',
        'asset_type': 'Cryptocurrency',
        'quantity': '0.00123456',  # Fractional quantity
        'purchase_price': '45000.00',
        'purchase_date': '2024-01-15'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    with app.app_context():
        db = get_db()
        investment = db.execute(
            'SELECT * FROM investments WHERE ticker_symbol = ?', ('BTC',)
        ).fetchone()
        
        assert investment is not None
        assert float(investment['quantity']) == pytest.approx(0.00123456, rel=1e-6)

def test_add_investment_special_characters_in_name(client, auth, app):
    """Test adding investment with special characters in name"""
    auth.login()
    
    response = client.post('/investments/add', data={
        'asset_name': "Johnson & Johnson (J&J)",
        'ticker_symbol': 'JNJ',
        'asset_type': 'Stock',
        'quantity': '10',
        'purchase_price': '150.00',
        'purchase_date': '2024-01-15'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    with app.app_context():
        db = get_db()
        investment = db.execute(
            'SELECT * FROM investments WHERE ticker_symbol = ?', ('JNJ',)
        ).fetchone()
        
        assert investment is not None
        assert "Johnson & Johnson" in investment['asset_name']