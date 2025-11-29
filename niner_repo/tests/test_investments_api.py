"""Unit tests for investments and portfolio endpoints."""

import os
import sqlite3
import pytest
from db import get_db


def _apply_investments_schema(app):
    """Helper to apply investments schema to the test DB."""
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'investments_schema.sql')
    schema_path = os.path.abspath(schema_path)
    with open(schema_path, 'r') as f:
        schema = f.read()
    db = get_db()
    db.executescript(schema)
    # insert a default asset type
    db.execute("INSERT OR IGNORE INTO asset_types (id, name) VALUES (1, 'Equity')")
    db.commit()


def test_create_investment_and_position(client, auth, app):
    # register and login
    auth.register(username='invtester')
    auth.login(username='invtester')

    # prepare DB schema for investments
    with app.app_context():
        _apply_investments_schema(app)

    # create a new investment via the form
    resp = client.post('/investments/create', data={
        'ticker': 'TEST',
        'name': 'Test Corp',
        'asset_type_id': '1',
        'exchange': 'NYSE'
    }, follow_redirects=False)

    # should redirect to investments index
    assert resp.status_code in (302, 303)

    # verify position was created in DB
    with app.app_context():
        db = get_db()
        row = db.execute('SELECT p.id, i.ticker FROM positions p JOIN investments i ON p.investment_id=i.id').fetchone()
        assert row is not None
        assert row['ticker'] == 'TEST'


def test_portfolio_shows_position(logged_in_user, app):
    # ensure investments schema and a sample position exist
    with app.app_context():
        _apply_investments_schema(app)
        db = get_db()
        # create an investment
        cur = db.execute("INSERT INTO investments (ticker, name, asset_type_id, exchange) VALUES (?,?,?,?)", ('PFTEST', 'PF Test Co', 1, 'NYSE'))
        inv_id = cur.lastrowid
        # create a position for the logged in user
        user = db.execute("SELECT id FROM user WHERE username = ?", ('testuser',)).fetchone()
        uid = user['id']
        db.execute('INSERT INTO positions (user_id, investment_id, quantity, avg_cost) VALUES (?,?,?,?)', (uid, inv_id, 10, 5.0))
        db.commit()

    # request portfolio page
    resp = logged_in_user.get('/portfolio/')
    assert resp.status_code == 200
    assert b'PFTEST' in resp.data
