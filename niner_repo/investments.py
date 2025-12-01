from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from db import get_db
from auth import login_required

bp = Blueprint('investments', __name__, url_prefix='/investments')


@bp.route('/')
@login_required
def index():
    db = get_db()
    user_id = g.user['id']
    # List user's positions joined with investments
    rows = db.execute('''
        SELECT p.id as position_id, p.quantity, p.avg_cost, i.id as investment_id, i.ticker, i.name, at.name as asset_type
        FROM positions p
        JOIN investments i ON p.investment_id = i.id
        JOIN asset_types at ON i.asset_type_id = at.id
        WHERE p.user_id = ?
        ORDER BY i.ticker
    ''', (user_id,)).fetchall()

    positions = [dict(r) for r in rows]
    return render_template('home/investments.html', positions=positions)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    db = get_db()
    if request.method == 'POST':
        ticker = request.form.get('ticker', '').strip().upper()
        name = request.form.get('name', '').strip()
        asset_type_id = request.form.get('asset_type_id')
        exchange = request.form.get('exchange', '').strip()

        # basic validation
        errors = []
        if not ticker:
            errors.append('Ticker is required')
        if not name:
            errors.append('Name is required')
        try:
            asset_type_id = int(asset_type_id)
        except Exception:
            errors.append('Asset type is required')

        if errors:
            for e in errors:
                flash(e, 'error')
        else:
            # insert or get existing investment
            cur = db.execute('SELECT id FROM investments WHERE ticker = ? AND exchange = ?', (ticker, exchange))
            row = cur.fetchone()
            if row:
                investment_id = row['id']
            else:
                cur2 = db.execute('INSERT INTO investments (ticker, name, asset_type_id, exchange) VALUES (?,?,?,?)',
                                  (ticker, name, asset_type_id, exchange))
                investment_id = cur2.lastrowid

            # create empty position for user
            try:
                db.execute('INSERT INTO positions (user_id, investment_id, quantity, avg_cost) VALUES (?,?,?,?)',
                           (g.user['id'], investment_id, 0, 0))
                db.commit()
                flash(f'Investment {ticker} added to your portfolio', 'success')
                return redirect(url_for('investments.index'))
            except Exception as e:
                flash(f'Error creating position: {e}', 'error')

    # GET: render form
    asset_types = db.execute('SELECT id, name FROM asset_types ORDER BY name').fetchall()
    return render_template('home/investment_form.html', asset_types=asset_types, action='Create')


@bp.route('/<int:position_id>/edit', methods=('GET', 'POST'))
@login_required
def edit(position_id):
    db = get_db()
    user_id = g.user['id']
    pos = db.execute('SELECT p.id as position_id, p.quantity, p.avg_cost, p.investment_id, i.ticker, i.name, i.exchange, i.asset_type_id FROM positions p JOIN investments i ON p.investment_id = i.id WHERE p.id = ? AND p.user_id = ?', (position_id, user_id)).fetchone()
    if not pos:
        flash('Position not found', 'error')
        return redirect(url_for('investments.index'))

    if request.method == 'POST':
        try:
            quantity = float(request.form.get('quantity', pos['quantity']))
            avg_cost = float(request.form.get('avg_cost', pos['avg_cost']))
            db.execute('UPDATE positions SET quantity = ?, avg_cost = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (quantity, avg_cost, position_id))
            db.commit()
            flash('Position updated', 'success')
            return redirect(url_for('investments.index'))
        except ValueError:
            flash('Invalid numeric value', 'error')

    return render_template('home/investment_form.html', position=pos, action='Edit')


@bp.route('/<int:position_id>/delete', methods=('POST',))
@login_required
def delete(position_id):
    db = get_db()
    user_id = g.user['id']
    # verify ownership
    pos = db.execute('SELECT id FROM positions WHERE id = ? AND user_id = ?', (position_id, user_id)).fetchone()
    if not pos:
        flash('Position not found', 'error')
        return redirect(url_for('investments.index'))

    db.execute('DELETE FROM positions WHERE id = ?', (position_id,))
    db.commit()
    flash('Position removed', 'success')
    return redirect(url_for('investments.index'))
