from decimal import Decimal
from datetime import datetime
from flask import Blueprint, g, render_template, redirect, jsonify, request, flash, url_for
from auth import login_required
from db import get_db
from priorities import get_personalized_suggestions, get_user_financial_stats
from gamification import on_goal_created, on_goal_completed
import budget

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
        
        return render_template('home/financial-split.html')
    except Exception as e:
        flash(f'Error loading finance page: {e}', 'error')
        return render_template('home/dashboard.html')

@bp.route('/finance/dashboard')
@login_required
def dashboard():
    """Show finance dashboard page"""
    db = get_db()
    
    # Get user's top priority
    top_priority = db.execute(
        '''SELECT priority_type FROM user_priorities 
           WHERE user_id = ? 
           ORDER BY importance_level DESC LIMIT 1''',
        (g.user['id'],)
    ).fetchone()
    
    priority_insights = None
    if top_priority:
        priority_insights = {
            'type': top_priority['priority_type'],
            'suggestions': get_personalized_suggestions(top_priority['priority_type'], g.user['id'])[:3]
        }
    
    return render_template('home/dashboard.html',
        priority_insights=priority_insights
    )

# FINANCIAL GOALS ROUTES - These match app.py routes
@bp.route('/goals')
@login_required
def goals():
    """Financial goals page with user's data"""
    db_conn = get_db()
    try:
        # Check if financial_goals table exists
        table_check = db_conn.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='financial_goals'
        ''').fetchone()
        
        user_goals = []
        if table_check:
            # Get user's goals from database
            user_goals = db_conn.execute('''
                SELECT * FROM financial_goals 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (g.user['id'],)).fetchall()
        else:
            # Create the table if it doesn't exist
            db_conn.execute('''
                CREATE TABLE IF NOT EXISTS financial_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    goal_name TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    current_amount REAL DEFAULT 0,
                    target_date TEXT,
                    category TEXT,
                    description TEXT,
                    priority TEXT DEFAULT 'medium',
                    is_completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            db_conn.commit()
    except Exception as e:
        print(f"Database error in goals: {e}")
        user_goals = []
    
    # Get financial summary for the split view
    financial_summary = budget.get_financial_summary(g.user['id'])
    
    # Convert goals to list of dicts for easier template access
    goals_data = []
    for goal in user_goals:
        # Parse target_date from string to datetime object
        target_date = None
        if goal['target_date']:
            try:
                target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
            except (ValueError, TypeError):
                try:
                    # Try ISO format
                    target_date = datetime.fromisoformat(goal['target_date'])
                except:
                    target_date = None
        
        # Parse created_at from string to datetime object
        created_at = None
        if goal['created_at']:
            try:
                created_at = datetime.strptime(goal['created_at'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                try:
                    # Try ISO format
                    created_at = datetime.fromisoformat(goal['created_at'])
                except:
                    created_at = datetime.now()
        
        goals_data.append({
            'id': goal['id'],
            'goal_name': goal['goal_name'],
            'target_amount': float(goal['target_amount']),
            'current_amount': float(goal['current_amount']),
            'target_date': target_date,  # Now a datetime object
            'target_date_str': goal['target_date'] if goal['target_date'] else '',  # Keep string for form
            'category': goal['category'] if goal['category'] else 'other',
            'description': goal['description'] if goal['description'] else '',
            'priority': goal['priority'] if goal['priority'] else 'medium',
            'is_completed': bool(goal['is_completed']),
            'created_at': created_at  # Now a datetime object
        })
    
    return render_template('home/finance-goals.html', 
                         goals=goals_data,
                         **financial_summary)

@bp.route('/goals/create', methods=['GET', 'POST'])
@login_required
def create_goal():
    """Create a new financial goal - uses edit-goal.html as template"""
    if request.method == 'POST':
        try:
            # Get form data
            goal_name = request.form['goal_name']
            target_amount = float(request.form['target_amount'])
            current_amount = float(request.form.get('current_amount', 0))
            target_date = request.form.get('target_date', '')
            category = request.form.get('category', 'other')
            description = request.form.get('description', '')
            priority = request.form.get('priority', 'medium')
            
            # Validation
            if not goal_name or target_amount <= 0:
                flash('Please provide a valid goal name and target amount.', 'error')
                return redirect(url_for('finance.create_goal'))
            
            # Insert into database
            db_conn = get_db()
            db_conn.execute('''
                INSERT INTO financial_goals 
                (user_id, goal_name, target_amount, current_amount, target_date, 
                 category, description, priority, is_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                g.user['id'],
                goal_name,
                target_amount,
                current_amount,
                target_date,
                category,
                description,
                priority,
                False
            ))
            db_conn.commit()
            
            # GAMIFICATION: Award points for creating goal
            try:
                on_goal_created(g.user['id'])
            except Exception as e:
                print(f"Gamification error: {e}")
            
            flash(f'Goal "{goal_name}" created successfully!', 'success')
            return redirect(url_for('finance.goals'))
            
        except ValueError:
            flash('Please enter valid amounts for target and current values.', 'error')
        except Exception as e:
            flash(f'Error creating goal: {str(e)}', 'error')
    
    # Use edit-goal.html template with empty goal for create mode
    empty_goal = {
        'id': None,
        'goal_name': '',
        'target_amount': 0,
        'current_amount': 0,
        'target_date': '',
        'category': 'other',
        'description': '',
        'priority': 'medium',
        'is_completed': False
    }
    return render_template('home/edit-goal.html', goal=empty_goal, create_mode=True)

@bp.route('/goals/<int:goal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    """Edit an existing financial goal"""
    db_conn = get_db()
    
    # Get the goal and verify ownership
    goal = db_conn.execute('''
        SELECT * FROM financial_goals 
        WHERE id = ? AND user_id = ?
    ''', (goal_id, g.user['id'])).fetchone()
    
    if not goal:
        flash('Goal not found.', 'error')
        return redirect(url_for('finance.goals'))
    
    if request.method == 'POST':
        try:
            # Get form data
            goal_name = request.form['goal_name']
            target_amount = float(request.form['target_amount'])
            current_amount = float(request.form.get('current_amount', 0))
            target_date = request.form.get('target_date', '')
            category = request.form.get('category', 'other')
            description = request.form.get('description', '')
            priority = request.form.get('priority', 'medium')
            is_completed = bool(request.form.get('is_completed', False))
            
            # Validation
            if not goal_name or target_amount <= 0:
                flash('Please provide a valid goal name and target amount.', 'error')
                return redirect(url_for('finance.edit_goal', goal_id=goal_id))
            
            # Update in database
            db_conn.execute('''
                UPDATE financial_goals SET
                    goal_name = ?, target_amount = ?, current_amount = ?,
                    target_date = ?, category = ?, description = ?,
                    priority = ?, is_completed = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            ''', (
                goal_name, target_amount, current_amount,
                target_date, category, description, priority, is_completed,
                goal_id, g.user['id']
            ))
            db_conn.commit()
            
            flash(f'Goal "{goal_name}" updated successfully!', 'success')
            return redirect(url_for('finance.goals'))
            
        except ValueError:
            flash('Please enter valid amounts for target and current values.', 'error')
        except Exception as e:
            flash(f'Error updating goal: {str(e)}', 'error')
    
    return render_template('home/edit-goal.html', goal=goal, create_mode=False)

@bp.route('/goals/<int:goal_id>/contribute', methods=['POST'])
@login_required
def add_contribution(goal_id):
    """Add contribution to a goal"""
    try:
        contribution = float(request.form['contribution'])
        
        if contribution <= 0:
            flash('Contribution amount must be positive.', 'error')
            return redirect(url_for('finance.goals'))
        
        db_conn = get_db()
        
        # Get current goal
        goal = db_conn.execute('''
            SELECT * FROM financial_goals 
            WHERE id = ? AND user_id = ?
        ''', (goal_id, g.user['id'])).fetchone()
        
        if not goal:
            flash('Goal not found.', 'error')
            return redirect(url_for('finance.goals'))
        
        # Update current amount
        new_amount = float(goal['current_amount']) + contribution
        old_amount = float(goal['current_amount'])
        target_amount = float(goal['target_amount']);
        
        db_conn.execute('''
            UPDATE financial_goals SET
                current_amount = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        ''', (new_amount, goal_id, g.user['id']))
        db_conn.commit()
        
        # Check if goal just completed
        if new_amount >= target_amount and old_amount < target_amount:
            try:
                on_goal_completed(g.user['id'])
            except Exception as e:
                print(f"Gamification error: {e}")
        
        flash(f'Added ${contribution:.2f} to "{goal["goal_name"]}"!', 'success')
        
    except ValueError:
        flash('Please enter a valid contribution amount.', 'error')
    except Exception as e:
        flash(f'Error adding contribution: {str(e)}', 'error')
    
    return redirect(url_for('finance.goals'))

@bp.route('/goals/<int:goal_id>/delete', methods=['POST'])
@login_required
def delete_goal(goal_id):
    """Delete a financial goal"""
    try:
        db_conn = get_db()
        
        # Get goal name for flash message
        goal = db_conn.execute('''
            SELECT goal_name FROM financial_goals 
            WHERE id = ? AND user_id = ?
        ''', (goal_id, g.user['id'])).fetchone()
        
        if not goal:
            flash('Goal not found.', 'error')
            return redirect(url_for('finance.goals'))
        
        # Delete the goal
        db_conn.execute('''
            DELETE FROM financial_goals 
            WHERE id = ? AND user_id = ?
        ''', (goal_id, g.user['id']))
        db_conn.commit()
        
        flash(f'Goal "{goal["goal_name"]}" deleted successfully.', 'success')
        
    except Exception as e:
        flash(f'Error deleting goal: {str(e)}', 'error')
    
    return redirect(url_for('finance.goals'))

@bp.route('/goals/<int:goal_id>/toggle', methods=['POST'])
@login_required
def toggle_goal_completion(goal_id):
    """Toggle goal completion status"""
    try:
        db_conn = get_db()
        
        # Get current status
        goal = db_conn.execute('''
            SELECT goal_name, is_completed FROM financial_goals 
            WHERE id = ? AND user_id = ?
        ''', (goal_id, g.user['id'])).fetchone()
        
        if not goal:
            flash('Goal not found.', 'error')
            return redirect(url_for('finance.goals'))
        
        # Toggle completion status
        new_status = not bool(goal['is_completed'])
        
        db_conn.execute('''
            UPDATE financial_goals SET
                is_completed = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        ''', (new_status, goal_id, g.user['id']))
        db_conn.commit()
        
        status_text = 'completed' if new_status else 'reopened'
        flash(f'Goal "{goal["goal_name"]}" marked as {status_text}!', 'success')
        
    except Exception as e:
        flash(f'Error updating goal status: {str(e)}', 'error')
    
    return redirect(url_for('finance.goals'))

# API ROUTES
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
        'daily': Decimal('30.44'),
        'weekly': Decimal('4.348'),
        'biweekly': Decimal('2.174'),
        'monthly': Decimal('1'),
        'quarterly': Decimal('0.333'),
        'annually': Decimal('0.0833')
    }
    return amount * multipliers.get(recurrence_period, Decimal('1'))