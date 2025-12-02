from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from gamification import on_transaction_added

# Use local imports (same directory)
try:
    from auth import login_required
    from db import get_db
    from notifications import NotificationEngine
except ImportError:
    # Fallback if auth/db modules don't exist
    def login_required(f):
        return f
    def get_db():
        return None
    # Dummy NotificationEngine for fallback
    class NotificationEngine:
        @staticmethod
        def check_overspending(user_id, category=None):
            return []
        @staticmethod
        def check_budget_warning(user_id):
            return []
        @staticmethod
        def check_unusual_spending(user_id, category, amount):
            return None

bp = Blueprint('transactions', __name__)

@bp.route('/visuals')
@login_required
def show_visuals():
    """Show transaction dashboard"""
    try:
        return render_template('graphs/visuals.html')
    except:
        # Fallback if template doesn't exist
        return render_template('home/dashboard.html')

@bp.route('/transactions')
@login_required
def index():
    """Show all transactions with statistics and deleted transactions"""
    transactions = []
    deleted_transactions = []
    total_income = 0.0
    total_expenses = 0.0
    category_totals = {
        'food': 0.0,
        'transportation': 0.0,
        'entertainment': 0.0,
        'other': 0.0
    }
    
    try:
        db = get_db()
        if db and g.user:
            user_id = g.user['id']
            
            # Check what columns exist in transactions table
            cursor = db.execute("PRAGMA table_info(transactions)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Determine type column name
            type_column = 'transaction_type' if 'transaction_type' in columns else 'type'
            has_category = 'category' in columns
            has_is_active = 'is_active' in columns
            
            # Build query for ACTIVE transactions
            if has_category:
                query = f"""
                    SELECT 
                        id, 
                        description, 
                        amount, 
                        date,
                        {type_column} as type,
                        category
                    FROM transactions 
                    WHERE user_id = ? 
                    {'AND is_active = 1' if has_is_active else ''}
                    ORDER BY date DESC, id DESC
                    LIMIT 50
                """
            else:
                query = f"""
                    SELECT 
                        id, 
                        description, 
                        amount, 
                        date,
                        {type_column} as type,
                        NULL as category
                    FROM transactions 
                    WHERE user_id = ? 
                    {'AND is_active = 1' if has_is_active else ''}
                    ORDER BY date DESC, id DESC
                    LIMIT 50
                """
            
            # Get active transactions
            cursor = db.execute(query, (user_id,))
            transactions = [dict(row) for row in cursor.fetchall()]
            
            # Build query for DELETED transactions
            if has_is_active:
                if has_category:
                    deleted_query = f"""
                        SELECT 
                            id, 
                            description, 
                            amount, 
                            date,
                            {type_column} as type,
                            category,
                            updated_at as deleted_at
                        FROM transactions 
                        WHERE user_id = ? AND is_active = 0
                        ORDER BY updated_at DESC
                    """
                else:
                    deleted_query = f"""
                        SELECT 
                            id, 
                            description, 
                            amount, 
                            date,
                            {type_column} as type,
                            NULL as category,
                            updated_at as deleted_at
                        FROM transactions 
                        WHERE user_id = ? AND is_active = 0
                        ORDER BY updated_at DESC
                    """
                
                # Get deleted transactions
                cursor = db.execute(deleted_query, (user_id,))
                deleted_transactions = [dict(row) for row in cursor.fetchall()]
            
            # Calculate total income (only active)
            income_query = f"""
                SELECT COALESCE(SUM(amount), 0) as total 
                FROM transactions 
                WHERE user_id = ? AND {type_column} = 'income'
                {'AND is_active = 1' if has_is_active else ''}
            """
            income_result = db.execute(income_query, (user_id,)).fetchone()
            total_income = float(income_result['total'])
            
            # Calculate total expenses (only active)
            expense_query = f"""
                SELECT COALESCE(SUM(amount), 0) as total 
                FROM transactions 
                WHERE user_id = ? AND {type_column} = 'expense'
                {'AND is_active = 1' if has_is_active else ''}
            """
            expense_result = db.execute(expense_query, (user_id,)).fetchone()
            total_expenses = float(expense_result['total'])
            
            # Calculate category totals (only if category column exists and only active)
            if has_category:
                category_query = f"""
                    SELECT 
                        category, 
                        COALESCE(SUM(amount), 0) as total 
                    FROM transactions 
                    WHERE user_id = ? AND {type_column} = 'expense' AND category IS NOT NULL
                    {'AND is_active = 1' if has_is_active else ''}
                    GROUP BY category
                """
                category_results = db.execute(category_query, (user_id,)).fetchall()
                
                for row in category_results:
                    cat = row['category']
                    if cat in category_totals:
                        category_totals[cat] = float(row['total'])
            else:
                # Get category totals from expenses table instead
                try:
                    expenses_query = """
                        SELECT 
                            category, 
                            COALESCE(SUM(amount), 0) as total 
                        FROM expenses 
                        WHERE user_id = ? AND is_active = 1
                        GROUP BY category
                    """
                    expense_cats = db.execute(expenses_query, (user_id,)).fetchall()
                    
                    for row in expense_cats:
                        cat = row['category']
                        if cat in category_totals:
                            category_totals[cat] = float(row['total'])
                except:
                    pass  # expenses table might not exist
                
    except Exception as e:
        flash(f'Error loading transactions: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
    
    # Calculate net income
    net_income = total_income - total_expenses
    
    # Get transaction count
    transaction_count = len(transactions)
    
    return render_template(
        'home/transaction.html', 
        transactions=transactions,
        deleted_transactions=deleted_transactions,
        total_income=total_income,
        total_expenses=total_expenses,
        net_income=net_income,
        transaction_count=transaction_count,
        category_totals=category_totals
    )

@bp.route('/transactions/update')
@login_required
def add():
    """Show add transaction form"""
    return render_template('home/update.html')

@bp.route('/transactions/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new transaction"""
    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        amount = request.form.get('amount', '').strip()
        category = request.form.get('category', '').strip().lower()  # Normalize to lowercase
        transaction_type = request.form.get('type', 'expense')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        error = None
        
        # Validation
        if not description:
            error = 'Description is required.'
        elif not amount:
            error = 'Amount is required.'
        elif transaction_type == 'expense' and not category:
            error = 'Category is required for expenses.'
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
                    user_id = g.user['id'] if hasattr(g, 'user') and g.user else 1
                    
                    # Check if table has is_active column
                    cursor = db.execute("PRAGMA table_info(transactions)")
                    columns = [row[1] for row in cursor.fetchall()]
                    has_is_active = 'is_active' in columns
                    
                    # Insert into transactions table WITH category and is_active
                    if has_is_active:
                        db.execute(
                            'INSERT INTO transactions (user_id, transaction_type, category, amount, description, date, is_active)'
                            ' VALUES (?, ?, ?, ?, ?, ?, 1)',
                            (user_id, transaction_type, category if transaction_type == 'expense' else None, 
                             float(amount), description, date)
                        )
                    else:
                        db.execute(
                            'INSERT INTO transactions (user_id, transaction_type, category, amount, description, date)'
                            ' VALUES (?, ?, ?, ?, ?, ?)',
                            (user_id, transaction_type, category if transaction_type == 'expense' else None, 
                             float(amount), description, date)
                        )
                    db.commit()
                    
                    # Also insert into expenses or income table if they exist
                    if transaction_type == 'expense':
                        try:
                            db.execute(
                                'INSERT INTO expenses (user_id, category, amount, description, date, created_by, is_active)'
                                ' VALUES (?, ?, ?, ?, ?, ?, 1)',
                                (user_id, category, float(amount), description, date, user_id)
                            )
                            db.commit()
                        except Exception as e:
                            print(f"Could not insert into expenses table: {e}")
                    elif transaction_type == 'income':
                        try:
                            # Get default income category
                            cat_result = db.execute("SELECT id FROM income_category LIMIT 1").fetchone()
                            if cat_result:
                                category_id = cat_result[0]
                                db.execute(
                                    'INSERT INTO income (user_id, category_id, amount, source, date, created_by, is_active)'
                                    ' VALUES (?, ?, ?, ?, ?, ?, 1)',
                                    (user_id, category_id, float(amount), description, date, user_id)
                                )
                                db.commit()
                        except Exception as e:
                            print(f"Could not insert into income table: {e}")
                    
                    # GAMIFICATION: Award points for logging transaction
                    try:
                        on_transaction_added(g.user['id'])
                    except Exception as e:
                        print(f"Gamification error: {e}")
                    
                    # Trigger notification checks for expenses
                    if transaction_type == 'expense':
                        try:
                            NotificationEngine.check_unusual_spending(user_id, category, float(amount))
                            NotificationEngine.check_budget_warning(user_id)
                            NotificationEngine.check_overspending(user_id)
                        except Exception as notif_error:
                            print(f"Notification error: {notif_error}")
                    
                    flash('Transaction added successfully!', 'success')
                    return redirect(url_for('transactions.index'))
                else:
                    flash('Database not available', 'error')
            except Exception as e:
                flash(f'Error saving transaction: {str(e)}', 'error')
                import traceback
                traceback.print_exc()
    
    return render_template('home/update.html')

@bp.route('/transactions/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Soft delete a transaction"""
    try:
        db = get_db()
        if db:
            # Check if transaction exists and belongs to user
            transaction = db.execute(
                'SELECT id, description, date FROM transactions WHERE id = ? AND user_id = ?', 
                (id, g.user['id'])
            ).fetchone()
            
            if transaction is None:
                flash('Transaction not found.', 'error')
            else:
                # Soft delete - mark as inactive
                db.execute(
                    '''UPDATE transactions 
                       SET is_active = 0, updated_at = CURRENT_TIMESTAMP 
                       WHERE id = ? AND user_id = ?''', 
                    (id, g.user['id'])
                )
                
                # Also soft delete from expenses/income tables if they exist
                try:
                    db.execute(
                        '''UPDATE expenses 
                           SET is_active = 0, updated_at = CURRENT_TIMESTAMP 
                           WHERE user_id = ? AND description = ? AND date = ?''',
                        (g.user['id'], transaction['description'], transaction['date'])
                    )
                except:
                    pass  # expenses table might not exist
                
                try:
                    db.execute(
                        '''UPDATE income 
                           SET is_active = 0, updated_at = CURRENT_TIMESTAMP 
                           WHERE user_id = ? AND source = ? AND date = ?''',
                        (g.user['id'], transaction['description'], transaction['date'])
                    )
                except:
                    pass  # income table might not exist
                
                db.commit()
                flash('Transaction moved to deleted items. You can restore it from the Deleted tab.', 'success')
        else:
            flash('Database not available', 'error')
    except Exception as e:
        flash(f'Error deleting transaction: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('transactions.index'))


@bp.route('/transactions/deleted')
@login_required
def deleted():
    """Show deleted transactions page (redirects to main page with deleted view)"""
    # Since we merged everything into transaction.html, just redirect to index
    # The JavaScript will handle showing the deleted view
    return redirect(url_for('transactions.index') + '#deleted')


@bp.route('/transactions/<int:id>/restore', methods=('POST',))
@login_required
def restore(id):
    """Restore a deleted transaction"""
    try:
        db = get_db()
        if db:
            # Check if transaction exists and belongs to user
            transaction = db.execute(
                'SELECT id, description, date, transaction_type FROM transactions WHERE id = ? AND user_id = ? AND is_active = 0', 
                (id, g.user['id'])
            ).fetchone()
            
            if transaction is None:
                flash('Transaction not found or already active.', 'error')
            else:
                # Restore - mark as active
                db.execute(
                    '''UPDATE transactions 
                       SET is_active = 1, updated_at = CURRENT_TIMESTAMP 
                       WHERE id = ? AND user_id = ?''', 
                    (id, g.user['id'])
                )
                
                # Also restore in expenses/income tables if they exist
                try:
                    db.execute(
                        '''UPDATE expenses 
                           SET is_active = 1, updated_at = CURRENT_TIMESTAMP 
                           WHERE user_id = ? AND description = ? AND date = ?''',
                        (g.user['id'], transaction['description'], transaction['date'])
                    )
                except:
                    pass
                
                try:
                    db.execute(
                        '''UPDATE income 
                           SET is_active = 1, updated_at = CURRENT_TIMESTAMP 
                           WHERE user_id = ? AND source = ? AND date = ?''',
                        (g.user['id'], transaction['description'], transaction['date'])
                    )
                except:
                    pass
                
                db.commit()
                flash('Transaction restored successfully!', 'success')
        else:
            flash('Database not available', 'error')
    except Exception as e:
        flash(f'Error restoring transaction: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('transactions.index'))


@bp.route('/transactions/<int:id>/permanent-delete', methods=('POST',))
@login_required
def permanent_delete(id):
    """Permanently delete a transaction"""
    try:
        db = get_db()
        if db:
            # Check if transaction exists and belongs to user
            transaction = db.execute(
                'SELECT id, description, date FROM transactions WHERE id = ? AND user_id = ? AND is_active = 0', 
                (id, g.user['id'])
            ).fetchone()
            
            if transaction is None:
                flash('Transaction not found or not deleted.', 'error')
            else:
                # Permanently delete from expenses/income tables first
                try:
                    db.execute(
                        'DELETE FROM expenses WHERE user_id = ? AND description = ? AND date = ?',
                        (g.user['id'], transaction['description'], transaction['date'])
                    )
                except:
                    pass
                
                try:
                    db.execute(
                        'DELETE FROM income WHERE user_id = ? AND source = ? AND date = ?',
                        (g.user['id'], transaction['description'], transaction['date'])
                    )
                except:
                    pass
                
                # Permanently delete from transactions table
                db.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', (id, g.user['id']))
                
                db.commit()
                flash('Transaction permanently deleted.', 'warning')
        else:
            flash('Database not available', 'error')
    except Exception as e:
        flash(f'Error permanently deleting transaction: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('transactions.index'))


@bp.route('/transactions/permanent-delete-all', methods=('GET', 'POST'))
@login_required
def permanent_delete_all():
    """Permanently delete all deleted transactions"""
    try:
        db = get_db()
        if db:
            # Get all deleted transactions
            deleted_trans = db.execute(
                'SELECT id, description, date FROM transactions WHERE user_id = ? AND is_active = 0',
                (g.user['id'],)
            ).fetchall()
            
            count = len(deleted_trans)
            
            if count > 0:
                # Delete from expenses/income tables
                for trans in deleted_trans:
                    try:
                        db.execute(
                            'DELETE FROM expenses WHERE user_id = ? AND description = ? AND date = ?',
                            (g.user['id'], trans['description'], trans['date'])
                        )
                    except:
                        pass
                    
                    try:
                        db.execute(
                            'DELETE FROM income WHERE user_id = ? AND source = ? AND date = ?',
                            (g.user['id'], trans['description'], trans['date'])
                        )
                    except:
                        pass
                
                # Permanently delete all inactive transactions
                db.execute('DELETE FROM transactions WHERE user_id = ? AND is_active = 0', (g.user['id'],))
                
                db.commit()
                flash(f'{count} transaction(s) permanently deleted.', 'warning')
            else:
                flash('No deleted transactions to remove.', 'info')
        else:
            flash('Database not available', 'error')
    except Exception as e:
        flash(f'Error permanently deleting transactions: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('transactions.index'))

# Helper function to get available categories
def get_categories():
    """Get list of transaction categories"""
    return ['food', 'transportation', 'entertainment', 'other']

# Make categories available to templates
@bp.app_template_global()
def transaction_categories():
    return get_categories()
