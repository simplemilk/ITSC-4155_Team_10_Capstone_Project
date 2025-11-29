import sqlite3
import os
import datetime

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'niner_finance.sqlite')
print('Using DB:', db_path)
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# find demo user
cur.execute("SELECT id FROM user WHERE username='demo'")
row = cur.fetchone()
if not row:
    print('Demo user not found; aborting')
    conn.close()
    raise SystemExit(1)

demo_id = row[0]
print('Demo user id:', demo_id)

# find investments
cur.execute("SELECT id, ticker FROM investments WHERE ticker IN ('AAPL','BTC','VOO')")
invs = {r['ticker']: r['id'] for r in cur.fetchall()}
print('Investments found:', invs)

# insert positions
def insert_position(ticker, qty, avg_cost):
    iid = invs.get(ticker)
    if not iid:
        print('Investment', ticker, 'not found; skipping')
        return
    cur.execute('INSERT OR IGNORE INTO positions (user_id, investment_id, quantity, avg_cost) VALUES (?,?,?,?)', (demo_id, iid, qty, avg_cost))

insert_position('AAPL', 25, 135.2)
insert_position('VOO', 50, 350.0)
insert_position('BTC', 0.05, 20000.0)
conn.commit()
print('Positions inserted/ensured')

# insert sample transactions (if table exists)
try:
    today = datetime.date.today()
    txs = [
        (demo_id, invs.get('AAPL'), 'buy', 25, 170.0, 0, 25*170.0, (today - datetime.timedelta(days=10)).isoformat()),
        (demo_id, invs.get('VOO'), 'buy', 50, 360.0, 0, 50*360.0, (today - datetime.timedelta(days=20)).isoformat()),
        (demo_id, invs.get('BTC'), 'buy', 0.05, 18000.0, 0, 0.05*18000.0, (today - datetime.timedelta(days=30)).isoformat()),
    ]
    for t in txs:
        if t[1] is None:
            continue
        cur.execute('INSERT INTO investment_transactions (user_id, investment_id, type, quantity, price, fees, total, date) VALUES (?,?,?,?,?,?,?,?)', t)
    conn.commit()
    print('Sample transactions inserted')
except Exception as e:
    print('Could not insert transactions:', e)

conn.close()
