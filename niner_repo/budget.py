from datetime import datetime, timedelta
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
from werkzeug.exceptions import abort
from auth import login_required
from db import get_db
import json
from gamification import on_budget_created

bp = Blueprint('budget', __name__, url_prefix='/budget')

def get_financial_summary(user_id):
    """Get comprehensive financial summary for consistent data across pages"""
    db = get_db()
    
    # Get current week dates
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get current month dates  
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    # Current week budget
    current_budget_row = db.execute('''
        SELECT * FROM budgets 
        WHERE user_id = ? 
        AND week_start_date = ?
        ORDER BY created_at DESC LIMIT 1
    ''', (user_id, week_start.isoformat())).fetchone()
    
    # Convert Row to dict
    current_budget = dict(current_budget_row) if current_budget_row else None
    
    # Weekly spending by category
    week_spending_rows = db.execute('''
        SELECT 
            category,
            COALESCE(SUM(amount), 0) as spent
        FROM transactions 
        WHERE user_id = ? 
        AND type = 'expense'
        AND date >= ? AND date <= ?
        GROUP BY category
    ''', (user_id, week_start.isoformat(), week_end.isoformat())).fetchall()
    
    # Convert to list of dicts
    week_spending = [dict(row) for row in week_spending_rows]
    
    # Total weekly spending
    total_weekly_spent_row = db.execute('''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM transactions 
        WHERE user_id = ? 
        AND type = 'expense'
        AND date >= ? AND date <= ?
    ''', (user_id, week_start.isoformat(), week_end.isoformat())).fetchone()
    
    total_weekly_spent = dict(total_weekly_spent_row) if total_weekly_spent_row else {'total': 0}
    
    # Monthly income
    monthly_income_row = db.execute('''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM transactions 
        WHERE user_id = ? 
        AND type = 'income'
        AND date >= ? AND date <= ?
    ''', (user_id, month_start.isoformat(), month_end.isoformat())).fetchone()
    
    monthly_income = dict(monthly_income_row) if monthly_income_row else {'total': 0}
    
    # Monthly expenses
    monthly_expenses_row = db.execute('''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM transactions 
        WHERE user_id = ? 
        AND type = 'expense'
        AND date >= ? AND date <= ?
    ''', (user_id, month_start.isoformat(), month_end.isoformat())).fetchone()
    
    monthly_expenses = dict(monthly_expenses_row) if monthly_expenses_row else {'total': 0}
    
    # Recent transactions
    recent_transactions_rows = db.execute('''
        SELECT * FROM transactions 
        WHERE user_id = ? 
        ORDER BY date DESC, created_at DESC 
        LIMIT 5
    ''', (user_id,)).fetchall()
    
    # Convert to list of dicts
    recent_transactions = [dict(row) for row in recent_transactions_rows]
    
    # Process budget data
    total_budget = float(current_budget['total_amount']) if current_budget else 0.0
    total_spent = float(total_weekly_spent['total']) if total_weekly_spent else 0.0
    
    # Category data with defaults
    categories = {
        'Food': {'budget': 0.0, 'spent': 0.0},
        'Transportation': {'budget': 0.0, 'spent': 0.0},
        'Entertainment': {'budget': 0.0, 'spent': 0.0},
        'Other': {'budget': 0.0, 'spent': 0.0}
    }
    
    # Set budget amounts if budget exists
    if current_budget:
        categories['Food']['budget'] = float(current_budget['food_budget'] or 0)
        categories['Transportation']['budget'] = float(current_budget['transportation_budget'] or 0)
        categories['Entertainment']['budget'] = float(current_budget['entertainment_budget'] or 0)
        categories['Other']['budget'] = float(current_budget['other_budget'] or 0)
    
    # Set actual spending amounts
    for spending in week_spending:
        category = spending['category']
        if category in categories:
            categories[category]['spent'] = float(spending['spent'])
    
    return {
        'budget': {
            'total_budget': total_budget,
            'total_spent': total_spent,
            'remaining': total_budget - total_spent,
            'categories': categories,
            'current_budget': current_budget,
            'week_progress': (total_spent / total_budget * 100) if total_budget > 0 else 0
        },
        'monthly': {
            'income': float(monthly_income['total']) if monthly_income else 0.0,
            'expenses': float(monthly_expenses['total']) if monthly_expenses else 0.0,
            'net': (float(monthly_income['total']) if monthly_income else 0.0) - 
                   (float(monthly_expenses['total']) if monthly_expenses else 0.0)
        },
        'recent_transactions': recent_transactions,
        'week_dates': {
            'start': week_start.isoformat(),
            'end': week_end.isoformat()
        },
        'month_dates': {
            'start': month_start.isoformat(),
            'end': month_end.isoformat()
        }
    }

@bp.route('/')
@login_required
def index():
    """Budget management page with real financial data"""
    financial_summary = get_financial_summary(g.user['id'])
    
    # Get additional budget-specific data
    db = get_db()
    user_id = g.user['id']
    
    # Get budget history
    budget_history_rows = db.execute('''
        SELECT * FROM budgets 
        WHERE user_id = ? 
        ORDER BY week_start_date DESC
        LIMIT 10
    ''', (user_id,)).fetchall()
    
    budget_history = [dict(row) for row in budget_history_rows]
    
    # Get spending trends
    spending_trends_rows = db.execute('''
        SELECT 
            DATE(date) as day,
            COALESCE(SUM(amount), 0) as daily_total
        FROM transactions 
        WHERE user_id = ? 
        AND type = 'expense'
        AND date >= ?
        GROUP BY DATE(date)
        ORDER BY date DESC
        LIMIT 7
    ''', (user_id, financial_summary['week_dates']['start'])).fetchall()
    
    spending_trends = [dict(row) for row in spending_trends_rows]
    
    # Add budget-specific data to the summary
    financial_summary['budget_history'] = budget_history
    financial_summary['spending_trends'] = spending_trends
    
    return render_template('home/budget.html', **financial_summary)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new budget"""
    if request.method == 'POST':
        try:
            # Get form data
            total_amount = float(request.form['total_amount'])
            food_budget = float(request.form.get('food_budget', 0))
            transportation_budget = float(request.form.get('transportation_budget', 0))
            entertainment_budget = float(request.form.get('entertainment_budget', 0))
            other_budget = float(request.form.get('other_budget', 0))
            
            # Validate total matches categories
            category_total = food_budget + transportation_budget + entertainment_budget + other_budget
            if abs(category_total - total_amount) > 0.01:  # Allow for small rounding differences
                flash(f'Category budgets (${category_total:.2f}) must equal total budget (${total_amount:.2f})', 'error')
                return render_template('home/budget-create.html')
            
            # Get current week start date
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            
            db = get_db()
            
            # Check if budget already exists for this week
            existing_budget = db.execute('''
                SELECT id FROM budgets 
                WHERE user_id = ? AND week_start_date = ?
            ''', (g.user['id'], week_start.isoformat())).fetchone()
            
            if existing_budget:
                # Update existing budget
                db.execute('''
                    UPDATE budgets SET 
                        total_amount = ?, food_budget = ?, transportation_budget = ?,
                        entertainment_budget = ?, other_budget = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (total_amount, food_budget, transportation_budget, 
                     entertainment_budget, other_budget, existing_budget['id']))
                flash('Weekly budget updated successfully!', 'success')
            else:
                # Create new budget
                db.execute('''
                    INSERT INTO budgets (user_id, total_amount, food_budget, transportation_budget,
                                       entertainment_budget, other_budget, week_start_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (g.user['id'], total_amount, food_budget, transportation_budget,
                     entertainment_budget, other_budget, week_start.isoformat()))
                flash('Weekly budget created successfully!', 'success')
            
            db.commit()
            return redirect(url_for('budget.index'))
            
        except ValueError as e:
            flash('Please enter valid amounts for all budget fields', 'error')
        except Exception as e:
            flash(f'Error creating budget: {str(e)}', 'error')
    
    return render_template('home/budget-create.html')

@bp.route('/api/suggestions')
@login_required
def get_budget_suggestions():
    """Get smart budget suggestions based on spending history"""
    db = get_db()
    user_id = g.user['id']
    
    # Get average spending by category over last 4 weeks
    suggestions_rows = db.execute('''
        SELECT 
            category,
            AVG(weekly_total) as avg_amount
        FROM (
            SELECT 
                category,
                strftime('%Y-%W', date) as week,
                SUM(amount) as weekly_total
            FROM transactions 
            WHERE user_id = ? 
            AND type = 'expense'
            AND date >= date('now', '-28 days')
            GROUP BY category, week
        )
        GROUP BY category
    ''', (user_id,)).fetchall()
    
    suggestions = [dict(row) for row in suggestions_rows]
    
    # Calculate suggestions with 10% buffer
    result = {}
    total_suggested = 0
    
    for suggestion in suggestions:
        category = suggestion['category']
        suggested_amount = float(suggestion['avg_amount']) * 1.1  # 10% buffer
        result[category] = round(suggested_amount, 2)
        total_suggested += suggested_amount
    
    result['total'] = round(total_suggested, 2)
    
    return jsonify(result)

@bp.route('/<int:budget_id>/delete', methods=('POST',))
@login_required
def delete(budget_id):
    """Delete a budget"""
    db = get_db()
    
    # Verify budget belongs to current user
    budget = db.execute('''
        SELECT * FROM budgets WHERE id = ? AND user_id = ?
    ''', (budget_id, g.user['id'])).fetchone()
    
    if not budget:
        abort(404)
    
    db.execute('DELETE FROM budgets WHERE id = ?', (budget_id,))
    db.commit()
    
    flash('Budget deleted successfully!', 'success')
    return redirect(url_for('budget.index'))