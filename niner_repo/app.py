import os
from flask import Flask, render_template, redirect, url_for, g, flash, request
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix

# Create Flask app
app = Flask(__name__)

# Use instance folder for database
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['DATABASE'] = os.path.join(instance_path, 'niner_finance.sqlite')
app.config['WTF_CSRF_ENABLED'] = False

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

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
    """users profile page"""
    return redirect(url_for('auth.profile'))

# Financial Goals routes - REDIRECT TO FINANCE BLUEPRINT
@app.route('/goals')
@auth.login_required
def financial_goals():
    """Redirect to finance blueprint goals page"""
    return redirect(url_for('finance.goals'))

@app.route('/goals/create', methods=['GET', 'POST'])
@auth.login_required
def create_goal():
    """Redirect to finance blueprint create goal"""
    if request.method == 'POST':
        # Forward the form data
        return redirect(url_for('finance.create_goal'), code=307)
    return redirect(url_for('finance.create_goal'))

@app.route('/goals/<int:goal_id>/edit', methods=['GET', 'POST'])
@auth.login_required
def edit_goal(goal_id):
    """Redirect to finance blueprint edit goal"""
    if request.method == 'POST':
        return redirect(url_for('finance.edit_goal', goal_id=goal_id), code=307)
    return redirect(url_for('finance.edit_goal', goal_id=goal_id))

@app.route('/goals/<int:goal_id>/contribute', methods=['POST'])
@auth.login_required
def add_contribution(goal_id):
    """Redirect to finance blueprint contribution"""
    return redirect(url_for('finance.add_contribution', goal_id=goal_id), code=307)

@app.route('/goals/<int:goal_id>/delete', methods=['POST'])
@auth.login_required
def delete_goal(goal_id):
    """Redirect to finance blueprint delete goal"""
    return redirect(url_for('finance.delete_goal', goal_id=goal_id), code=307)

@app.route('/goals/<int:goal_id>/toggle', methods=['POST'])
@auth.login_required
def toggle_goal_completion(goal_id):
    """Redirect to finance blueprint toggle completion"""
    return redirect(url_for('finance.toggle_goal_completion', goal_id=goal_id), code=307)

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
    return dict(user=g.user, now=datetime.now)  # Changed from g.user to g.user

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
            
            # Create demo users
            auth.create_demo_user()
            print("✓ Demo users created/verified")
            
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
    
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)