import os
import sys
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from datetime import datetime

print("🔄 Starting Niner Finance App initialization...")

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
bcrypt = Bcrypt()

print("✅ Flask extensions initialized")

def create_app():
    """Application factory pattern"""
    print("🏗️  Creating Flask app...")
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///niner_finance.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    
    print(f"📊 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    bcrypt.init_app(app)
    
    print("🔗 Extensions connected to app")
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            import models
            if hasattr(models, 'User') and models.User:
                return models.User.query.get(int(user_id))
        except Exception as e:
            print(f"Error in load_user: {e}")
        return None
    
    print("🔐 Login manager configured")
    
    # Register blueprints with better error handling
    print("📋 Registering blueprints...")
    
    try:
        from auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        print("✅ Auth blueprint registered successfully.")
    except ImportError as e:
        print(f"⚠️  Auth blueprint not available: {e}")
    
    try:
        from transactions import bp as transactions_bp
        app.register_blueprint(transactions_bp)
        print("✅ Transactions blueprint registered successfully.")
    except ImportError as e:
        print(f"⚠️  Transactions blueprint not available: {e}")
    
    try:
        from budget import bp as budget_bp
        app.register_blueprint(budget_bp)
        print("✅ Budget blueprint registered successfully.")
    except ImportError as e:
        print(f"⚠️  Budget blueprint not available: {e}")
    
    try:
        from finance import bp as finance_bp
        app.register_blueprint(finance_bp)
        print("✅ Finance blueprint registered successfully.")
    except ImportError as e:
        print(f"⚠️  Finance blueprint not available: {e}")
    
    try:
        from income import bp as income_bp
        app.register_blueprint(income_bp)
        print("✅ Income blueprint registered successfully.")
    except ImportError as e:
        print(f"⚠️  Income blueprint not available: {e}")
    
    # Main navigation routes with templates
    @app.route('/')
    def index():
        return '<h1>🏦 Niner Finance</h1><p>Welcome to Niner Finance!</p><ul><li><a href="/test">Test Page</a></li><li><a href="/transactions">Transactions</a></li><li><a href="/income">Income</a></li><li><a href="/budget">Budget</a></li><li><a href="/finance">Finance</a></li></ul>'
    
    @app.route('/dashboard')
    def dashboard():
        stats = {
            'total_income': 0.00,
            'total_expenses': 0.00,
            'net_balance': 0.00,
            'monthly_budget': 0.00
        }
        return f'<h1>📊 Dashboard</h1><p>Stats: {stats}</p>'
    
    @app.route('/test')
    def test():
        system_info = {
            'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'flask_status': 'Running',
            'database_status': 'SQLAlchemy configured',
            'routes_status': 'All functional'
        }
        return f'<h1>🧪 Test Page</h1><pre>{system_info}</pre><p><a href="/">Back to Home</a></p>'
    
    print("🛣️  Main routes configured")
    
    # Create database tables WITHIN app context
    print("🗄️  Setting up database...")
    with app.app_context():
        try:
            # Initialize models with db instance
            print("🔧 Initializing models...")
            
            # Import models and initialize
            import models
            
            # Check if init_models function exists
            if hasattr(models, 'init_models'):
                model_classes = models.init_models(db)
                print(f"✅ Models initialized successfully!")
                
                # Test models
                if models.test_models():
                    print("✅ All models are ready!")
                else:
                    print("⚠️  Some models may have issues")
                
            else:
                print("❌ init_models function not found in models.py")
                model_classes = {}
            
            # Create all tables
            print("🏗️  Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Create default categories
            if hasattr(models, 'create_default_categories'):
                print("📁 Creating default categories...")
                models.create_default_categories()
            
            # Create admin user if User model exists
            if model_classes and 'User' in model_classes:
                print("👤 Checking for admin user...")
                try:
                    User = model_classes['User']
                    admin_user = User.query.filter_by(email='admin@ninerfinance.com').first()
                    if not admin_user:
                        admin_user = User(
                            username='admin',
                            email='admin@ninerfinance.com',
                            password='admin123'
                        )
                        db.session.add(admin_user)
                        db.session.commit()
                        print("✅ Default admin user created!")
                        print("   📧 Email: admin@ninerfinance.com")
                        print("   🔑 Password: admin123")
                    else:
                        print("ℹ️  Admin user already exists.")
                except Exception as e:
                    print(f"❌ Error with admin user: {e}")
            else:
                print("⚠️  User model not available, skipping admin user creation")
                
        except Exception as e:
            print(f"❌ Database setup error: {e}")
            import traceback
            traceback.print_exc()
    
    print("🎯 App creation completed!")
    return app

# Create the app instance
print("🚀 Creating app instance...")
app = create_app()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔥 STARTING NINER FINANCE APPLICATION")
    print("="*60)
    
    # Run the application
    debug_mode = True
    port = 5001
    
    print(f"\n🌟 Configuration:")
    print(f"   🐛 Debug mode: {debug_mode}")
    print(f"   🔌 Port: {port}")
    print(f"   🏠 Host: 0.0.0.0")
    
    print(f"\n🚀 Starting server...")
    print(f"📱 Open your browser to: http://localhost:{port}")
    print(f"🔍 Test page: http://localhost:{port}/test")
    print("\n" + "="*60)
    
    # Force flush output
    sys.stdout.flush()
    
    try:
        app.run(debug=debug_mode, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()