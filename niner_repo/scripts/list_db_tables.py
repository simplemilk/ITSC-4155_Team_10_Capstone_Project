import sqlite3
import os

def list_tables(path):
    print('DB:', os.path.abspath(path))
    if not os.path.exists(path):
        print('NOT FOUND')
        return
    conn = sqlite3.connect(path)
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    rows = [r[0] for r in cur.fetchall()]
    print('Tables:', rows)
    if 'positions' in rows:
        sch = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='positions'").fetchone()[0]
        print('\nPositions schema:\n', sch)
    conn.close()

if __name__ == '__main__':
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    list_tables(os.path.join(base, 'niner_finance.sqlite'))
    list_tables(os.path.join(base, 'instance', 'niner_finance.sqlite'))
    list_tables(os.path.join(base, 'niner_finance.sqlite.backup'))
