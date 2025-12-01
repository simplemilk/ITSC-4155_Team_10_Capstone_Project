from flask import Blueprint, render_template
from auth import login_required
from db import get_db
from flask import g
from datetime import datetime, timedelta, date

bp = Blueprint('portfolio', __name__, url_prefix='/portfolio')


def _get_last_price_for_investment(db, investment_id):
    r = db.execute('SELECT price, date FROM investment_transactions WHERE investment_id = ? ORDER BY date DESC LIMIT 1', (investment_id,)).fetchone()
    if r:
        return float(r['price'])
    return None


@bp.route('/')
@login_required
def index():
    db = get_db()
    user_id = g.user['id']

    # Get positions and instrument metadata
    rows = db.execute('''
        SELECT p.id as position_id, p.quantity, p.avg_cost, i.id as investment_id, i.ticker, i.name, i.asset_type_id, at.name as asset_type
        FROM positions p
        JOIN investments i ON p.investment_id = i.id
        LEFT JOIN asset_types at ON i.asset_type_id = at.id
        WHERE p.user_id = ?
    ''', (user_id,)).fetchall()

    holdings = []
    total_value = 0.0
    # build holdings with a best-effort current price (last transaction price or avg_cost)
    for r in rows:
        qty = float(r['quantity'])
        last_price = _get_last_price_for_investment(db, r['investment_id'])
        price = last_price if last_price is not None else float(r['avg_cost'] or 0)
        value = qty * price
        # compute profit/loss relative to avg_cost
        avg_cost = float(r['avg_cost'] or 0)
        pl_amount = (price - avg_cost) * qty
        pl_percent = ( (price - avg_cost) / avg_cost * 100 ) if avg_cost not in (0, None) else 0

        holdings.append({
            'position_id': r['position_id'],
            'investment_id': r['investment_id'],
            'ticker': r['ticker'],
            'name': r['name'],
            'qty': qty,
            'avg_cost': float(r['avg_cost'] or 0),
            'price': price,
            'value': value,
            'asset_type': r['asset_type'] or 'Other',
            'pl_amount': round(pl_amount, 2),
            'pl_percent': round(pl_percent, 2)
        })
        total_value += value

    # allocations by asset_type
    alloc_map = {}
    for h in holdings:
        alloc_map.setdefault(h['asset_type'], 0.0)
        alloc_map[h['asset_type']] += h['value']

    allocations = [{'name': k, 'value': v, 'color': '#4f46e5'} for k, v in alloc_map.items()]

    # add allocation percentage to each holding (used by templates)
    if total_value > 0:
        for h in holdings:
            h['allocation'] = round((h['value'] / total_value) * 100, 1)
    else:
        for h in holdings:
            h['allocation'] = 0.0

    # Build historical performance (last 30 days) by aggregating transactions
    # Fetch user's investment transactions
    tx_rows = db.execute('SELECT investment_id, date, type, quantity, price FROM investment_transactions WHERE user_id = ? ORDER BY date', (user_id,)).fetchall()
    txs = [dict(x) for x in tx_rows]

    today = date.today()
    days = 30
    series = []

    # Precompute transactions grouped by investment
    inv_txs = {}
    for t in txs:
        inv_txs.setdefault(t['investment_id'], []).append(t)

    for i in range(days-1, -1, -1):
        d = today - timedelta(days=i)
        day_val = 0.0
        # for each investment in holdings, compute cumulative qty up to date and price at or before date
        for h in holdings:
            inv_id = h['investment_id']
            qty = 0.0
            price = None
            if inv_id in inv_txs:
                for t in inv_txs[inv_id]:
                    tdate = datetime.strptime(t['date'], '%Y-%m-%d').date() if isinstance(t['date'], str) else t['date']
                    if tdate <= d:
                        # treat sell as negative quantity
                        if t['type'] == 'sell':
                            qty -= float(t['quantity'])
                        else:
                            qty += float(t['quantity'])
                        price = float(t['price'])
            else:
                # If there are no recorded transactions for this investment,
                # assume the current quantity applies to all past dates up to today.
                # (previous code used `d >= today` which produced zeros for historical
                # dates and a single spike on today.)
                qty = h['qty'] if d <= today else 0.0
                price = h['price']

            if price is None:
                price = h['price']

            day_val += qty * price

        series.append({'date': d.isoformat(), 'value': round(day_val, 2)})

    # compute daily change
    today_val = series[-1]['value'] if series else total_value
    yesterday_val = series[-2]['value'] if len(series) >= 2 else 0
    daily_change = today_val - yesterday_val
    daily_change_pct = (daily_change / yesterday_val * 100) if yesterday_val != 0 else 0

    summary = {
        'total_value': round(today_val, 2),
        'daily_change': round(daily_change, 2),
        'daily_change_pct': round(daily_change_pct, 2),
        'cash_available': 0.0,
        'allocations': allocations
    }

    return render_template('home/portfolio.html', summary=summary, holdings=holdings, performance_series=series)
