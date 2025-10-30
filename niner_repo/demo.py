import sqlite3
import os
from werkzeug.security import generate_password_hash

# Path to your database
db_path = os.path.join('instance', 'niner_finance.db')

# Make sure instance directory exists
os.makedirs('instance', exist_ok=True)

# Demo user credentials
demo_username = "demo"
demo_email = "demo@ninerfinance.com"
demo_password = "demo123"

print("Creating demo user to match schema and models...")

try:
    with sqlite3.connect(db_path) as conn:
        # Check the actual table structure first
        cursor = conn.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        
        print("Current user table structure:")
        for col in columns:
            print(f"   Column: {col[1]}, Type: {col[2]}")
        
        # Get column names
        column_names = [col[1] for col in columns]
        
        # Determine correct password column (from your models it's 'password')
        password_column = 'password' if 'password' in column_names else 'password_hash'
        print(f"Using password column: {password_column}")
        
        # Check if demo user already exists
        existing_user = conn.execute(
            "SELECT id FROM user WHERE username = ?", (demo_username,)
        ).fetchone()
        
        if existing_user:
            print("✅ Demo user already exists!")
            print(f"Username: {demo_username}")
            print(f"Password: {demo_password}")
            user_id = existing_user[0]
        else:
            # Create demo user
            password_hash = generate_password_hash(demo_password)
            
            query = f"INSERT INTO user (username, email, {password_column}) VALUES (?, ?, ?)"
            cursor = conn.execute(query, (demo_username, demo_email, password_hash))
            user_id = cursor.lastrowid
            
            print("✅ Demo user created successfully!")
            print(f"Username: {demo_username}")
            print(f"Password: {demo_password}")
            print(f"User ID: {user_id}")
        
        # Create income categories if they don't exist (from schema)
        income_categories = [
            ('Salary', 'Regular employment income'),
            ('Freelance', 'Income from freelance work'),
            ('Investment', 'Income from investments'),
            ('Business', 'Business income'),
            ('Other', 'Other sources of income')
        ]
        
        category_ids = {}
        for cat_name, cat_desc in income_categories:
            existing_cat = conn.execute(
                "SELECT id FROM income_category WHERE name = ?", (cat_name,)
            ).fetchone()
            
            if existing_cat:
                category_ids[cat_name] = existing_cat[0]
            else:
                cursor = conn.execute(
                    "INSERT INTO income_category (name, description, created_by) VALUES (?, ?, ?)",
                    (cat_name, cat_desc, user_id)
                )
                category_ids[cat_name] = cursor.lastrowid
                print(f"   Created income category: {cat_name}")
        
        # Add demo income records (matching your schema)
        demo_income = [
            ("Monthly Salary", 2500.00, "Salary", "Regular full-time job", "2024-01-01", True, "monthly"),
            ("Freelance Project", 300.00, "Freelance", "Web design project", "2024-01-05", False, None),
            ("Investment Dividends", 75.50, "Investment", "Stock dividends", "2024-01-15", False, None),
        ]
        
        for source, amount, category, description, date, is_recurring, recurrence in demo_income:
            # Check if this income already exists
            existing_income = conn.execute(
                "SELECT id FROM income WHERE user_id = ? AND source = ? AND date = ?",
                (user_id, source, date)
            ).fetchone()
            
            if not existing_income:
                category_id = category_ids.get(category, category_ids['Other'])
                next_recurrence = None
                if is_recurring and recurrence == "monthly":
                    next_recurrence = "2024-02-01"  # Next month
                
                conn.execute(
                    """INSERT INTO income (user_id, category_id, amount, source, description, date, 
                       is_recurring, recurrence_period, next_recurrence_date, created_by) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, category_id, amount, source, description, date, 
                     is_recurring, recurrence, next_recurrence, user_id)
                )
                print(f"   Added income: {source} - ${amount}")
        
        # Add demo expenses (matching your schema)
        demo_expenses = [
            ("Grocery Store", 45.67, "food", "Weekly groceries", "2024-01-02"),
            ("Gas Station", 52.30, "transportation", "Fill up car", "2024-01-03"),
            ("Coffee Shop", 4.50, "food", "Morning coffee", "2024-01-04"),
            ("Electric Bill", 89.45, "other", "Monthly electric bill", "2024-01-06"),
            ("Netflix", 15.99, "entertainment", "Monthly subscription", "2024-01-07"),
            ("Lunch", 12.50, "food", "Restaurant lunch", "2024-01-08"),
            ("Uber Ride", 18.75, "transportation", "Ride to airport", "2024-01-09"),
        ]
        
        for description, amount, category, desc, date in demo_expenses:
            # Check if this expense already exists
            existing_expense = conn.execute(
                "SELECT id FROM expenses WHERE user_id = ? AND description = ? AND date = ?",
                (user_id, description, date)
            ).fetchone()
            
            if not existing_expense:
                conn.execute(
                    """INSERT INTO expenses (user_id, category, amount, description, date, created_by) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, category, amount, description, date, user_id)
                )
                print(f"   Added expense: {description} - ${amount}")
        
        # Add demo transactions (if your app uses the transactions table)
        demo_transactions = [
            ("Monthly Salary", 2500.00, "income", "Salary payment", "2024-01-01"),
            ("Grocery Store", 45.67, "expense", "Weekly groceries", "2024-01-02"),
            ("Freelance Work", 300.00, "income", "Web design project", "2024-01-05"),
        ]
        
        for description, amount, trans_type, desc, date in demo_transactions:
            # Check if this transaction already exists
            existing_trans = conn.execute(
                "SELECT id FROM transactions WHERE user_id = ? AND description = ? AND date = ?",
                (user_id, description, date)
            ).fetchone()
            
            if not existing_trans:
                conn.execute(
                    """INSERT INTO transactions (user_id, transaction_type, amount, description, date) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, trans_type, amount, description, date)
                )
                print(f"   Added transaction: {description} - ${amount} ({trans_type})")
        
        conn.commit()
        print("✅ All demo data created successfully!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Verify the user was created
try:
    with sqlite3.connect(db_path) as conn:
        # Check users
        users = conn.execute("SELECT id, username, email FROM user").fetchall()
        print(f"\n📋 All users in database:")
        for user in users:
            print(f"   ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
        
        # Check demo user's data
        demo_user = conn.execute("SELECT id FROM user WHERE username = 'demo'").fetchone()
        if demo_user:
            demo_id = demo_user[0]
            
            # Count income records
            income_count = conn.execute("SELECT COUNT(*) FROM income WHERE user_id = ?", (demo_id,)).fetchone()[0]
            print(f"   Demo user has {income_count} income records")
            
            # Count expense records
            expense_count = conn.execute("SELECT COUNT(*) FROM expenses WHERE user_id = ?", (demo_id,)).fetchone()[0]
            print(f"   Demo user has {expense_count} expense records")
            
            # Count transaction records
            trans_count = conn.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ?", (demo_id,)).fetchone()[0]
            print(f"   Demo user has {trans_count} transaction records")
        
except Exception as e:
    print(f"❌ Error verifying: {e}")

print(f"\n🎯 Demo account ready!")
print(f"Username: {demo_username}")
print(f"Password: {demo_password}")
print(f"You can now log in to test the application!")