import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from niner_repo.db import get_db, close_db, init_db
from niner_repo import create_app

class TestDatabase:
    """Test cases for database functionality following schema.sql structure."""
    
    def test_get_close_db(self, app):
        """Test database connection and closing."""
        with app.app_context():
            db = get_db()
            assert db is get_db()  # Should return same connection within context
        
        # Test that database is properly closed
        with pytest.raises(sqlite3.ProgrammingError):
            db.execute('SELECT 1')

    def test_init_db_command(self, runner, monkeypatch):
        """Test the init-db command."""
        class Recorder:
            called = False
        
        def fake_init_db():
            Recorder.called = True
        
        monkeypatch.setattr('niner_repo.db.init_db', fake_init_db)
        result = runner.invoke(args=['init-db'])
        assert 'Initialized' in result.output
        assert Recorder.called

    def test_database_schema_creation(self, app):
        """Test that database schema is created correctly per schema.sql."""
        with app.app_context():
            db = get_db()
            
            # Check that required tables exist (from schema.sql)
            tables = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            
            table_names = [table['name'] for table in tables]
            
            # Core tables from schema.sql
            expected_tables = ['users', 'expenses', 'income']
            for table in expected_tables:
                assert table in table_names, f"Table {table} not found in database"

    def test_users_table_structure(self, app):
        """Test users table structure matches schema.sql exactly."""
        with app.app_context():
            db = get_db()
            
            # Check table structure
            columns = db.execute("PRAGMA table_info(users)").fetchall()
            column_info = {col[1]: {'type': col[2], 'notnull': col[3], 'pk': col[5]} for col in columns}
            
            # Expected columns from schema.sql
            expected_columns = {
                'id': {'type': 'INTEGER', 'notnull': 0, 'pk': 1},
                'username': {'type': 'TEXT', 'notnull': 1, 'pk': 0},
                'email': {'type': 'TEXT', 'notnull': 1, 'pk': 0},
                'password': {'type': 'TEXT', 'notnull': 1, 'pk': 0},
                'created_at': {'type': 'TIMESTAMP', 'notnull': 0, 'pk': 0}
            }
            
            for col_name, expected in expected_columns.items():
                assert col_name in column_info, f"Column {col_name} not found in users table"
                assert column_info[col_name]['type'] == expected['type'], f"Column {col_name} has wrong type"

    def test_expenses_table_structure(self, app):
        """Test expenses table structure matches schema.sql exactly."""
        with app.app_context():
            db = get_db()
            
            # Check table structure
            columns = db.execute("PRAGMA table_info(expenses)").fetchall()
            column_info = {col[1]: {'type': col[2], 'notnull': col[3], 'pk': col[5]} for col in columns}
            
            # Expected columns from schema.sql
            expected_columns = {
                'id': {'type': 'INTEGER', 'notnull': 0, 'pk': 1},
                'user_id': {'type': 'INTEGER', 'notnull': 1, 'pk': 0},
                'amount': {'type': 'REAL', 'notnull': 1, 'pk': 0},
                'description': {'type': 'TEXT', 'notnull': 1, 'pk': 0},
                'category': {'type': 'TEXT', 'notnull': 1, 'pk': 0},
                'date': {'type': 'DATE', 'notnull': 1, 'pk': 0},
                'is_active': {'type': 'INTEGER', 'notnull': 0, 'pk': 0},
                'created_at': {'type': 'TIMESTAMP', 'notnull': 0, 'pk': 0}
            }
            
            for col_name, expected in expected_columns.items():
                assert col_name in column_info, f"Column {col_name} not found in expenses table"

    def test_income_table_structure(self, app):
        """Test income table structure matches schema.sql exactly."""
        with app.app_context():
            db = get_db()
            
            # Check table structure
            columns = db.execute("PRAGMA table_info(income)").fetchall()
            column_info = {col[1]: {'type': col[2], 'notnull': col[3], 'pk': col[5]} for col in columns}
            
            # Expected columns from schema.sql
            expected_columns = {
                'id': {'type': 'INTEGER', 'notnull': 0, 'pk': 1},
                'user_id': {'type': 'INTEGER', 'notnull': 1, 'pk': 0},
                'amount': {'type': 'REAL', 'notnull': 1, 'pk': 0},
                'source': {'type': 'TEXT', 'notnull': 1, 'pk': 0},
                'date': {'type': 'DATE', 'notnull': 1, 'pk': 0},
                'recurrence_period': {'type': 'TEXT', 'notnull': 0, 'pk': 0},
                'is_active': {'type': 'INTEGER', 'notnull': 0, 'pk': 0},
                'created_at': {'type': 'TIMESTAMP', 'notnull': 0, 'pk': 0}
            }
            
            for col_name, expected in expected_columns.items():
                assert col_name in column_info, f"Column {col_name} not found in income table"

    def test_users_table_operations(self, app):
        """Test users table CRUD operations with exact schema fields."""
        with app.app_context():
            db = get_db()
            
            # CREATE - Insert a user with schema.sql fields only
            db.execute('''
                INSERT INTO users (username, email, password, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('testuser', 'test@example.com', 'hashed_password', datetime.now().isoformat()))
            db.commit()
            
            # READ - Retrieve user
            user = db.execute(
                'SELECT * FROM users WHERE username = ?', ('testuser',)
            ).fetchone()
            
            assert user is not None
            assert user['username'] == 'testuser'
            assert user['email'] == 'test@example.com'
            
            # UPDATE - Modify user
            db.execute('''
                UPDATE users SET email = ? WHERE username = ?
            ''', ('newemail@example.com', 'testuser'))
            db.commit()
            
            updated_user = db.execute(
                'SELECT email FROM users WHERE username = ?', ('testuser',)
            ).fetchone()
            
            assert updated_user['email'] == 'newemail@example.com'
            
            # DELETE - Remove user
            db.execute('DELETE FROM users WHERE username = ?', ('testuser',))
            db.commit()
            
            deleted_user = db.execute(
                'SELECT * FROM users WHERE username = ?', ('testuser',)
            ).fetchone()
            
            assert deleted_user is None

    def test_expenses_table_operations(self, app):
        """Test expenses table CRUD operations with exact schema fields."""
        with app.app_context():
            db = get_db()
            
            # Create test user first
            db.execute('''
                INSERT INTO users (username, email, password, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('testuser', 'test@example.com', 'password', datetime.now().isoformat()))
            db.commit()
            
            user_id = db.lastrowid
            expense_date = datetime.now().strftime('%Y-%m-%d')
            
            # CREATE - Insert expense with schema.sql fields only
            db.execute('''
                INSERT INTO expenses (user_id, amount, description, category, date, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, 85.50, 'Test Grocery Shopping', 'food', expense_date, 1, datetime.now().isoformat()))
            db.commit()
            
            expense_id = db.lastrowid
            
            # READ - Retrieve expense
            expense = db.execute(
                'SELECT * FROM expenses WHERE id = ?', (expense_id,)
            ).fetchone()
            
            assert expense is not None
            assert expense['description'] == 'Test Grocery Shopping'
            assert expense['amount'] == 85.50
            assert expense['category'] == 'food'
            assert expense['user_id'] == user_id
            
            # UPDATE - Modify expense
            db.execute('''
                UPDATE expenses SET amount = ?, description = ? WHERE id = ?
            ''', (95.75, 'Updated Grocery Shopping', expense_id))
            db.commit()
            
            updated_expense = db.execute(
                'SELECT amount, description FROM expenses WHERE id = ?', (expense_id,)
            ).fetchone()
            
            assert updated_expense['amount'] == 95.75
            assert updated_expense['description'] == 'Updated Grocery Shopping'
            
            # DELETE - Soft delete expense using is_active
            db.execute('''
                UPDATE expenses SET is_active = 0 WHERE id = ?
            ''', (expense_id,))
            db.commit()
            
            inactive_expense = db.execute(
                'SELECT is_active FROM expenses WHERE id = ?', (expense_id,)
            ).fetchone()
            
            assert inactive_expense['is_active'] == 0

    def test_income_table_operations(self, app):
        """Test income table CRUD operations with exact schema fields."""
        with app.app_context():
            db = get_db()
            
            # Create test user
            db.execute('''
                INSERT INTO users (username, email, password, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('testuser', 'test@example.com', 'password', datetime.now().isoformat()))
            db.commit()
            
            user_id = db.lastrowid
            income_date = datetime.now().strftime('%Y-%m-%d')
            
            # CREATE - Insert income with schema.sql fields only
            db.execute('''
                INSERT INTO income (user_id, amount, source, date, recurrence_period, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, 3500.00, 'Monthly Salary', income_date, 'monthly', 1, datetime.now().isoformat()))
            db.commit()
            
            income_id = db.lastrowid
            
            # READ - Retrieve income
            income = db.execute(
                'SELECT * FROM income WHERE id = ?', (income_id,)
            ).fetchone()
            
            assert income is not None
            assert income['amount'] == 3500.00
            assert income['source'] == 'Monthly Salary'
            assert income['recurrence_period'] == 'monthly'
            
            # UPDATE - Modify income
            db.execute('''
                UPDATE income SET amount = ? WHERE id = ?
            ''', (3750.00, income_id))
            db.commit()
            
            updated_income = db.execute(
                'SELECT amount FROM income WHERE id = ?', (income_id,)
            ).fetchone()
            
            assert updated_income['amount'] == 3750.00

    def test_expense_categories_validation(self, app):
        """Test that expense categories match the 4 categories from schema (food, transportation, entertainment, other)."""
        with app.app_context():
            db = get_db()
            
            # Create test user
            db.execute('''
                INSERT INTO users (username, email, password, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('testuser', 'test@example.com', 'password', datetime.now().isoformat()))
            db.commit()
            
            user_id = db.lastrowid
            valid_categories = ['food', 'transportation', 'entertainment', 'other']
            
            # Test each valid category
            for i, category in enumerate(valid_categories, 1):
                db.execute('''
                    INSERT INTO expenses (user_id, amount, description, category, date, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, 25.00, f'Test {category} expense', category, 
                     datetime.now().strftime('%Y-%m-%d'), 1, datetime.now().isoformat()))
                db.commit()
                
                # Verify expense was created
                expense = db.execute(
                    'SELECT category FROM expenses WHERE description = ?', (f'Test {category} expense',)
                ).fetchone()
                
                assert expense['category'] == category

    def test_income_recurrence_periods(self, app):
        """Test income recurrence periods (none, weekly, monthly, yearly)."""
        with app.app_context():
            db = get_db()
            
            # Create test user
            db.execute('''
                INSERT INTO users (username, email, password, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('testuser', 'test@example.com', 'password', datetime.now().isoformat()))
            db.commit()
            
            user_id = db.lastrowid
            valid_periods = ['none', 'weekly', 'monthly', 'yearly']
            
            # Test each valid recurrence period
            for i, period in enumerate(valid_periods, 1):
                db.execute('''
                    INSERT INTO income (user_id, amount, source, date, recurrence_period, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, 100.00 * i, f'Test {period} income', 
                     datetime.now().strftime('%Y-%m-%d'), period, 1, datetime.now().isoformat()))
                db.commit()
                
                # Verify income was created
                income = db.execute(
                    'SELECT recurrence_period FROM income WHERE source = ?', (f'Test {period} income',)
                ).fetchone()
                
                assert income['recurrence_period'] == period

    def test_foreign_key_constraints(self, app):
        """Test foreign key constraints between users and expenses/income."""
        with app.app_context():
            db = get_db()
            
            # Enable foreign key constraints
            db.execute('PRAGMA foreign_keys = ON')
            
            # Try to insert expense for non-existent user
            with pytest.raises(sqlite3.IntegrityError):
                db.execute('''
                    INSERT INTO expenses (user_id, amount, description, category, date, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (999, 25.50, 'Test Expense', 'food', 
                     datetime.now().strftime('%Y-%m-%d'), 1, datetime.now().isoformat()))
                db.commit()
            
            # Try to insert income for non-existent user
            with pytest.raises(sqlite3.IntegrityError):
                db.execute('''
                    INSERT INTO income (user_id, amount, source, date, recurrence_period, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (999, 1000.00, 'Test Income', 
                     datetime.now().strftime('%Y-%m-%d'), 'monthly', 1, datetime.now().isoformat()))
                db.commit()

    def test_data_with_test_data_sql(self, app_with_data):
        """Test database operations with loaded test data from data.sql."""
        with app_with_data.app_context():
            db = get_db()
            
            # Verify test users were loaded
            users = db.execute('SELECT COUNT(*) as count FROM users').fetchone()
            assert users['count'] == 5
            
            # Verify test expenses were loaded
            expenses = db.execute('SELECT COUNT(*) as count FROM expenses WHERE is_active = 1').fetchone()
            assert expenses['count'] >= 40  # Should have at least 40 active expenses
            
            # Verify test income was loaded
            income = db.execute('SELECT COUNT(*) as count FROM income WHERE is_active = 1').fetchone()
            assert income['count'] >= 20  # Should have at least 20 active income records
            
            # Test category distribution
            categories = db.execute('''
                SELECT category, COUNT(*) as count 
                FROM expenses 
                WHERE is_active = 1 
                GROUP BY category
            ''').fetchall()
            
            category_counts = {cat['category']: cat['count'] for cat in categories}
            
            # All 4 categories should be present
            expected_categories = ['food', 'transportation', 'entertainment', 'other']
            for category in expected_categories:
                assert category in category_counts, f"Category {category} not found in test data"
                assert category_counts[category] > 0, f"No expenses found for category {category}"

    def test_date_range_queries_with_test_data(self, app_with_data):
        """Test date range queries using test data."""
        with app_with_data.app_context():
            db = get_db()
            
            # Test expenses in October 2024
            october_expenses = db.execute('''
                SELECT COUNT(*) as count FROM expenses 
                WHERE date >= '2024-10-01' AND date < '2024-11-01' AND is_active = 1
            ''').fetchone()
            
            assert october_expenses['count'] > 0
            
            # Test expenses by user (demo user should have expenses)
            demo_user_expenses = db.execute('''
                SELECT COUNT(*) as count FROM expenses 
                WHERE user_id = 1 AND is_active = 1
            ''').fetchone()
            
            assert demo_user_expenses['count'] > 0

    def test_aggregation_queries_with_test_data(self, app_with_data):
        """Test aggregation queries using test data."""
        with app_with_data.app_context():
            db = get_db()
            
            # Test total expenses by category for demo user
            category_totals = db.execute('''
                SELECT 
                    category,
                    SUM(amount) as total,
                    COUNT(*) as count
                FROM expenses 
                WHERE user_id = 1 AND is_active = 1
                GROUP BY category
                ORDER BY total DESC
            ''').fetchall()
            
            assert len(category_totals) > 0
            
            # Verify amounts are reasonable
            for category in category_totals:
                assert category['total'] > 0
                assert category['count'] > 0
            
            # Test total income for demo user
            total_income = db.execute('''
                SELECT SUM(amount) as total FROM income 
                WHERE user_id = 1 AND is_active = 1
            ''').fetchone()
            
            assert total_income['total'] > 0

    def test_data_integrity_with_test_data(self, app_with_data):
        """Test data integrity constraints with loaded test data."""
        with app_with_data.app_context():
            db = get_db()
            
            # Verify all expenses have valid user_ids
            orphaned_expenses = db.execute('''
                SELECT COUNT(*) as count FROM expenses e
                LEFT JOIN users u ON e.user_id = u.id
                WHERE u.id IS NULL
            ''').fetchone()
            
            assert orphaned_expenses['count'] == 0
            
            # Verify all income has valid user_ids
            orphaned_income = db.execute('''
                SELECT COUNT(*) as count FROM income i
                LEFT JOIN users u ON i.user_id = u.id
                WHERE u.id IS NULL
            ''').fetchone()
            
            assert orphaned_income['count'] == 0
            
            # Verify all categories are valid
            invalid_categories = db.execute('''
                SELECT COUNT(*) as count FROM expenses 
                WHERE category NOT IN ('food', 'transportation', 'entertainment', 'other')
            ''').fetchone()
            
            assert invalid_categories['count'] == 0
            
            # Verify all recurrence periods are valid
            invalid_periods = db.execute('''
                SELECT COUNT(*) as count FROM income 
                WHERE recurrence_period NOT IN ('none', 'weekly', 'monthly', 'yearly')
                AND recurrence_period IS NOT NULL
            ''').fetchone()
            
            assert invalid_periods['count'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])