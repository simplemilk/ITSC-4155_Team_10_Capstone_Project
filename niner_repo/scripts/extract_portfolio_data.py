import os, json, sqlite3
from datetime import datetime, timedelta, date

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_path = os.path.join(project_root, 'niner_finance.sqlite')
if not os.path.exists(db_path):
    print('DB_NOT_FOUND', db_path)
    raise SystemExit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# pick a user (demo user or first user)
u = cur.execute("SELECT id, username FROM user LIMIT 1").fetchone()
if not u:
    print('NO_USER')
    raise SystemExit(1)
user_id = u['id']
print('USING_USER', u['username'], user_id)

# Fetch positions joined with investments and asset types
rows = cur.execute('''
        SELECT p.id as position_id, p.quantity, p.avg_cost, i.id as investment_id, i.ticker, i.name, i.asset_type_id, at.name as asset_type
        FROM positions p
        JOIN investments i ON p.investment_id = i.id
        LEFT JOIN asset_types at ON i.asset_type_id = at.id
        WHERE p.user_id = ?
    ''', (user_id,)).fetchall()

holdings = []
total_value = 0.0

def _get_last_price_for_investment(cur, investment_id):
    r = cur.execute('SELECT price, date FROM investment_transactions WHERE investment_id = ? ORDER BY date DESC LIMIT 1', (investment_id,)).fetchone()
    if r:
        return float(r['price'])
    return None

for r in rows:
    qty = float(r['quantity'])
    last_price = _get_last_price_for_investment(cur, r['investment_id'])
    price = last_price if last_price is not None else float(r['avg_cost'] or 0)
    value = qty * price
    avg_cost = float(r['avg_cost'] or 0)
    pl_amount = (price - avg_cost) * qty
    pl_percent = ((price - avg_cost) / avg_cost * 100) if avg_cost not in (0, None) else 0
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

# allocations
alloc_map = {}
for h in holdings:
    alloc_map.setdefault(h['asset_type'], 0.0)
    alloc_map[h['asset_type']] += h['value']
allocations = [{'name': k, 'value': v, 'color': '#4f46e5'} for k, v in alloc_map.items()]
if total_value > 0:
    for h in holdings:
        h['allocation'] = round((h['value'] / total_value) * 100, 1)
else:
    for h in holdings:
        h['allocation'] = 0.0

# transactions
tx_rows = cur.execute('SELECT investment_id, date, type, quantity, price FROM investment_transactions WHERE user_id = ? ORDER BY date', (user_id,)).fetchall()
txs = [dict(x) for x in tx_rows]
today = date.today()
days = 30
series = []
inv_txs = {}
for t in txs:
    inv_txs.setdefault(t['investment_id'], []).append(t)

for i in range(days-1, -1, -1):
    d = today - timedelta(days=i)
    day_val = 0.0
    for h in holdings:
        inv_id = h['investment_id']
        qty = 0.0
        price = None
        if inv_id in inv_txs:
            for t in inv_txs[inv_id]:
                tdate = datetime.strptime(t['date'], '%Y-%m-%d').date() if isinstance(t['date'], str) else t['date']
                if tdate <= d:
                    if t['type'] == 'sell':
                        qty -= float(t['quantity'])
                    else:
                        qty += float(t['quantity'])
                    price = float(t['price'])
        else:
            qty = h['qty'] if d <= today else 0.0
            price = h['price']
        if price is None:
            price = h['price']
        day_val += qty * price
    series.append({'date': d.isoformat(), 'value': round(day_val, 2)})

print('PERF_LEN', len(series))
print('PERF_SAMPLE', json.dumps(series[-7:], indent=2))
print('ALLOC', json.dumps(allocations, indent=2))

conn.close()
