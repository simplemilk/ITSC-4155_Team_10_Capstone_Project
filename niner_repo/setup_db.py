#!/usr/bin/env python3
"""
Create a complete database with all required tables and sample data
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def setup_database():
    """Set up complete database with all tables and sample data"""
    db_path = 'niner_finance.sqlite'
    
    # Remove existing database
    if os.path.exists(db_path):
        backup_name = f"{db_path}.backup"
        if os.path.exists(backup_name):
            os.remove(backup_name)
        os.rename(db_path, backup_name)
        print(f"✓ Backed up existing database to {backup_name}")
    
    # Create new database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Create user table with security questions
        cursor.execute('''
            CREATE TABLE user (
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
        print("✓ User table created with security questions")
        
        # Create password_resets table
        cursor.execute('''
            CREATE TABLE password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        print("✓ Password resets table created")
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        print("✓ Transactions table created")
        
        # Create budgets table
        cursor.execute('''
            CREATE TABLE budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                food_budget REAL DEFAULT 0,
                transportation_budget REAL DEFAULT 0,
                entertainment_budget REAL DEFAULT 0,
                other_budget REAL DEFAULT 0,
                week_start_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        print("✓ Budgets table created")
        
        # Create income_sources table
        cursor.execute('''
            CREATE TABLE income_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                source_name TEXT NOT NULL,
                amount REAL NOT NULL,
                frequency TEXT NOT NULL CHECK (frequency IN ('weekly', 'bi-weekly', 'monthly', 'yearly')),
                start_date DATE,
                end_date DATE,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        print("✓ Income sources table created")
        
        # Create financial_goals table (for future use)
        cursor.execute('''
            CREATE TABLE financial_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                goal_name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                target_date DATE,
                category TEXT,
                description TEXT,
                is_completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        print("✓ Financial goals table created")
        
        # Create demo user with security questions
        demo_password = generate_password_hash('demo123')
        demo_answer_1 = generate_password_hash('fluffy')  # Hash the answers for security
        demo_answer_2 = generate_password_hash('rover')
        
        cursor.execute('''
            INSERT INTO user (username, email, password, security_question_1, security_answer_1, security_question_2, security_answer_2) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            'demo', 
            'demo@ninerfinance.com', 
            demo_password,
            "What was the name of your first pet?",
            demo_answer_1,
            "What was the name of your childhood best friend?",
            demo_answer_2
        ))
        
        demo_user_id = cursor.lastrowid
        print("✓ Demo user created with security questions")
        print("  Demo login: username=demo, password=demo123")
        print("  Demo security answers: 'fluffy' and 'rover'")
        
        # Create test user without security questions (for testing migration)
        test_password = generate_password_hash('test123')
        cursor.execute('''
            INSERT INTO user (username, email, password) 
            VALUES (?, ?, ?)
        ''', ('test', 'test@example.com', test_password))
        test_user_id = cursor.lastrowid
        print("✓ Test user created without security questions")
        
        # Create sample data for demo user
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        # Sample budget for demo user
        cursor.execute('''
            INSERT INTO budgets (user_id, total_amount, food_budget, transportation_budget, entertainment_budget, other_budget, week_start_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (demo_user_id, 500.0, 200.0, 100.0, 150.0, 50.0, week_start.isoformat()))
        print("✓ Sample budget created for demo user")
        
        # Sample transactions for demo user
        sample_transactions = [
            ('expense', 25.50, 'Food', 'Grocery shopping', today.isoformat()),
            ('expense', 15.00, 'Transportation', 'Bus fare', (today - timedelta(days=1)).isoformat()),
            ('expense', 30.00, 'Entertainment', 'Movie tickets', (today - timedelta(days=2)).isoformat()),
            ('income', 800.00, 'Salary', 'Part-time job', (today - timedelta(days=3)).isoformat()),
            ('expense', 12.99, 'Food', 'Lunch', (today - timedelta(days=3)).isoformat()),
            ('expense', 45.00, 'Food', 'Dinner out', (today - timedelta(days=4)).isoformat()),
            ('expense', 20.00, 'Transportation', 'Gas', (today - timedelta(days=5)).isoformat()),
            ('expense', 8.50, 'Other', 'Coffee', (today - timedelta(days=6)).isoformat()),
            ('income', 200.00, 'Side Job', 'Freelance work', (today - timedelta(days=7)).isoformat()),
            ('expense', 60.00, 'Entertainment', 'Concert ticket', (today - timedelta(days=8)).isoformat()),
        ]
        
        for trans in sample_transactions:
            cursor.execute('''
                INSERT INTO transactions (user_id, type, amount, category, description, date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (demo_user_id,) + trans)
        
        print(f"✓ {len(sample_transactions)} sample transactions created for demo user")
        
        # Sample income sources for demo user
        sample_income_sources = [
            ('Part-time Job', 800.0, 'bi-weekly', today.isoformat(), 1),
            ('Freelance Work', 200.0, 'monthly', today.isoformat(), 1),
            ('Scholarship', 1000.0, 'monthly', today.isoformat(), 1),
        ]
        
        for source in sample_income_sources:
            cursor.execute('''
                INSERT INTO income_sources (user_id, source_name, amount, frequency, start_date, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (demo_user_id,) + source)
        
        print(f"✓ {len(sample_income_sources)} sample income sources created for demo user")
        
        # Sample financial goals for demo user
        sample_goals = [
            ('Emergency Fund', 1000.0, 250.0, (today + timedelta(days=180)).isoformat(), 'Savings', 'Build emergency fund for unexpected expenses'),
            ('New Laptop', 800.0, 150.0, (today + timedelta(days=120)).isoformat(), 'Technology', 'Save for new laptop for school'),
            ('Spring Break Trip', 600.0, 50.0, (today + timedelta(days=90)).isoformat(), 'Travel', 'Save for spring break vacation'),
        ]
        
        for goal in sample_goals:
            cursor.execute('''
                INSERT INTO financial_goals (user_id, goal_name, target_amount, current_amount, target_date, category, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (demo_user_id,) + goal)
        
        print(f"✓ {len(sample_goals)} sample financial goals created for demo user")
        
        # Commit changes
        conn.commit()
        
        # Verify setup
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📋 Database setup complete!")
        print(f"📂 Database file: {os.path.abspath(db_path)}")
        print(f"🗂️ Tables created: {[table[0] for table in tables]}")
        print(f"👥 Total users: {user_count}")
        
        # Show demo user summary
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ?", (demo_user_id,))
        transaction_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM budgets WHERE user_id = ?", (demo_user_id,))
        budget_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM income_sources WHERE user_id = ?", (demo_user_id,))
        income_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM financial_goals WHERE user_id = ?", (demo_user_id,))
        goals_count = cursor.fetchone()[0]
        
        print(f"\n👤 Demo User Summary:")
        print(f"   Username: demo")
        print(f"   Password: demo123")
        print(f"   Security Answers: 'fluffy' and 'rover'")
        print(f"   Transactions: {transaction_count}")
        print(f"   Budgets: {budget_count}")
        print(f"   Income Sources: {income_count}")
        print(f"   Financial Goals: {goals_count}")
        
        # Show table structure
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        print(f"\n📋 User table structure:")
        for col in columns:
            print(f"  - {col[1]}: {col[2]}")
        
        print(f"\n✓ Database setup completed: {os.path.abspath(db_path)}")
        
    except Exception as e:
        print(f"✗ Error setting up database: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == '__main__':
    print("=== Setting up Complete Niner Finance Database ===")
    if setup_database():
        print("\n🎉 Database is ready with full functionality!")
        print("\nYou can now:")
        print("1. Run: python3 app.py")
        print("2. Register new users with security questions")
        print("3. Use demo account: demo/demo123")
        print("4. Test password recovery with security questions")
        print("5. View dashboard with real financial data")
        print("6. Test all financial management features")
    else:
        print("\n❌ Database setup failed!")