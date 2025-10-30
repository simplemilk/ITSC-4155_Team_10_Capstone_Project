from decimal import Decimal
from datetime import datetime
from flask import Blueprint, g, render_template, redirect, jsonify, request, flash
from auth import login_required
from db import get_db

try:
    from db import get_db
except ImportError:
    def login_required(f):
        return f
    def get_db():
        return None
    
bp = Blueprint('finance', __name__)

def init_app(app):
    app.register_blueprint(bp)

def calculate_total_income(user_id, start_date=None, end_date=None):
    """Calculate total income for a user within a date range."""
    query = '''
        SELECT COALESCE(SUM(amount), 0) as total_income
        FROM v_active_income 
        WHERE user_id = ?
    '''
    params = [user_id]
    
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)

    result = get_db().execute(query, params).fetchone()
    return Decimal(str(result['total_income']))

def calculate_total_expenses(user_id, start_date=None, end_date=None):
    """Calculate total expenses for a user within a date range."""
    query = '''
        SELECT COALESCE(SUM(amount), 0) as total_expenses
        FROM expenses 
        WHERE user_id = ? AND is_active = 1
    '''
    params = [user_id]
    
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)

    result = get_db().execute(query, params).fetchone()
    return Decimal(str(result['total_expenses']))

def calculate_savings(user_id, start_date=None, end_date=None):
    """Calculate total savings (income - expenses) for a user."""
    total_income = calculate_total_income(user_id, start_date, end_date)
    total_expenses = calculate_total_expenses(user_id, start_date, end_date)
    return total_income - total_expenses

def calculate_budget_allocations(user_id):
    """Calculate budget allocations based on income and category settings."""
    db = get_db()
    
    # Get total monthly income
    current_month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    monthly_income = calculate_total_income(user_id, start_date=current_month_start)
    
    # Get budget categories with their allocation percentages
    categories = db.execute('''
        SELECT 
            bc.id,
            bc.name,
            bc.allocation_percentage,
            COALESCE(SUM(e.amount), 0) as spent_amount
        FROM budget_categories bc
        LEFT JOIN expenses e ON e.category_id = bc.id 
            AND e.user_id = bc.user_id 
            AND e.is_active = 1 
            AND strftime('%Y-%m', e.date) = strftime('%Y-%m', 'now')
        WHERE bc.user_id = ? AND bc.is_active = 1
        GROUP BY bc.id, bc.name, bc.allocation_percentage
    ''', (user_id,)).fetchall()
    
    allocations = []
    for category in categories:
        allocated_amount = (monthly_income * Decimal(str(category['allocation_percentage']))) / 100
        remaining_amount = allocated_amount - Decimal(str(category['spent_amount']))
        
        allocations.append({
            'category_id': category['id'],
            'category_name': category['name'],
            'allocation_percentage': float(category['allocation_percentage']),
            'allocated_amount': float(allocated_amount),
            'spent_amount': float(category['spent_amount']),
            'remaining_amount': float(remaining_amount)
        })
    
    return allocations

@bp.route('/finance')
@login_required
def index():
    """Show finance dashboard page"""
    try:
        db = get_db()
        if db is None:
            flash("Database connection not available.", "error")
        
        return render_template('home/finance-split.html')
    except Exception as e:
        flash(f'Error loading finance page: {e}', 'error')
        return render_template('home/financial-split.html')

@bp.route('/finance/dashboard')
@login_required
def dashboard():
    """Show finance dashboard page"""
    return render_template('home/dashboard.html')


@bp.route('/finance/summary', methods=['GET'])
@login_required
def get_financial_summary():
    """Get comprehensive financial summary including income, expenses, savings, and budget."""
    try:
        db = get_db()
        if db is None:
            return jsonify({'error': 'Database connection not available'}), 503
        
        # Get date range parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Calculate all financial metrics
        total_income = calculate_total_income(g.user['id'], start_date, end_date)
        total_expenses = calculate_total_expenses(g.user['id'], start_date, end_date)
        total_savings = calculate_savings(g.user['id'], start_date, end_date)
        budget_allocations = calculate_budget_allocations(g.user['id'])

        # Get income breakdown by category
        income_breakdown = get_db().execute('''
            SELECT 
                ic.name as category_name,
                COUNT(*) as entry_count,
                SUM(i.amount) as total_amount,
                AVG(i.amount) as average_amount
            FROM v_active_income i
            JOIN income_category ic ON i.category_id = ic.id
            WHERE i.user_id = ?
            GROUP BY ic.id, ic.name
            ORDER BY total_amount DESC
        ''', (g.user['id'],)).fetchall()

        # Calculate savings rate
        savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0

        return jsonify({
            'summary': {
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'total_savings': float(total_savings),
                'savings_rate': float(savings_rate)
            },
            'income_breakdown': [{
                'category': item['category_name'],
                'count': item['entry_count'],
                'total': float(item['total_amount']),
                'average': float(item['average_amount'])
            } for item in income_breakdown],
            'budget_allocations': budget_allocations,
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/budget/recalculate', methods=['POST'])
@login_required
def recalculate_budget():
    """Force a budget recalculation based on current income."""
    try:
        allocations = calculate_budget_allocations(g.user['id'])
        
        # Update the budget_allocations table with new calculated amounts
        db = get_db()
        for allocation in allocations:
            db.execute('''
                UPDATE budget_allocations 
                SET allocated_amount = ?,
                    updated_at = CURRENT_TIMESTAMP,
                    updated_by = ?
                WHERE category_id = ? AND user_id = ?
            ''', (
                allocation['allocated_amount'],
                g.user['id'],
                allocation['category_id'],
                g.user['id']
            ))
        db.commit()

        return jsonify({
            'message': 'Budget allocations updated successfully',
            'data': allocations
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/savings/projected', methods=['GET'])
@login_required
def get_projected_savings():
    """Calculate projected savings based on recurring income and expenses."""
    try:
        # Get recurring income
        recurring_income = get_db().execute('''
            SELECT 
                amount,
                recurrence_period
            FROM v_active_income
            WHERE user_id = ? AND is_recurring = 1
        ''', (g.user['id'],)).fetchall()

        # Get recurring expenses
        recurring_expenses = get_db().execute('''
            SELECT 
                amount,
                recurrence_period
            FROM expenses
            WHERE user_id = ? AND is_recurring = 1 AND is_active = 1
        ''', (g.user['id'],)).fetchall()

        # Calculate monthly projections
        monthly_recurring_income = sum(
            calculate_monthly_amount(item['amount'], item['recurrence_period'])
            for item in recurring_income
        )
        
        monthly_recurring_expenses = sum(
            calculate_monthly_amount(item['amount'], item['recurrence_period'])
            for item in recurring_expenses
        )

        projected_monthly_savings = monthly_recurring_income - monthly_recurring_expenses
        projected_annual_savings = projected_monthly_savings * 12

        return jsonify({
            'monthly': {
                'income': float(monthly_recurring_income),
                'expenses': float(monthly_recurring_expenses),
                'savings': float(projected_monthly_savings)
            },
            'annual': {
                'income': float(monthly_recurring_income * 12),
                'expenses': float(monthly_recurring_expenses * 12),
                'savings': float(projected_annual_savings)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_monthly_amount(amount, recurrence_period):
    """Convert an amount to its monthly equivalent based on recurrence period."""
    amount = Decimal(str(amount))
    multipliers = {
        'daily': Decimal('30.44'),  # Average days per month
        'weekly': Decimal('4.348'),  # Average weeks per month
        'biweekly': Decimal('2.174'),  # Biweekly to monthly
        'monthly': Decimal('1'),
        'quarterly': Decimal('0.333'),  # Quarterly to monthly
        'annually': Decimal('0.0833')  # Annual to monthly
    }
    return amount * multipliers.get(recurrence_period, Decimal('1'))