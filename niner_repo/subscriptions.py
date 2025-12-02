from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g
from db import get_db
from auth import login_required
from datetime import datetime, timedelta
import re

bp = Blueprint('subscriptions', __name__, url_prefix='/subscriptions')

@bp.route('/')
@login_required
def index():
    """View all subscriptions"""
    db = get_db()
    
    # Get all active subscriptions
    subscriptions = db.execute(
        '''SELECT s.*, sc.icon, sc.color
           FROM subscriptions s
           LEFT JOIN subscription_categories sc ON s.category = sc.name
           WHERE s.user_id = ? AND s.is_active = 1
           ORDER BY s.next_billing_date ASC''',
        (g.user['id'],)
    ).fetchall()
    
    # Get subscription categories
    categories = db.execute(
        'SELECT * FROM subscription_categories ORDER BY name'
    ).fetchall()
    
    # Calculate total monthly cost
    total_monthly = calculate_total_monthly_cost(subscriptions)
    
    # Upcoming bills (next 30 days)
    upcoming = [s for s in subscriptions if is_upcoming(s['next_billing_date'], 30)]
    
    return render_template(
        'subscriptions/index.html',
        subscriptions=subscriptions,
        categories=categories,
        total_monthly=total_monthly,
        upcoming=upcoming
    )

@bp.route('/add', methods=['POST'])
@login_required
def add():
    """Manually add a subscription"""
    name = request.form.get('name')
    amount = request.form.get('amount')
    frequency = request.form.get('frequency')
    category = request.form.get('category')
    next_billing_date = request.form.get('next_billing_date')
    notes = request.form.get('notes', '')
    
    # Validation
    error = None
    if not name:
        error = 'Subscription name is required.'
    elif not amount or float(amount) <= 0:
        error = 'Valid amount is required.'
    elif frequency not in ['daily', 'weekly', 'monthly', 'yearly']:
        error = 'Invalid frequency.'
    elif not next_billing_date:
        error = 'Next billing date is required.'
    
    if error:
        flash(error, 'danger')
        return redirect(url_for('subscriptions.index'))
    
    # Insert subscription
    db = get_db()
    
    # Create subscription
    cursor = db.execute(
        '''INSERT INTO subscriptions 
           (user_id, name, amount, frequency, category, next_billing_date, 
            start_date, notes, auto_detected)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)''',
        (g.user['id'], name, float(amount), frequency, category, 
         next_billing_date, datetime.now().date().isoformat(), notes)
    )
    subscription_id = cursor.lastrowid
    
    # ALSO CREATE TRANSACTION - Map subscription category to expense category
    expense_category = map_subscription_to_expense_category(category)
    
    try:
        # Check if transactions table has category column
        cursor = db.execute("PRAGMA table_info(transactions)")
        columns = [row[1] for row in cursor.fetchall()]
        has_category = 'category' in columns
        
        # Insert into transactions table
        if has_category:
            trans_cursor = db.execute(
                '''INSERT INTO transactions 
                   (user_id, transaction_type, category, amount, description, date, is_active)
                   VALUES (?, 'expense', ?, ?, ?, ?, 1)''',
                (g.user['id'], expense_category, float(amount), 
                 f'{name} (Subscription)', next_billing_date)
            )
        else:
            trans_cursor = db.execute(
                '''INSERT INTO transactions 
                   (user_id, transaction_type, amount, description, date, is_active)
                   VALUES (?, 'expense', ?, ?, ?, 1)''',
                (g.user['id'], float(amount), f'{name} (Subscription)', next_billing_date)
            )
        
        transaction_id = trans_cursor.lastrowid
        
        # Link subscription to transaction
        db.execute(
            'UPDATE subscriptions SET transaction_id = ? WHERE id = ?',
            (transaction_id, subscription_id)
        )
        
        # Also add to expenses table if it exists
        try:
            db.execute(
                '''INSERT INTO expenses 
                   (user_id, category, amount, description, date, created_by, is_active)
                   VALUES (?, ?, ?, ?, ?, ?, 1)''',
                (g.user['id'], expense_category, float(amount), 
                 f'{name} (Subscription)', next_billing_date, g.user['id'])
            )
        except:
            pass  # expenses table might not exist or have different schema
        
    except Exception as e:
        print(f"Error creating transaction for subscription: {e}")
    
    db.commit()
    
    flash(f'Subscription "{name}" added successfully and recorded as expense!', 'success')
    return redirect(url_for('subscriptions.index'))

@bp.route('/<int:id>/edit', methods=['POST'])
@login_required
def edit(id):
    """Edit a subscription"""
    db = get_db()
    subscription = db.execute(
        'SELECT * FROM subscriptions WHERE id = ? AND user_id = ?',
        (id, g.user['id'])
    ).fetchone()
    
    if not subscription:
        flash('Subscription not found.', 'danger')
        return redirect(url_for('subscriptions.index'))
    
    # Update fields
    name = request.form.get('name', subscription['name'])
    amount = request.form.get('amount', subscription['amount'])
    frequency = request.form.get('frequency', subscription['frequency'])
    category = request.form.get('category', subscription['category'])
    next_billing_date = request.form.get('next_billing_date', subscription['next_billing_date'])
    notes = request.form.get('notes', subscription['notes'])
    
    db.execute(
        '''UPDATE subscriptions 
           SET name = ?, amount = ?, frequency = ?, category = ?, 
               next_billing_date = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ? AND user_id = ?''',
        (name, float(amount), frequency, category, next_billing_date, 
         notes, id, g.user['id'])
    )
    db.commit()
    
    flash(f'Subscription "{name}" updated successfully!', 'success')
    return redirect(url_for('subscriptions.index'))

@bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    """Cancel/deactivate a subscription"""
    db = get_db()
    
    # Get the subscription and verify ownership
    subscription = db.execute(
        'SELECT * FROM subscriptions WHERE id = ? AND user_id = ?',
        (id, g.user['id'])
    ).fetchone()
    
    if not subscription:
        flash('Subscription not found.', 'danger')
        return redirect(url_for('subscriptions.index'))
    
    # Check if already cancelled
    if subscription['is_active'] == 0:
        flash(f'Subscription "{subscription["name"]}" is already cancelled.', 'info')
        return redirect(url_for('subscriptions.index'))
    
    # Cancel the subscription
    db.execute(
        '''UPDATE subscriptions 
           SET is_active = 0, end_date = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ? AND user_id = ?''',
        (datetime.now().date().isoformat(), id, g.user['id'])
    )
    db.commit()
    
    flash(f'✅ Subscription "{subscription["name"]}" has been cancelled successfully.', 'success')
    return redirect(url_for('subscriptions.index'))

@bp.route('/<int:id>/reactivate', methods=['POST'])
@login_required
def reactivate(id):
    """Reactivate a cancelled subscription"""
    db = get_db()
    db.execute(
        '''UPDATE subscriptions 
           SET is_active = 1, end_date = NULL, updated_at = CURRENT_TIMESTAMP
           WHERE id = ? AND user_id = ?''',
        (id, g.user['id'])
    )
    db.commit()
    
    flash('Subscription reactivated successfully!', 'success')
    return redirect(url_for('subscriptions.index'))

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Permanently delete a subscription"""
    db = get_db()
    subscription = db.execute(
        'SELECT name FROM subscriptions WHERE id = ? AND user_id = ?',
        (id, g.user['id'])
    ).fetchone()
    
    if not subscription:
        flash('Subscription not found.', 'danger')
        return redirect(url_for('subscriptions.index'))
    
    db.execute('DELETE FROM subscriptions WHERE id = ? AND user_id = ?', (id, g.user['id']))
    db.commit()
    
    flash(f'Subscription "{subscription["name"]}" deleted permanently.', 'warning')
    return redirect(url_for('subscriptions.index'))

@bp.route('/detect', methods=['POST'])
@login_required
def detect_recurring():
    """Automatically detect recurring transactions from transaction history"""
    db = get_db()
    
    # Find transactions that occur regularly
    recurring_patterns = find_recurring_patterns(g.user['id'])
    
    detected_count = 0
    for pattern in recurring_patterns:
        # Check if subscription already exists
        existing = db.execute(
            '''SELECT id FROM subscriptions 
               WHERE user_id = ? AND name = ? AND is_active = 1''',
            (g.user['id'], pattern['name'])
        ).fetchone()
        
        if not existing:
            # Map category to subscription category
            sub_category = map_expense_to_subscription_category(pattern.get('category', 'other'))
            
            # Create subscription from pattern
            db.execute(
                '''INSERT INTO subscriptions 
                   (user_id, name, amount, frequency, category, next_billing_date, 
                    start_date, auto_detected, transaction_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)''',
                (g.user['id'], pattern['name'], pattern['amount'], 
                 pattern['frequency'], sub_category, pattern['next_date'], 
                 pattern['start_date'], pattern['transaction_id'])
            )
            detected_count += 1
    
    db.commit()
    
    if detected_count > 0:
        flash(f'🎉 Detected {detected_count} new recurring payment(s)!', 'success')
    else:
        flash('No new recurring payments detected. Try adding transactions first!', 'info')
    
    return redirect(url_for('subscriptions.index'))

# Helper functions
def calculate_total_monthly_cost(subscriptions):
    """Calculate total monthly cost of all subscriptions"""
    total = 0
    for sub in subscriptions:
        if sub['frequency'] == 'daily':
            total += sub['amount'] * 30
        elif sub['frequency'] == 'weekly':
            total += sub['amount'] * 4
        elif sub['frequency'] == 'monthly':
            total += sub['amount']
        elif sub['frequency'] == 'yearly':
            total += sub['amount'] / 12
    return round(total, 2)

def is_upcoming(next_billing_date, days=30):
    """Check if billing date is within next N days"""
    try:
        billing_date = datetime.fromisoformat(next_billing_date)
        days_until = (billing_date - datetime.now()).days
        return 0 <= days_until <= days
    except:
        return False

def find_recurring_patterns(user_id):
    """Detect recurring payment patterns from transactions"""
    db = get_db()
    
    # Get all expense transactions from the last 6 months
    six_months_ago = (datetime.now() - timedelta(days=180)).date().isoformat()
    
    # Check which columns exist
    cursor = db.execute("PRAGMA table_info(transactions)")
    columns = [row[1] for row in cursor.fetchall()]
    type_column = 'transaction_type' if 'transaction_type' in columns else 'type'
    has_category = 'category' in columns
    
    # Build query
    if has_category:
        query = f'''SELECT id, description, amount, date, category
                   FROM transactions 
                   WHERE user_id = ? AND {type_column} = 'expense' 
                   AND date >= ? AND is_active = 1
                   ORDER BY date DESC'''
    else:
        query = f'''SELECT id, description, amount, date, NULL as category
                   FROM transactions 
                   WHERE user_id = ? AND {type_column} = 'expense' 
                   AND date >= ? AND is_active = 1
                   ORDER BY date DESC'''
    
    transactions = db.execute(query, (user_id, six_months_ago)).fetchall()
    
    patterns = []
    
    # Group by similar description and amount
    grouped = {}
    for t in transactions:
        # Normalize description
        desc = normalize_description(t['description'])
        amount = round(t['amount'], 2)
        key = f"{desc}_{amount}"
        
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(dict(t))
    
    # Find patterns with 3+ occurrences
    for key, txns in grouped.items():
        if len(txns) >= 3:
            # Calculate frequency
            dates = [datetime.fromisoformat(t['date']) for t in txns]
            dates.sort()
            
            # Check if dates are evenly spaced
            intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
            avg_interval = sum(intervals) / len(intervals)
            
            # Determine frequency
            frequency = None
            if 25 <= avg_interval <= 35:
                frequency = 'monthly'
            elif 6 <= avg_interval <= 8:
                frequency = 'weekly'
            elif 360 <= avg_interval <= 370:
                frequency = 'yearly'
            
            if frequency:
                # Calculate next billing date
                last_date = dates[-1]
                if frequency == 'monthly':
                    next_date = last_date + timedelta(days=30)
                elif frequency == 'weekly':
                    next_date = last_date + timedelta(days=7)
                elif frequency == 'yearly':
                    next_date = last_date + timedelta(days=365)
                
                patterns.append({
                    'name': txns[0]['description'],
                    'amount': txns[0]['amount'],
                    'category': txns[0].get('category', 'Other'),
                    'frequency': frequency,
                    'next_date': next_date.date().isoformat(),
                    'start_date': dates[0].date().isoformat(),
                    'transaction_id': txns[-1]['id']
                })
    
    return patterns

def normalize_description(description):
    """Normalize transaction description for pattern matching"""
    # Remove dates, numbers, special chars
    normalized = re.sub(r'\d+', '', description)
    normalized = re.sub(r'[^a-zA-Z\s]', '', normalized)
    normalized = normalized.strip().lower()
    return normalized

def map_subscription_to_expense_category(sub_category):
    """Map subscription category to transaction expense category"""
    mapping = {
        'Streaming': 'entertainment',
        'Music': 'entertainment',
        'Gaming': 'entertainment',
        'Software': 'other',
        'Cloud Storage': 'other',
        'Fitness': 'other',
        'News': 'other',
        'Utilities': 'other',
        'Insurance': 'other',
    }
    return mapping.get(sub_category, 'other')

def map_expense_to_subscription_category(expense_category):
    """Map transaction expense category to subscription category"""
    mapping = {
        'entertainment': 'Streaming',
        'food': 'Other',
        'transportation': 'Other',
        'other': 'Other'
    }
    return mapping.get(expense_category, 'Other')