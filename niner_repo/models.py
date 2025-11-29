from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Global variables that will be set by init_models
db = None
User = None
Income = None
Transaction = None
Budget = None
BudgetCategory = None
FinancialGoal = None
Category = None

def init_models(database):
    """Initialize all models with the database instance"""
    global db, User, Income, Transaction, Budget, BudgetCategory, FinancialGoal, Category
    
    print("🔧 Initializing models with database...")
    db = database
    
    # Define User model
    class User(UserMixin, db.Model):
        __tablename__ = 'users'
        __table_args__ = {'extend_existing': True}
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password = db.Column(db.String(128), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        is_active = db.Column(db.Boolean, default=True)
        
        def __init__(self, username, email, password):
            self.username = username
            self.email = email
            self.set_password(password)
        
        def set_password(self, password):
            """Set password hash"""
            self.password = generate_password_hash(password)
        
        def check_password(self, password):
            """Check password hash"""
            return check_password_hash(self.password, password)
        
        def __repr__(self):
            return f'<User {self.username}>'

    # Define Income model
    class Income(db.Model):
        __tablename__ = 'income'
        __table_args__ = {'extend_existing': True}

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        source = db.Column(db.String(100), nullable=False)
        amount = db.Column(db.Float, nullable=False)
        description = db.Column(db.Text)
        date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
        is_recurring = db.Column(db.Boolean, default=False)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<Income {self.source}: ${self.amount}>'

    # Define Transaction model
    class Transaction(db.Model):
        __tablename__ = 'transactions'
        __table_args__ = {'extend_existing': True}
             
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        description = db.Column(db.String(200), nullable=False)
        amount = db.Column(db.Float, nullable=False)
        category = db.Column(db.String(50), nullable=False)
        type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
        date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<Transaction {self.description}: ${self.amount}>'

    # Define Budget model
    class Budget(db.Model):
        __tablename__ = 'budgets'
        __table_args__ = {'extend_existing': True}
             
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        name = db.Column(db.String(100), nullable=False)
        total_amount = db.Column(db.Float, nullable=False)
        period = db.Column(db.String(20), nullable=False)  # weekly, monthly, yearly
        start_date = db.Column(db.Date, nullable=False)
        description = db.Column(db.Text)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<Budget {self.name}: ${self.total_amount}>'

    # Define BudgetCategory model
    class BudgetCategory(db.Model):
        __tablename__ = 'budget_categories'
        __table_args__ = {'extend_existing': True}
             
        id = db.Column(db.Integer, primary_key=True)
        budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
        category_name = db.Column(db.String(50), nullable=False)
        allocated_amount = db.Column(db.Float, nullable=False)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<BudgetCategory {self.category_name}: ${self.allocated_amount}>'

    # Define FinancialGoal model  
    class FinancialGoal(db.Model):
        __tablename__ = 'financial_goals'
        __table_args__ = {'extend_existing': True}
             
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        name = db.Column(db.String(100), nullable=False)
        target_amount = db.Column(db.Float, nullable=False)
        current_amount = db.Column(db.Float, default=0.0)
        target_date = db.Column(db.Date)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<FinancialGoal {self.name}: ${self.current_amount}/${self.target_amount}>'

    # Define Category model
    class Category(db.Model):
        __tablename__ = 'categories'
        __table_args__ = {'extend_existing': True}
             
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), unique=True, nullable=False)
        type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
        description = db.Column(db.Text)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def __repr__(self):
            return f'<Category {self.name} ({self.type})>'
    
    # Set global variables
    globals()['User'] = User
    globals()['Income'] = Income 
    globals()['Transaction'] = Transaction
    globals()['Budget'] = Budget
    globals()['BudgetCategory'] = BudgetCategory
    globals()['FinancialGoal'] = FinancialGoal
    globals()['Category'] = Category
    
    print(f"✅ Models defined: User, Income, Transaction, Budget, BudgetCategory, FinancialGoal, Category")
    
    return {
        'User': User,
        'Income': Income,
        'Transaction': Transaction,
        'Budget': Budget,
        'BudgetCategory': BudgetCategory,
        'FinancialGoal': FinancialGoal,
        'Category': Category
    }

def create_default_categories():
    """Create default income and expense categories (only if they don't exist)"""
    try:
        if not Category:
            print("❌ Category model not available")
            return
            
        # Check how many categories already exist
        existing_count = Category.query.count()
        print(f"📊 Found {existing_count} existing categories")
        
        if existing_count > 0:
            print("ℹ️  Categories already exist, skipping creation")
            
            # Show existing categories
            existing_categories = Category.query.all()
            for cat in existing_categories:
                print(f"   - {cat.name} ({cat.type})")
            return
        
        print("📁 Creating default categories...")
        
        default_categories = [
            # Expense categories
            ('Food & Dining', 'expense', 'Restaurants, groceries, takeout'),
            ('Transportation', 'expense', 'Gas, public transit, car maintenance'),
            ('Shopping', 'expense', 'Clothing, electronics, general purchases'),
            ('Entertainment', 'expense', 'Movies, games, hobbies'),
            ('Bills & Utilities', 'expense', 'Electricity, water, internet, phone'),
            ('Healthcare', 'expense', 'Medical, dental, pharmacy'),
            ('Education', 'expense', 'Books, courses, tuition'),
            ('Travel', 'expense', 'Flights, hotels, vacation'),
            ('Expense Other', 'expense', 'Miscellaneous expenses'),
            
            # Income categories
            ('Salary', 'income', 'Regular employment income'),
            ('Freelance', 'income', 'Freelance and contract work'),
            ('Investment', 'income', 'Dividends, interest, capital gains'),
            ('Business', 'income', 'Business revenue'),
            ('Gift', 'income', 'Gifts and donations received'),
            ('Income Other', 'income', 'Miscellaneous income')
        ]
        
        created_count = 0
        for name, cat_type, desc in default_categories:
            # Check if this specific category exists
            existing = Category.query.filter_by(name=name).first()
            if not existing:
                category = Category(
                    name=name,
                    type=cat_type,
                    description=desc
                )
                db.session.add(category)
                created_count += 1
                print(f"   + Added: {name} ({cat_type})")
            else:
                print(f"   - Exists: {name} ({cat_type})")
        
        if created_count > 0:
            db.session.commit()
            print(f"✅ Created {created_count} new categories!")
        else:
            print("ℹ️  All default categories already exist")
            
    except Exception as e:
        print(f"❌ Error creating default categories: {e}")
        if db:
            try:
                db.session.rollback()
                print("🔄 Database session rolled back")
            except:
                pass

def clear_all_categories():
    """Clear all categories (for testing purposes)"""
    try:
        if not Category:
            print("❌ Category model not available")
            return
            
        count = Category.query.count()
        if count > 0:
            Category.query.delete()
            db.session.commit()
            print(f"🗑️  Cleared {count} categories")
        else:
            print("ℹ️  No categories to clear")
            
    except Exception as e:
        print(f"❌ Error clearing categories: {e}")
        if db:
            db.session.rollback()

def list_all_categories():
    """List all categories in the database"""
    try:
        if not Category:
            print("❌ Category model not available")
            return
            
        categories = Category.query.all()
        if categories:
            print(f"📋 Found {len(categories)} categories:")
            for cat in categories:
                print(f"   {cat.id}. {cat.name} ({cat.type}) - {cat.description}")
        else:
            print("📋 No categories found")
            
    except Exception as e:
        print(f"❌ Error listing categories: {e}")

# Test function to verify models are working
def test_models():
    """Test that models are properly initialized"""
    try:
        models = [User, Income, Transaction, Budget, BudgetCategory, FinancialGoal, Category]
        model_names = ['User', 'Income', 'Transaction', 'Budget', 'BudgetCategory', 'FinancialGoal', 'Category']
        
        for model, name in zip(models, model_names):
            if model is None:
                print(f"❌ {name} model is None")
                return False
            else:
                print(f"✅ {name} model is ready")
        
        return True
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return False