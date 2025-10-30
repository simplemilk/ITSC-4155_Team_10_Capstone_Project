from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from datetime import datetime
from decimal import Decimal, InvalidOperation

# Use local imports (same directory)
try:
    from auth import login_required
    from db import get_db
except ImportError:
    # Fallback if auth/db modules don't exist
    def login_required(f):
        return f
    def get_db():
        return None

bp = Blueprint('transactions', __name__)

@bp.route('/visuals')
def show_visuals():
    """Show transaction dashboard"""
    try:
        return render_template('graphs/visuals.html')
    except:
        # Fallback if template doesn't exist
        return render_template('home/dashboard.html')

@bp.route('/transactions')
def index():
    """Show all transactions"""
    transactions = []
    
    # Try to get transactions from database
    try:
        db = get_db()
        if db:
            transactions = db.execute(
                'SELECT t.id, t.description, t.amount, t.category, t.date, t.type'
                ' FROM transactions t'
                ' ORDER BY t.date DESC'
            ).fetchall()
    except Exception as e:
        flash(f'Error loading transactions: {str(e)}', 'error')
    
    return render_template('home/index.html', transactions=transactions)

@bp.route('/transactions/update')
def add():
    """Show add transaction form"""
    return render_template('home/update.html')

@bp.route('/transactions/create', methods=('GET', 'POST'))
def create():
    """Create a new transaction"""
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        amount = request.form.get('amount', '').strip()
        category = request.form.get('category', '').strip()
        transaction_type = request.form.get('type', 'expense')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        error = None
        
        # Validation
        if not description:
            error = 'Description is required.'
        elif not amount:
            error = 'Amount is required.'
        elif not category:
            error = 'Category is required.'
        else:
            try:
                amount = Decimal(amount)
                if amount <= 0:
                    error = 'Amount must be greater than 0.'
            except (InvalidOperation, ValueError):
                error = 'Invalid amount format.'
        
        if error is not None:
            flash(error, 'error')
        else:
            # Try to save to database
            try:
                db = get_db()
                if db:
                    db.execute(
                        'INSERT INTO transactions (description, amount, category, type, date, user_id)'
                        ' VALUES (?, ?, ?, ?, ?, ?)',
                        (description, float(amount), category, transaction_type, date, 1)  # Default user_id = 1
                    )
                    db.commit()
                    flash('Transaction added successfully!', 'success')
                    return redirect(url_for('transactions.index'))
                else:
                    flash('Database not available', 'error')
            except Exception as e:
                flash(f'Error saving transaction: {str(e)}', 'error')
    
    return render_template('home/update.html')

@bp.route('/transactions/<int:id>')
def detail(id):
    """Show transaction details"""
    transaction = None
    
    try:
        db = get_db()
        if db:
            transaction = db.execute(
                'SELECT * FROM transactions WHERE id = ?', (id,)
            ).fetchone()
            
        if transaction is None:
            abort(404)
            
    except Exception as e:
        flash(f'Error loading transaction: {str(e)}', 'error')
        return redirect(url_for('home/index.html'))
    
    return render_template('home/transaction.html', transaction=transaction)

@bp.route('/transactions/<int:id>/edit')
def edit(id):
    """Show edit transaction form"""
    transaction = None
    
    try:
        db = get_db()
        if db:
            transaction = db.execute(
                'SELECT * FROM transactions WHERE id = ?', (id,)
            ).fetchone()
            
        if transaction is None:
            abort(404)
            
    except Exception as e:
        flash(f'Error loading transaction: {str(e)}', 'error')
        return redirect(url_for('transactions.index'))
    
    return render_template('home/update.html', transaction=transaction)

@bp.route('/transactions/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    """Update a transaction"""
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        amount = request.form.get('amount', '').strip()
        category = request.form.get('category', '').strip()
        transaction_type = request.form.get('type', 'expense')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        error = None
        
        # Validation
        if not description:
            error = 'Description is required.'
        elif not amount:
            error = 'Amount is required.'
        elif not category:
            error = 'Category is required.'
        else:
            try:
                amount = Decimal(amount)
                if amount <= 0:
                    error = 'Amount must be greater than 0.'
            except (InvalidOperation, ValueError):
                error = 'Invalid amount format.'
        
        if error is not None:
            flash(error, 'error')
        else:
            try:
                db = get_db()
                if db:
                    db.execute(
                        'UPDATE transactions SET description = ?, amount = ?, category = ?, type = ?, date = ?'
                        ' WHERE id = ?',
                        (description, float(amount), category, transaction_type, date, id)
                    )
                    db.commit()
                    flash('Transaction updated successfully!', 'success')
                    return redirect(url_for('transactions.detail', id=id))
                else:
                    flash('Database not available', 'error')
            except Exception as e:
                flash(f'Error updating transaction: {str(e)}', 'error')
    
    # If GET request or error, show the edit form
    return redirect(url_for('transactions.edit', id=id))

@bp.route('/transactions/<int:id>/delete', methods=('POST',))
def delete(id):
    """Delete a transaction"""
    try:
        db = get_db()
        if db:
            # Check if transaction exists
            transaction = db.execute('SELECT id FROM transactions WHERE id = ?', (id,)).fetchone()
            if transaction is None:
                flash('Transaction not found.', 'error')
            else:
                db.execute('DELETE FROM transactions WHERE id = ?', (id,))
                db.commit()
                flash('Transaction deleted successfully!', 'success')
        else:
            flash('Database not available', 'error')
    except Exception as e:
        flash(f'Error deleting transaction: {str(e)}', 'error')
    
    return redirect(url_for('transactions.index'))

@bp.route('/transactions/stats')
def stats():
    """Show transaction statistics"""
    stats_data = {
        'total_income': 0.0,
        'total_expenses': 0.0,
        'net_balance': 0.0,
        'transaction_count': 0,
        'categories': {}
    }
    
    try:
        db = get_db()
        if db:
            # Get total income
            income_result = db.execute(
                "SELECT SUM(amount) as total FROM transactions WHERE type = 'income'"
            ).fetchone()
            stats_data['total_income'] = float(income_result['total'] or 0)
            
            # Get total expenses
            expense_result = db.execute(
                "SELECT SUM(amount) as total FROM transactions WHERE type = 'expense'"
            ).fetchone()
            stats_data['total_expenses'] = float(expense_result['total'] or 0)
            
            # Calculate net balance
            stats_data['net_balance'] = stats_data['total_income'] - stats_data['total_expenses']
            
            # Get transaction count
            count_result = db.execute('SELECT COUNT(*) as count FROM transactions').fetchone()
            stats_data['transaction_count'] = int(count_result['count'] or 0)
            
            # Get category breakdown
            category_results = db.execute(
                'SELECT category, SUM(amount) as total, COUNT(*) as count'
                ' FROM transactions GROUP BY category ORDER BY total DESC'
            ).fetchall()
            
            for row in category_results:
                stats_data['categories'][row['category']] = {
                    'total': float(row['total']),
                    'count': int(row['count'])
                }
                
    except Exception as e:
        flash(f'Error loading statistics: {str(e)}', 'error')
    
    return render_template('home/dashboard.html', stats=stats_data)

# Helper function to get available categories
def get_categories():
    """Get list of transaction categories"""
    default_categories = [
        'Food & Dining',
        'Transportation',
        'Shopping',
        'Entertainment',
        'Bills & Utilities',
        'Healthcare',
        'Education',
        'Travel',
        'Income',
        'Other'
    ]
    
    try:
        db = get_db()
        if db:
            # Get categories from existing transactions
            db_categories = db.execute(
                'SELECT DISTINCT category FROM transactions ORDER BY category'
            ).fetchall()
            
            existing_categories = [row['category'] for row in db_categories if row['category']]
            
            # Combine with defaults, remove duplicates
            all_categories = list(set(default_categories + existing_categories))
            all_categories.sort()
            
            return all_categories
    except:
        pass
    
    return default_categories

# Make categories available to templates
@bp.app_template_global()
def transaction_categories():
    return get_categories()