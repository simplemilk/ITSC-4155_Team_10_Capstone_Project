import os
import sys
import sqlite3
from datetime import datetime, timedelta

def seed_demo_data(db_path):
    """Add sample data for demo user"""
    print("\n📦 Seeding demo data...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get demo user ID
        demo_user = cursor.execute("SELECT id FROM users WHERE username = 'demo'").fetchone()
        if not demo_user:
            print("⚠️  Demo user not found, skipping data seeding")
            conn.close()
            return False
        
        user_id = demo_user[0]
        
        # Clear existing demo data
        cursor.execute("DELETE FROM expenses WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM income WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM budgets WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM financial_goals WHERE user_id = ?", (user_id,))
        conn.commit()
        
        # 1. Add Weekly Budget
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        cursor.execute('''
            INSERT INTO budgets (user_id, total_amount, food_budget, transportation_budget, 
                               entertainment_budget, other_budget, week_start_date)
            VALUES (?, 500.00, 200.00, 100.00, 100.00, 100.00, ?)
        ''', (user_id, week_start.date()))
        
        # 2. Add Income Categories
        income_categories = [
            ('Salary', 'Monthly salary'),
            ('Freelance', 'Freelance work'),
            ('Investment', 'Investment returns')
        ]
        
        for name, desc in income_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO income_category (name, description, created_by)
                VALUES (?, ?, ?)
            ''', (name, desc, user_id))
        
        conn.commit()
        
        # Get category IDs
        salary_cat = cursor.execute("SELECT id FROM income_category WHERE name = 'Salary'").fetchone()[0]
        
        # 3. Add Sample Income
        income_data = [
            (salary_cat, 3000.00, 'Monthly Salary', datetime.now().replace(day=1).date()),
            (salary_cat, 500.00, 'Bonus', (datetime.now() - timedelta(days=15)).date()),
        ]
        
        for cat_id, amount, source, date in income_data:
            cursor.execute('''
                INSERT INTO income (user_id, category_id, amount, source, date, created_by, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (user_id, cat_id, amount, source, date, user_id))
            
            # Also add to transactions
            cursor.execute('''
                INSERT INTO transactions (user_id, transaction_type, amount, description, date)
                VALUES (?, 'income', ?, ?, ?)
            ''', (user_id, amount, source, date))
        
        # 4. Add Sample Expenses with proper categories
        expenses_data = [
            # Food expenses
            ('food', 45.50, 'Grocery shopping at Harris Teeter', 1),
            ('food', 22.00, 'Lunch at Student Union', 2),
            ('food', 15.75, 'Coffee at Starbucks', 3),
            ('food', 35.20, 'Dinner at Chipotle', 4),
            ('food', 18.50, 'Pizza delivery', 5),
            
            # Transportation expenses
            ('transportation', 50.00, 'Gas for the week', 1),
            ('transportation', 25.00, 'Uber to airport', 4),
            ('transportation', 15.00, 'Parking fee', 6),
            ('transportation', 40.00, 'Monthly bus pass', 7),
            
            # Entertainment expenses
            ('entertainment', 40.00, 'Movie tickets with friends', 2),
            ('entertainment', 60.00, 'Concert at Fillmore', 5),
            ('entertainment', 25.00, 'Bowling night', 8),
            ('entertainment', 30.00, 'Video game purchase', 10),
            
            # Other expenses
            ('other', 30.00, 'Miscellaneous supplies', 3),
            ('other', 45.00, 'Textbook purchase', 6),
            ('other', 20.00, 'Phone case', 9),
        ]
        
        for category, amount, desc, days_ago in expenses_data:
            expense_date = (datetime.now() - timedelta(days=days_ago)).date()
            
            # Insert into expenses table
            cursor.execute('''
                INSERT INTO expenses (user_id, category, amount, description, date, created_by, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (user_id, category, amount, desc, expense_date, user_id))
            
            # Also add to transactions table WITH CATEGORY
            cursor.execute('''
                INSERT INTO transactions (user_id, transaction_type, category, amount, description, date)
                VALUES (?, 'expense', ?, ?, ?, ?)
            ''', (user_id, category, amount, desc, expense_date))
        
        # 5. Add Sample Subscriptions
        subscriptions_data = [
            ('Netflix', 15.99, 'monthly', 'Streaming', 1, True),
            ('Spotify', 9.99, 'monthly', 'Music', 5, True),
            ('Amazon Prime', 14.99, 'monthly', 'Other', 10, True),
            ('Gym Membership', 29.99, 'monthly', 'Fitness', 1, True),
            ('Adobe Creative Cloud', 52.99, 'monthly', 'Software', 15, True),
        ]
        
        for name, amount, frequency, category, day_of_month, is_active in subscriptions_data:
            next_billing = datetime.now().replace(day=day_of_month)
            if next_billing < datetime.now():
                # Move to next month
                if next_billing.month == 12:
                    next_billing = next_billing.replace(year=next_billing.year + 1, month=1)
                else:
                    next_billing = next_billing.replace(month=next_billing.month + 1)
            
            cursor.execute('''
                INSERT INTO subscriptions (user_id, name, amount, frequency, category, 
                                         next_billing_date, start_date, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, name, amount, frequency, category, next_billing.date().isoformat(), 
                  datetime.now().date().isoformat(), is_active))
        
        # 6. Add Sample Financial Goals
        goals_data = [
            ('Emergency Fund', 5000.00, 1200.00, 'emergency', 'Build 3-6 months emergency savings', 'high', 180),
            ('New Laptop', 1500.00, 450.00, 'technology', 'Save for MacBook Pro', 'medium', 90),
            ('Spring Break Trip', 800.00, 200.00, 'travel', 'Beach vacation with friends', 'medium', 120),
            ('Car Down Payment', 3000.00, 500.00, 'transportation', 'Save for used car', 'high', 365),
            ('Professional Certification', 600.00, 150.00, 'education', 'AWS certification course', 'low', 60),
        ]
        
        for goal_name, target, current, category, description, priority, days in goals_data:
            target_date = (datetime.now() + timedelta(days=days)).date().isoformat()
            
            cursor.execute('''
                INSERT INTO financial_goals 
                (user_id, goal_name, target_amount, current_amount, target_date, 
                 category, description, priority, is_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (user_id, goal_name, target, current, target_date, category, description, priority))
        
        conn.commit()
        conn.close()
        
        print("✓ Demo data seeded successfully")
        print(f"  - 1 weekly budget")
        print(f"  - 2 income records")
        print(f"  - {len(expenses_data)} expense records")
        print(f"    • Food: {len([e for e in expenses_data if e[0] == 'food'])} expenses")
        print(f"    • Transportation: {len([e for e in expenses_data if e[0] == 'transportation'])} expenses")
        print(f"    • Entertainment: {len([e for e in expenses_data if e[0] == 'entertainment'])} expenses")
        print(f"    • Other: {len([e for e in expenses_data if e[0] == 'other'])} expenses")
        print(f"  - {len(subscriptions_data)} subscriptions")
        print(f"  - {len(goals_data)} financial goals")
        return True
        
    except Exception as e:
        print(f"❌ Demo data seeding error: {e}")
        import traceback
        traceback.print_exc()
        return False

def init_all_databases():
    """Initialize all database schemas"""
    print("\n" + "=" * 60)
    print("🔧 Niner Finance - Complete Database Initialization")
    print("=" * 60)
    
    # Use instance folder
    instance_dir = 'instance'
    os.makedirs(instance_dir, exist_ok=True)
    db_path = os.path.join(instance_dir, 'niner_finance.sqlite')
    
    success_count = 0
    total_count = 0
    
    # 1. Main schema (users, password_resets, positions, portfolio_history, subscriptions)
    print("\n📊 Initializing main schema...")
    total_count += 1
    try:
        conn = sqlite3.connect(db_path)
        
        # Create users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                security_question_1 TEXT,
                security_answer_1 TEXT,
                security_question_2 TEXT,
                security_answer_2 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create positions table for portfolio
        conn.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                investment_id INTEGER NOT NULL,
                quantity REAL NOT NULL DEFAULT 0,
                avg_cost REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (investment_id) REFERENCES investments (id),
                UNIQUE(user_id, investment_id)
            )
        ''')
        
        # Create portfolio_history table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_value REAL NOT NULL,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create subscriptions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                frequency TEXT NOT NULL CHECK(frequency IN ('daily', 'weekly', 'monthly', 'yearly')),
                category TEXT,
                next_billing_date TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                is_active INTEGER DEFAULT 1,
                auto_detected INTEGER DEFAULT 0,
                transaction_id INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE SET NULL
            )
        ''')
        
        # Create subscription categories
        conn.execute('''
            CREATE TABLE IF NOT EXISTS subscription_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                icon TEXT,
                color TEXT
            )
        ''')
        
        # Insert default subscription categories
        categories = [
            ('Streaming', 'fa-tv', '#e74c3c'),
            ('Music', 'fa-music', '#9b59b6'),
            ('Software', 'fa-laptop-code', '#3498db'),
            ('Gaming', 'fa-gamepad', '#e67e22'),
            ('Fitness', 'fa-dumbbell', '#27ae60'),
            ('News', 'fa-newspaper', '#34495e'),
            ('Cloud Storage', 'fa-cloud', '#1abc9c'),
            ('Utilities', 'fa-bolt', '#f39c12'),
            ('Insurance', 'fa-shield-alt', '#16a085'),
            ('Other', 'fa-ellipsis-h', '#95a5a6')
        ]
        
        conn.executemany('''
            INSERT OR IGNORE INTO subscription_categories (name, icon, color)
            VALUES (?, ?, ?)
        ''', categories)
        
        # Create indexes for subscriptions
        conn.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_next_billing ON subscriptions(next_billing_date)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(is_active)')
        
        conn.commit()
        conn.close()
        print("✓ Main schema initialized")
        success_count += 1
    except Exception as e:
        print(f"❌ Main schema error: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. Budget schema
    print("\n💰 Initializing budget tables...")
    total_count += 1
    try:
        conn = sqlite3.connect(db_path)
        with open('budget_schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.close()
        print("✓ Budget tables initialized")
        success_count += 1
    except Exception as e:
        print(f"❌ Budget error: {e}")
    
    # 3. Schema.sql (transactions, income, expenses, financial_goals)
    print("\n📝 Initializing transaction/income/expense/goals tables...")
    total_count += 1
    try:
        conn = sqlite3.connect(db_path)
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.close()
        print("✓ Transaction tables initialized")
        success_count += 1
    except Exception as e:
        print(f"❌ Schema error: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Create demo user
    print("\n👤 Creating demo user...")
    total_count += 1
    try:
        from werkzeug.security import generate_password_hash
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if demo user exists
        existing = cursor.execute("SELECT id FROM users WHERE username = 'demo'").fetchone()
        
        if not existing:
            demo_answer_1 = generate_password_hash('fluffy')
            demo_answer_2 = generate_password_hash('rover')
            
            cursor.execute('''
                INSERT INTO users (username, email, password, security_question_1, security_answer_1, security_question_2, security_answer_2) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                'demo', 
                'demo@ninerfinance.com', 
                generate_password_hash('demo123'),
                "What was the name of your first pet?",
                demo_answer_1,
                "What was the name of your childhood best friend?",
                demo_answer_2
            ))
            conn.commit()
        
        conn.close()
        print("✓ Demo user created/verified")
        success_count += 1
    except Exception as e:
        print(f"❌ Demo user error: {e}")
    
    # 5. Seed demo data
    total_count += 1
    if seed_demo_data(db_path):
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Initialization Summary: {success_count}/{total_count} successful")
    print("=" * 60)
    
    if success_count == total_count:
        print("\n✅ Database fully initialized with sample data!")
        print("\n🔐 Login credentials:")
        print("   Username: demo")
        print("   Password: demo123")
    
    return success_count == total_count

if __name__ == '__main__':
    success = init_all_databases()
    sys.exit(0 if success else 1)