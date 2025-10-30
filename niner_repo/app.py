import os
import sys
from flask import Flask, render_template, redirect, url_for, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from transactions import login_required

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
bcrypt = Bcrypt()

def create_app():
    """Application factory pattern"""
    print("🏗️  Creating Flask app...")
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for simplicity; enable in production!

    # Database configuration
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "niner_finance.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DATABASE'] = os.path.join(instance_path, 'niner_finance.db')
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    bcrypt.init_app(app)
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        import sqlite3
        from flask_login import UserMixin
        
        try:
            db_path = app.config['DATABASE']
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                user_data = conn.execute(
                    'SELECT * FROM user WHERE id = ?', (user_id,)
                ).fetchone()
                
                if user_data:
                    # Create a simple user object that implements UserMixin
                    class User(UserMixin):
                        def __init__(self, user_data):
                            self.id = str(user_data['id'])
                            self.username = user_data['username']
                            self.email = user_data['email']
                            self.password = user_data['password']
                        
                        def get_id(self):
                            return self.id
                    
                    return User(user_data)
                return None
        except Exception as e:
            print(f"Error loading user: {e}")
            return None
    
    print("🔗 Extensions connected to app")
    
    # Initialize database
    import db as database_module
    database_module.init_app(app)
    
    with app.app_context():
        try:
            # Create basic tables directly
            import sqlite3
            db_path = app.config['DATABASE']
            
            with sqlite3.connect(db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS user (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        transaction_type TEXT NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        description TEXT NOT NULL,
                        date DATE NOT NULL DEFAULT CURRENT_DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user (id)
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS income (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        category_id INTEGER,
                        amount DECIMAL(10,2) NOT NULL,
                        source TEXT NOT NULL,
                        description TEXT,
                        date DATE NOT NULL DEFAULT CURRENT_DATE,
                        is_recurring BOOLEAN DEFAULT 0,
                        recurrence_period TEXT,
                        next_recurrence_date DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by INTEGER,
                        FOREIGN KEY (user_id) REFERENCES user (id)
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        description TEXT NOT NULL,
                        date DATE NOT NULL DEFAULT CURRENT_DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by INTEGER,
                        FOREIGN KEY (user_id) REFERENCES user (id)
                    )
                ''')
                
                conn.commit()
            
            print("✅ Database initialized successfully")
            
            # Create demo user
            database_module.create_demo_user()
            
        except Exception as e:
            print(f"⚠️  Database setup error: {e}")
    
    # Import and register blueprints
    try:
        import auth
        app.register_blueprint(auth.bp)
        print("✅ Auth blueprint registered")
    except Exception as e:
        print(f"⚠️  Error registering auth blueprint: {e}")
    
    try:
        import transactions
        app.register_blueprint(transactions.bp)
        print("✅ Transactions blueprint registered")
    except Exception as e:
        print(f"⚠️  Error registering transactions blueprint: {e}")
    
    try:
        import income
        app.register_blueprint(income.bp)
        print("✅ Income blueprint registered")
    except Exception as e:
        print(f"⚠️  Error registering income blueprint: {e}")
    
    try:
        import budget
        app.register_blueprint(budget.bp)
        print("✅ Budget blueprint registered")
    except Exception as e:
        print(f"⚠️  Error registering budget blueprint: {e}")
    
    try:
        import finance
        app.register_blueprint(finance.bp)
        print("✅ Finance blueprint registered")
    except Exception as e:
        print(f"⚠️  Error registering finance blueprint: {e}")
    
    # Routes
    @app.route('/')
    def index():
        """Main landing page"""
        return render_template('home/index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard page - requires login"""
        from auth import login_required
        
        @login_required
        def dashboard_view():
            return render_template('home/dashboard.html')
        
        return dashboard_view()
    
    @app.route('/finance-goals')
    @login_required
    def finance_goals():
        """Render the financial goals page"""
        return render_template('home/finance-goals.html')

    print("🎯 App creation completed!")
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Try to run on different ports if 5001 is busy
    ports_to_try = [5001, 5002, 8000, 3000]
    
    for port in ports_to_try:
        try:
            print(f"🚀 Starting server on port {port}")
            app.run(debug=True, port=port)
            break
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"❌ Port {port} is busy, trying next port...")
                continue
            else:
                raise e
    else:
        print("❌ Could not find an available port to run the server")