import os
from flask import Flask, render_template, redirect, url_for, g, flash, request
from datetime import datetime

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['DATABASE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'niner_finance.sqlite')

app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for simplicity in this example

# Initialize database
import db
db.init_app(app)

# Import and register auth blueprint
import auth
app.register_blueprint(auth.bp)

# Import and register your existing blueprints
import income
app.register_blueprint(income.bp)

import budget
app.register_blueprint(budget.bp)

import transactions
app.register_blueprint(transactions.bp)

# Import and register expenses API blueprint
try:
    import expenses_api
    app.register_blueprint(expenses_api.bp)
except ImportError as e:
    print(f"Expenses API module not found: {e}, skipping...")

# Import and register notification blueprint
try:
    import notification_routes
    app.register_blueprint(notification_routes.bp)
except ImportError as e:
    print(f"Notification module not found: {e}, skipping...")

# Try to import finance if it exists
try:
    import finance
    app.register_blueprint(finance.bp)
except ImportError:
    print("Finance module not found, skipping...")

# Import the priorities blueprint
from priorities import bp as priorities_bp
app.register_blueprint(priorities_bp)

# Optional blueprints: try to register additional modules if present
def try_register(module_name, attr='bp'):
    try:
        mod = __import__(module_name)
        bp = getattr(mod, attr, None)
        if bp is not None:
            app.register_blueprint(bp)
            return True
    except Exception:
        pass
    return False

# portfolio (may be a UI prototype)
if not try_register('portfolio'):
    try:
        import portfolio as _p
        app.register_blueprint(_p.bp)
    except Exception:
        print('Portfolio module not found: skipping...')

# subscriptions
if not try_register('subscriptions'):
    try:
        from subscriptions import bp as subscriptions_bp
        app.register_blueprint(subscriptions_bp)
    except Exception:
        print('Subscriptions module not found: skipping...')

# investments (support different import styles)
if not try_register('investments'):
    try:
        from investments import bp as investments_bp
        app.register_blueprint(investments_bp)
    except Exception:
        print('Investments module not found: skipping...')

# gamification
if not try_register('gamification'):
    try:
        import gamification as _g
        app.register_blueprint(_g.bp)
    except Exception:
        print('Gamification module not found: skipping...')

# Main Routes
@app.route('/')
def index():
    """Home page"""
    if g.user:
        return redirect(url_for('dashboard'))
    return render_template('home/index.html')

@app.route('/dashboard')
@auth.login_required
def dashboard():
    """Main dashboard page with real financial data"""
    # Use the get_financial_summary function from budget.py
    financial_summary = budget.get_financial_summary(g.user['id'])
    return render_template('home/dashboard.html', **financial_summary)

@app.route('/quick-expense')
@auth.login_required
def quick_expense():
    """Quick expense entry page"""
    return render_template('home/quick-expense.html')

@app.route('/profile')
@auth.login_required
def profile():
    """User profile page"""
    return redirect(url_for('auth.profile'))

# Financial Goals routes with traditional forms
@app.route('/goals')
@auth.login_required
def financial_goals():
    """Financial goals page with user data"""
    from db import get_db
    
    # Get user's financial goals if they exist in database
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
    except Exception as e:
        print(f"Database error in goals: {e}")
        user_goals = []
    
    # Get financial summary for the split view
    financial_summary = budget.get_financial_summary(g.user['id'])
    
    # Convert goals to list of dicts for easier template access
    goals_data = []
    for goal in user_goals:
        goals_data.append({
            'id': goal['id'],
            'goal_name': goal['goal_name'],
            'target_amount': float(goal['target_amount']),
            'current_amount': float(goal['current_amount']),
            'target_date': goal['target_date'],
            'category': goal['category'],
            'description': goal['description'],
            'is_completed': goal['is_completed'],
            'created_at': goal['created_at']
        })
    
    return render_template('home/finance-goals.html', 
                         goals=goals_data,
                         **financial_summary)

@app.route('/goals/create', methods=['GET', 'POST'])
@auth.login_required
def create_goal():
    """Create a new financial goal"""
    if request.method == 'POST':
        from db import get_db
        
        try:
            # Get form data
            goal_name = request.form['goal_name']
            target_amount = float(request.form['target_amount'])
            current_amount = float(request.form.get('current_amount', 0))
            target_date = request.form['target_date']
            category = request.form['category']
            description = request.form.get('description', '')
            
            # Validation
            if not goal_name or target_amount <= 0:
                flash('Please provide a valid goal name and target amount.', 'error')
                return redirect(url_for('create_goal'))
            
            # Insert into database
            db_conn = get_db()
            db_conn.execute('''
                INSERT INTO financial_goals 
                (user_id, goal_name, target_amount, current_amount, target_date, 
                 category, description, is_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                g.user['id'],
                goal_name,
                target_amount,
                current_amount,
                target_date,
                category,
                description,
                False
            ))
            db_conn.commit()
            
            # GAMIFICATION: Award points for creating goal
            try:
                from gamification import on_goal_created
                on_goal_created(g.user['id'])
            except Exception as e:
                print(f"Gamification error: {e}")
            
            flash(f'Goal "{goal_name}" created successfully!', 'success')
            return redirect(url_for('financial_goals'))
            
        except ValueError:
            flash('Please enter valid amounts for target and current values.', 'error')
        except Exception as e:
            flash(f'Error creating goal: {str(e)}', 'error')
    
    return render_template('home/create-goal.html')

@app.route('/goals/<int:goal_id>/edit', methods=['GET', 'POST'])
@auth.login_required
def edit_goal(goal_id):
    """Edit an existing financial goal"""
    from db import get_db
    
    db_conn = get_db()
    
    # Get the goal and verify ownership
    goal = db_conn.execute('''
        SELECT * FROM financial_goals 
        WHERE id = ? AND user_id = ?
    ''', (goal_id, g.user['id'])).fetchone()
    
    if not goal:
        flash('Goal not found.', 'error')
        return redirect(url_for('financial_goals'))
    
    if request.method == 'POST':
        try:
            # Get form data
            goal_name = request.form['goal_name']
            target_amount = float(request.form['target_amount'])
            current_amount = float(request.form.get('current_amount', 0))
            target_date = request.form['target_date']
            category = request.form['category']
            description = request.form.get('description', '')
            is_completed = bool(request.form.get('is_completed', False))
            
            # Validation
            if not goal_name or target_amount <= 0:
                flash('Please provide a valid goal name and target amount.', 'error')
                return redirect(url_for('edit_goal', goal_id=goal_id))
            
            # Update in database
            db_conn.execute('''
                UPDATE financial_goals SET
                    goal_name = ?, target_amount = ?, current_amount = ?,
                    target_date = ?, category = ?, description = ?,
                    is_completed = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            ''', (
                goal_name, target_amount, current_amount,
                target_date, category, description, is_completed,
                goal_id, g.user['id']
            ))
            db_conn.commit()
            
            flash(f'Goal "{goal_name}" updated successfully!', 'success')
            return redirect(url_for('financial_goals'))
            
        except ValueError:
            flash('Please enter valid amounts for target and current values.', 'error')
        except Exception as e:
            flash(f'Error updating goal: {str(e)}', 'error')
    
    return render_template('home/edit-goal.html', goal=goal)

@app.route('/goals/<int:goal_id>/contribute', methods=['POST'])
@auth.login_required
def add_contribution(goal_id):
    """Add contribution to a goal"""
    from db import get_db
    
    try:
        contribution = float(request.form['contribution'])
        
        if contribution <= 0:
            flash('Contribution amount must be positive.', 'error')
            return redirect(url_for('financial_goals'))
        
        db_conn = get_db()
        
        # Get current goal
        goal = db_conn.execute('''
            SELECT * FROM financial_goals 
            WHERE id = ? AND user_id = ?
        ''', (goal_id, g.user['id'])).fetchone()
        
        if not goal:
            flash('Goal not found.', 'error')
            return redirect(url_for('financial_goals'))
        
        # Update current amount
        new_amount = float(goal['current_amount']) + contribution
        old_amount = float(goal['current_amount'])
        target_amount = float(goal['target_amount'])
        
        db_conn.execute('''
            UPDATE financial_goals SET
                current_amount = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        ''', (new_amount, goal_id, g.user['id']))
        db_conn.commit()
        
        # Check if goal just completed
        if new_amount >= target_amount and old_amount < target_amount:
            try:
                from gamification import on_goal_completed
                on_goal_completed(g.user['id'])
            except Exception as e:
                print(f"Gamification error: {e}")
        
        flash(f'Added ${contribution:.2f} to "{goal["goal_name"]}"!', 'success')
        
    except ValueError:
        flash('Please enter a valid contribution amount.', 'error')
    except Exception as e:
        flash(f'Error adding contribution: {str(e)}', 'error')
    
    return redirect(url_for('financial_goals'))

@app.route('/goals/<int:goal_id>/delete', methods=['POST'])
@auth.login_required
def delete_goal(goal_id):
    """Delete a financial goal"""
    from db import get_db
    
    try:
        db_conn = get_db()
        
        # Get goal name for flash message
        goal = db_conn.execute('''
            SELECT goal_name FROM financial_goals 
            WHERE id = ? AND user_id = ?
        ''', (goal_id, g.user['id'])).fetchone()
        
        if not goal:
            flash('Goal not found.', 'error')
            return redirect(url_for('financial_goals'))
        
        # Delete the goal
        db_conn.execute('''
            DELETE FROM financial_goals 
            WHERE id = ? AND user_id = ?
        ''', (goal_id, g.user['id']))
        db_conn.commit()
        
        flash(f'Goal "{goal["goal_name"]}" deleted successfully.', 'success')
        
    except Exception as e:
        flash(f'Error deleting goal: {str(e)}', 'error')
    
    return redirect(url_for('financial_goals'))

@app.route('/goals/<int:goal_id>/toggle', methods=['POST'])
@auth.login_required
def toggle_goal_completion(goal_id):
    """Toggle goal completion status"""
    from db import get_db
    
    try:
        db_conn = get_db()
        
        # Get current status
        goal = db_conn.execute('''
            SELECT goal_name, is_completed FROM financial_goals 
            WHERE id = ? AND user_id = ?
        ''', (goal_id, g.user['id'])).fetchone()
        
        if not goal:
            flash('Goal not found.', 'error')
            return redirect(url_for('financial_goals'))
        
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
    
    return redirect(url_for('financial_goals'))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    flash('Page not found', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    flash('Internal server error', 'error')
    return redirect(url_for('index'))

# Context processor
@app.context_processor
def inject_user():
    """Make user and datetime available in all templates"""
    return dict(user=g.user, now=datetime.now)

@app.template_filter('date_diff')
def date_diff_filter(date_str):
    """Calculate days until date"""
    try:
        target_date = datetime.fromisoformat(date_str)
        today = datetime.now()
        delta = (target_date - today).days
        return delta
    except:
        return 0

if __name__ == '__main__':
    with app.app_context():
        try:
            print("\n🔧 Initializing Niner Finance Database...")
            print("=" * 50)
            
            # Initialize main database
            db.init_db()
            print("✓ Main database initialized")
            
            # Create demo user
            auth.create_demo_user()
            print("✓ Demo user created/verified")
            
            # Initialize subscriptions database
            print("\n🔄 Initializing subscriptions module...")
            try:
                from init_subscriptions_db import init_subscriptions_db
                success = init_subscriptions_db()
                if not success:
                    print("⚠️  WARNING: Subscriptions tables may not have been created properly")
            except Exception as sub_error:
                print(f"❌ Subscriptions initialization error: {sub_error}")
            
            # Initialize investments database
            print("\n💼 Initializing investments module...")
            try:
                from init_investments_db import init_investments_db
                success = init_investments_db()
                if not success:
                    print("⚠️  WARNING: Investments tables may not have been created properly")
            except Exception as inv_error:
                print(f"❌ Investments initialization error: {inv_error}")
            
            # Initialize gamification database
            print("\n🎮 Initializing gamification module...")
            try:
                from init_gamification_db import init_gamification_db
                success = init_gamification_db()
                if not success:
                    print("⚠️  WARNING: Gamification tables may not have been created properly")
                    print("   Try running: python init_gamification_db.py")
            except Exception as game_error:
                print(f"❌ Gamification initialization error: {game_error}")
                print("   To fix: python init_gamification_db.py")
                import traceback
                traceback.print_exc()
            
            # Initialize notifications database
            print("\n🔔 Initializing notifications module...")
            try:
                from init_notifications_db import init_notifications_db
                success = init_notifications_db()
                if not success:
                    print("⚠️  WARNING: Notifications tables may not have been created properly")
                    print("   Try running: python init_notifications_db.py")
            except Exception as notif_error:
                print(f"❌ Notifications initialization error: {notif_error}")
                print("   To fix: python init_notifications_db.py")
                import traceback
                traceback.print_exc()
            
            print("\n" + "=" * 50)
            print("✓ App initialization complete")
            
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR during initialization: {e}")
            import traceback
            traceback.print_exc()
            print("\n⚠️  App may not function correctly!")
    
    print("\n" + "=" * 60)
    print("🚀 Niner Finance - Full Featured!")
    print("=" * 60)
    print("📍 Server running at: http://localhost:5001")
    print("\n📋 Available Features:")
    print("  • Dashboard:         http://localhost:5001/dashboard")
    print("  • Income Management: http://localhost:5001/income")
    print("  • Budget Planning:   http://localhost:5001/budget")
    print("  • Transactions:      http://localhost:5001/transactions")
    print("  • Financial Goals:   http://localhost:5001/goals")
    print("  • Subscriptions:     http://localhost:5001/subscriptions")
    print("  • Investments:       http://localhost:5001/investments")
    print("  • Notifications:     http://localhost:5001/notifications")
    print("  • Game Dashboard:    http://localhost:5001/game")
    print("  • Login/Register:    http://localhost:5001/auth/login")
    print("\n👤 Demo Account Credentials:")
    print("  Username: demo")
    print("  Password: demo123")
    print("\n" + "=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5001)