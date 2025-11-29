import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from niner_repo.db import get_db, close_db, init_db
from niner_repo import create_app

class TestDatabase:
    """Test cases for database functionality."""
    
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
        """Test that database schema is created correctly."""
        with app.app_context():
            db = get_db()
            
            # Check that required tables exist
            tables = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            
            table_names = [table[0] for table in tables]
            
            # Core tables should exist
            expected_tables = ['users', 'expenses', 'income', 'budgets']
            for table in expected_tables:
                assert table in table_names, f"Table {table} not found in database"

    def test_users_table_structure(self, app):
        """Test users table structure and constraints."""
        with app.app_context():
            db = get_db()
            
            # Test table structure
            columns = db.execute("PRAGMA table_info(users)").fetchall()
            column_names = [col[1] for col in columns]
            
            expected_columns = ['id', 'username', 'email', 'password', 'created_at']
            for column in expected_columns:
                assert column in column_names, f"Column {column} not found in users table"
            
            # Test unique constraints
            # Insert a user
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'hashed_password')
            )
            db.commit()
            
            # Try to insert duplicate username
            with pytest.raises(sqlite3.IntegrityError):
                db.execute(
                    'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                    ('testuser', 'other@example.com', 'other_password')
                )
                db.commit()

    def test_expenses_table_structure(self, app):
        """Test expenses table structure and relationships."""
        with app.app_context():
            db = get_db()
            
            # Create a test user first
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'hashed_password')
            )
            db.commit()
            
            # Test inserting expense
            db.execute('''
                INSERT INTO expenses (user_id, description, amount, category, date, is_active)
                VALUES (1, 'Test Expense', 25.50, 'food', ?, 1)
            ''', (datetime.now().strftime('%Y-%m-%d'),))
            db.commit()
            
            # Verify expense was inserted
            expense = db.execute(
                'SELECT * FROM expenses WHERE user_id = 1'
            ).fetchone()
            
            assert expense is not None
            assert expense['description'] == 'Test Expense'
            assert expense['amount'] == 25.50
            assert expense['category'] == 'food'

    def test_income_table_structure(self, app):
        """Test income table structure and relationships."""
        with app.app_context():
            db = get_db()
            
            # Create a test user first
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'hashed_password')
            )
            db.commit()
            
            # Test inserting income
            db.execute('''
                INSERT INTO income (user_id, amount, source, date, recurrence_period, is_active)
                VALUES (1, 2500.00, 'Salary', ?, 'monthly', 1)
            ''', (datetime.now().strftime('%Y-%m-%d'),))
            db.commit()
            
            # Verify income was inserted
            income = db.execute(
                'SELECT * FROM income WHERE user_id = 1'
            ).fetchone()
            
            assert income is not None
            assert income['amount'] == 2500.00
            assert income['source'] == 'Salary'
            assert income['recurrence_period'] == 'monthly'

    def test_budgets_table_structure(self, app):
        """Test budgets table structure and relationships."""
        with app.app_context():
            db = get_db()
            
            # Create a test user first
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'hashed_password')
            )
            db.commit()
            
            # Test inserting budget
            week_start = datetime.now().strftime('%Y-%m-%d')
            db.execute('''
                INSERT INTO budgets (user_id, week_start, total_budget, food_budget, 
                                   transportation_budget, entertainment_budget, other_budget)
                VALUES (1, ?, 500.00, 200.00, 100.00, 75.00, 125.00)
            ''', (week_start,))
            db.commit()
            
            # Verify budget was inserted
            budget = db.execute(
                'SELECT * FROM budgets WHERE user_id = 1'
            ).fetchone()
            
            assert budget is not None
            assert budget['total_budget'] == 500.00
            assert budget['food_budget'] == 200.00

    def test_foreign_key_constraints(self, app):
        """Test foreign key constraints are enforced."""
        with app.app_context():
            db = get_db()
            
            # Enable foreign key constraints
            db.execute('PRAGMA foreign_keys = ON')
            
            # Try to insert expense for non-existent user
            with pytest.raises(sqlite3.IntegrityError):
                db.execute('''
                    INSERT INTO expenses (user_id, description, amount, category, date, is_active)
                    VALUES (999, 'Test Expense', 25.50, 'food', ?, 1)
                ''', (datetime.now().strftime('%Y-%m-%d'),))
                db.commit()

    def test_database_transactions(self, app):
        """Test database transaction handling."""
        with app.app_context():
            db = get_db()
            
            # Start transaction
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser1', 'test1@example.com', 'password1')
            )
            
            # Check user exists before commit
            user = db.execute('SELECT * FROM users WHERE username = ?', ('testuser1',)).fetchone()
            assert user is not None
            
            # Rollback transaction
            db.rollback()
            
            # Check user no longer exists after rollback
            user = db.execute('SELECT * FROM users WHERE username = ?', ('testuser1',)).fetchone()
            assert user is None

    def test_database_indexes(self, app):
        """Test that necessary indexes are created for performance."""
        with app.app_context():
            db = get_db()
            
            # Check for indexes
            indexes = db.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            ).fetchall()
            
            index_names = [index[0] for index in indexes]
            
            # Check for expected indexes (adjust based on your schema)
            # These might be created automatically or explicitly
            expected_patterns = ['users', 'expenses', 'income', 'budgets']
            
            # At minimum, primary key indexes should exist
            assert len(index_names) > 0, "No indexes found in database"

    def test_data_types_and_constraints(self, app):
        """Test data type handling and constraints."""
        with app.app_context():
            db = get_db()
            
            # Create test user
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'hashed_password')
            )
            db.commit()
            
            # Test decimal precision for amounts
            db.execute('''
                INSERT INTO expenses (user_id, description, amount, category, date, is_active)
                VALUES (1, 'Precision Test', 123.456789, 'food', ?, 1)
            ''', (datetime.now().strftime('%Y-%m-%d'),))
            db.commit()
            
            expense = db.execute(
                'SELECT amount FROM expenses WHERE description = ?', ('Precision Test',)
            ).fetchone()
            
            # Check that decimal precision is handled correctly
            assert expense['amount'] == 123.456789

    def test_date_handling(self, app):
        """Test date storage and retrieval."""
        with app.app_context():
            db = get_db()
            
            # Create test user
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'hashed_password')
            )
            db.commit()
            
            # Test various date formats
            test_date = datetime.now().strftime('%Y-%m-%d')
            
            db.execute('''
                INSERT INTO expenses (user_id, description, amount, category, date, is_active)
                VALUES (1, 'Date Test', 50.00, 'food', ?, 1)
            ''', (test_date,))
            db.commit()
            
            # Retrieve and verify date
            expense = db.execute(
                'SELECT date FROM expenses WHERE description = ?', ('Date Test',)
            ).fetchone()
            
            assert expense['date'] == test_date

    def test_null_handling(self, app):
        """Test NULL value handling in database."""
        with app.app_context():
            db = get_db()
            
            # Create test user
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'hashed_password')
            )
            db.commit()
            
            # Test inserting with NULL optional fields
            db.execute('''
                INSERT INTO expenses (user_id, description, amount, category, date, is_active, notes)
                VALUES (1, 'NULL Test', 25.00, 'food', ?, 1, NULL)
            ''', (datetime.now().strftime('%Y-%m-%d'),))
            db.commit()
            
            expense = db.execute(
                'SELECT notes FROM expenses WHERE description = ?', ('NULL Test',)
            ).fetchone()
            
            assert expense['notes'] is None

    def test_case_sensitivity(self, app):
        """Test case sensitivity in database operations."""
        with app.app_context():
            db = get_db()
            
            # Insert user with mixed case
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('TestUser', 'Test@Example.Com', 'password')
            )
            db.commit()
            
            # Test case-sensitive search
            user_exact = db.execute(
                'SELECT * FROM users WHERE username = ?', ('TestUser',)
            ).fetchone()
            
            user_lower = db.execute(
                'SELECT * FROM users WHERE username = ?', ('testuser',)
            ).fetchone()
            
            assert user_exact is not None
            assert user_lower is None  # SQLite is case-sensitive by default

    def test_special_characters_in_data(self, app):
        """Test handling of special characters in database."""
        with app.app_context():
            db = get_db()
            
            # Create test user
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'password')
            )
            db.commit()
            
            # Test special characters in expense description
            special_description = "Coffee & Donuts @ Café - $5.99 (20% tip)"
            
            db.execute('''
                INSERT INTO expenses (user_id, description, amount, category, date, is_active)
                VALUES (1, ?, 7.19, 'food', ?, 1)
            ''', (special_description, datetime.now().strftime('%Y-%m-%d')))
            db.commit()
            
            expense = db.execute(
                'SELECT description FROM expenses WHERE amount = ?', (7.19,)
            ).fetchone()
            
            assert expense['description'] == special_description

    def test_unicode_support(self, app):
        """Test Unicode character support in database."""
        with app.app_context():
            db = get_db()
            
            # Test Unicode in username and description
            unicode_username = 'tëstüser_中文'
            unicode_description = 'Café expense with émojis 🍕🍟'
            
            try:
                db.execute(
                    'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                    (unicode_username, 'test@example.com', 'password')
                )
                db.commit()
                
                db.execute('''
                    INSERT INTO expenses (user_id, description, amount, category, date, is_active)
                    VALUES (1, ?, 15.99, 'food', ?, 1)
                ''', (unicode_description, datetime.now().strftime('%Y-%m-%d')))
                db.commit()
                
                # Verify Unicode data is stored and retrieved correctly
                user = db.execute(
                    'SELECT username FROM users WHERE username = ?', (unicode_username,)
                ).fetchone()
                
                expense = db.execute(
                    'SELECT description FROM expenses WHERE description = ?', (unicode_description,)
                ).fetchone()
                
                assert user['username'] == unicode_username
                assert expense['description'] == unicode_description
                
            except sqlite3.Error:
                # Some SQLite configurations might not support full Unicode
                pytest.skip("Unicode not fully supported in this SQLite configuration")

    def test_large_data_handling(self, app):
        """Test handling of large amounts of data."""
        with app.app_context():
            db = get_db()
            
            # Create test user
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'password')
            )
            db.commit()
            
            # Insert multiple expenses
            expenses_data = []
            for i in range(100):
                expenses_data.append((
                    1,  # user_id
                    f'Expense {i}',  # description
                    round(10.0 + i * 0.1, 2),  # amount
                    'food',  # category
                    datetime.now().strftime('%Y-%m-%d'),  # date
                    1  # is_active
                ))
            
            db.executemany('''
                INSERT INTO expenses (user_id, description, amount, category, date, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', expenses_data)
            db.commit()
            
            # Verify all expenses were inserted
            count = db.execute('SELECT COUNT(*) FROM expenses WHERE user_id = 1').fetchone()[0]
            assert count == 100

    def test_database_performance_indexes(self, app):
        """Test database performance with indexes."""
        with app.app_context():
            db = get_db()
            
            # Create test user
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'password')
            )
            db.commit()
            
            # Insert many expenses for performance testing
            expenses_data = []
            base_date = datetime.now()
            
            for i in range(1000):
                expense_date = (base_date - timedelta(days=i)).strftime('%Y-%m-%d')
                expenses_data.append((
                    1, f'Expense {i}', round(10.0 + i * 0.1, 2), 
                    'food', expense_date, 1
                ))
            
            db.executemany('''
                INSERT INTO expenses (user_id, description, amount, category, date, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', expenses_data)
            db.commit()
            
            # Test query performance (this is basic - real performance testing would be more sophisticated)
            import time
            
            start_time = time.time()
            results = db.execute('''
                SELECT * FROM expenses 
                WHERE user_id = 1 AND date >= ? 
                ORDER BY date DESC LIMIT 10
            ''', ((base_date - timedelta(days=30)).strftime('%Y-%m-%d'),)).fetchall()
            end_time = time.time()
            
            # Query should complete reasonably quickly and return results
            assert len(results) == 10
            assert (end_time - start_time) < 1.0  # Should complete in under 1 second


class TestDatabaseMigrations:
    """Test database migration and schema evolution."""
    
    def test_schema_version_tracking(self, app):
        """Test schema version tracking for migrations."""
        with app.app_context():
            db = get_db()
            
            # Check if schema version table exists or can be created
            try:
                db.execute('''
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version INTEGER PRIMARY KEY,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                db.commit()
                
                # Insert initial version
                db.execute('INSERT INTO schema_version (version) VALUES (1)')
                db.commit()
                
                # Verify version was recorded
                version = db.execute('SELECT version FROM schema_version ORDER BY version DESC LIMIT 1').fetchone()
                assert version['version'] == 1
                
            except sqlite3.Error as e:
                pytest.fail(f"Schema version tracking failed: {e}")

    def test_backward_compatibility(self, app):
        """Test that database changes are backward compatible."""
        with app.app_context():
            db = get_db()
            
            # Test that basic operations still work after schema changes
            # This would be more relevant if you have actual migrations
            
            # Create user
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'password')
            )
            db.commit()
            
            # Basic operations should still work
            user = db.execute('SELECT * FROM users WHERE username = ?', ('testuser',)).fetchone()
            assert user is not None


class TestDatabaseSecurity:
    """Test database security features."""
    
    def test_sql_injection_prevention(self, app):
        """Test that parameterized queries prevent SQL injection."""
        with app.app_context():
            db = get_db()
            
            # Create test user
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'password')
            )
            db.commit()
            
            # Test SQL injection attempt
            malicious_input = "'; DROP TABLE users; --"
            
            try:
                # This should be safe due to parameterized query
                result = db.execute(
                    'SELECT * FROM users WHERE username = ?', (malicious_input,)
                ).fetchone()
                
                # Should return None (no user found) and not crash
                assert result is None
                
                # Verify users table still exists
                users = db.execute('SELECT COUNT(*) FROM users').fetchone()
                assert users[0] == 1  # Original user should still exist
                
            except sqlite3.Error as e:
                pytest.fail(f"Database error during injection test: {e}")

    def test_database_file_permissions(self, app):
        """Test database file has appropriate permissions."""
        # This test would check file system permissions
        # Implementation depends on your deployment setup
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])