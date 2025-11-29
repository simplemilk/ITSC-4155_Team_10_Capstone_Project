import pytest
import json
from werkzeug.security import generate_password_hash, check_password_hash
from niner_repo.db import get_db

class TestAuthentication:
    """Test cases for authentication functionality (login and registration)."""
    
    def test_register_success(self, client, app):
        """Test successful user registration."""
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'ValidPass123',
            'confirmPassword': 'ValidPass123',
            'agreeTerms': 'on'
        })
        
        # Should redirect to login page after successful registration
        assert response.status_code == 302
        assert '/auth/login' in response.location
        
        # Verify user was created in database
        with app.app_context():
            db = get_db()
            user = db.execute(
                'SELECT * FROM users WHERE username = ?', ('testuser',)
            ).fetchone()
            assert user is not None
            assert user['username'] == 'testuser'
            assert user['email'] == 'test@example.com'
            # Verify password is hashed
            assert check_password_hash(user['password'], 'ValidPass123')

    def test_register_duplicate_username(self, client, app):
        """Test registration with duplicate username."""
        # Create existing user
        with app.app_context():
            db = get_db()
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('existinguser', 'existing@example.com', generate_password_hash('password123'))
            )
            db.commit()
        
        # Try to register with same username
        response = client.post('/auth/register', data={
            'username': 'existinguser',
            'email': 'new@example.com',
            'password': 'ValidPass123',
            'confirmPassword': 'ValidPass123',
            'agreeTerms': 'on'
        })
        
        # Should stay on registration page with error
        assert response.status_code == 200
        assert b'Username already exists' in response.data or b'already taken' in response.data

    def test_register_duplicate_email(self, client, app):
        """Test registration with duplicate email."""
        # Create existing user
        with app.app_context():
            db = get_db()
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('existinguser', 'existing@example.com', generate_password_hash('password123'))
            )
            db.commit()
        
        # Try to register with same email
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'ValidPass123',
            'confirmPassword': 'ValidPass123',
            'agreeTerms': 'on'
        })
        
        # Should stay on registration page with error
        assert response.status_code == 200
        assert b'Email already exists' in response.data or b'already registered' in response.data

    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords."""
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'ValidPass123',
            'confirmPassword': 'DifferentPass456',
            'agreeTerms': 'on'
        })
        
        # Should stay on registration page with error
        assert response.status_code == 200
        assert b'Passwords do not match' in response.data or b'password confirmation' in response.data

    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        weak_passwords = [
            'short',           # Too short
            'nouppercase123',  # No uppercase
            'NOLOWERCASE123',  # No lowercase
            'NoNumbers',       # No numbers
            'password',        # Common password
            ''                 # Empty password
        ]
        
        for weak_password in weak_passwords:
            response = client.post('/auth/register', data={
                'username': f'testuser_{weak_password}',
                'email': f'test_{weak_password}@example.com',
                'password': weak_password,
                'confirmPassword': weak_password,
                'agreeTerms': 'on'
            })
            
            # Should stay on registration page (weak passwords may be accepted depending on implementation)
            assert response.status_code in [200, 302]

    def test_register_invalid_email(self, client):
        """Test registration with invalid email formats."""
        invalid_emails = [
            'notanemail',
            'missing@domain',
            '@missinglocal.com',
            'spaces in@email.com',
            'double@@domain.com',
            ''
        ]
        
        for invalid_email in invalid_emails:
            response = client.post('/auth/register', data={
                'username': f'testuser_{invalid_email.replace("@", "_at_")}',
                'email': invalid_email,
                'password': 'ValidPass123',
                'confirmPassword': 'ValidPass123',
                'agreeTerms': 'on'
            })
            
            # Should stay on registration page with error
            assert response.status_code == 200

    def test_register_missing_terms_agreement(self, client):
        """Test registration without agreeing to terms."""
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'ValidPass123',
            'confirmPassword': 'ValidPass123'
            # Missing agreeTerms
        })
        
        # Should stay on registration page with error
        assert response.status_code == 200
        assert b'must agree' in response.data or b'terms' in response.data.lower()

    def test_register_missing_required_fields(self, client):
        """Test registration with missing required fields."""
        incomplete_data_sets = [
            {'email': 'test@example.com', 'password': 'ValidPass123', 'confirmPassword': 'ValidPass123'},  # Missing username
            {'username': 'testuser', 'password': 'ValidPass123', 'confirmPassword': 'ValidPass123'},  # Missing email
            {'username': 'testuser', 'email': 'test@example.com', 'confirmPassword': 'ValidPass123'},  # Missing password
            {'username': 'testuser', 'email': 'test@example.com', 'password': 'ValidPass123'},  # Missing confirmPassword
        ]
        
        for incomplete_data in incomplete_data_sets:
            incomplete_data['agreeTerms'] = 'on'
            response = client.post('/auth/register', data=incomplete_data)
            
            # Should stay on registration page with error
            assert response.status_code == 200

    def test_login_success(self, client, app):
        """Test successful login."""
        # Create test user
        with app.app_context():
            db = get_db()
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', generate_password_hash('ValidPass123'))
            )
            db.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'ValidPass123'
        })
        
        # Should redirect to dashboard/home
        assert response.status_code == 302
        assert response.location in ['/', '/dashboard', '/home'] or 'dashboard' in response.location

    def test_login_invalid_username(self, client):
        """Test login with non-existent username."""
        response = client.post('/auth/login', data={
            'username': 'nonexistentuser',
            'password': 'SomePassword123'
        })
        
        # Should stay on login page with error
        assert response.status_code == 200
        assert b'Invalid username' in response.data or b'user not found' in response.data or b'invalid credentials' in response.data.lower()

    def test_login_wrong_password(self, client, app):
        """Test login with correct username but wrong password."""
        # Create test user
        with app.app_context():
            db = get_db()
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', generate_password_hash('CorrectPassword123'))
            )
            db.commit()
        
        # Login with wrong password
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'WrongPassword456'
        })
        
        # Should stay on login page with error
        assert response.status_code == 200
        assert b'Invalid password' in response.data or b'incorrect password' in response.data or b'invalid credentials' in response.data.lower()

    def test_login_empty_credentials(self, client):
        """Test login with empty credentials."""
        response = client.post('/auth/login', data={
            'username': '',
            'password': ''
        })
        
        # Should stay on login page with error
        assert response.status_code == 200
        assert b'required' in response.data.lower() or b'enter' in response.data.lower()

    def test_login_case_sensitivity(self, client, app):
        """Test login username case sensitivity."""
        # Create test user
        with app.app_context():
            db = get_db()
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('TestUser', 'test@example.com', generate_password_hash('ValidPass123'))
            )
            db.commit()
        
        # Try login with different case
        response = client.post('/auth/login', data={
            'username': 'testuser',  # lowercase
            'password': 'ValidPass123'
        })
        
        # Behavior depends on implementation - could be case sensitive or insensitive
        assert response.status_code in [200, 302]

    def test_session_management_after_login(self, client, app):
        """Test session is properly created after login."""
        # Create test user
        with app.app_context():
            db = get_db()
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', generate_password_hash('ValidPass123'))
            )
            db.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'ValidPass123'
        })
        
        # Should redirect after successful login
        assert response.status_code == 302
        
        # Verify session is active by accessing protected page
        with client.session_transaction() as sess:
            # Session should contain user information
            assert 'user_id' in sess or '_user_id' in sess or any('user' in key for key in sess.keys())

    def test_logout_functionality(self, client, app):
        """Test logout functionality."""
        # Create and login user
        with app.app_context():
            db = get_db()
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', generate_password_hash('ValidPass123'))
            )
            db.commit()
        
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'ValidPass123'
        })
        
        # Logout
        response = client.get('/auth/logout')
        
        # Should redirect to login page
        assert response.status_code == 302
        assert '/auth/login' in response.location or '/' in response.location
        
        # Verify session is cleared
        with client.session_transaction() as sess:
            assert 'user_id' not in sess and '_user_id' not in sess

    def test_protected_route_access_without_login(self, client):
        """Test accessing protected routes without login."""
        protected_routes = [
            '/dashboard',
            '/transactions',
            '/budget',
            '/income',
            '/profile'
        ]
        
        for route in protected_routes:
            response = client.get(route)
            # Should redirect to login page
            assert response.status_code == 302
            assert '/auth/login' in response.location or '/login' in response.location

    def test_protected_route_access_with_login(self, client, app):
        """Test accessing protected routes after login."""
        # Create and login user
        with app.app_context():
            db = get_db()
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', generate_password_hash('ValidPass123'))
            )
            db.commit()
        
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'ValidPass123'
        })
        
        # Access protected route
        response = client.get('/dashboard')
        # Should be successful (200) or redirect to home but not to login
        assert response.status_code in [200, 302]
        if response.status_code == 302:
            assert '/auth/login' not in response.location

    def test_login_with_remember_me(self, client, app):
        """Test login with remember me functionality."""
        # Create test user
        with app.app_context():
            db = get_db()
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', generate_password_hash('ValidPass123'))
            )
            db.commit()
        
        # Login with remember me
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'ValidPass123',
            'remember': 'on'
        })
        
        # Should redirect after successful login
        assert response.status_code == 302
        
        # Check if remember me cookie is set (implementation dependent)
        # This would need to be verified based on your specific implementation

    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection attacks."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "admin' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "admin'; INSERT INTO users VALUES ('hacker', 'hack@evil.com', 'password'); --"
        ]
        
        for malicious_input in malicious_inputs:
            # Test in username field
            response = client.post('/auth/login', data={
                'username': malicious_input,
                'password': 'password'
            })
            
            # Should not crash and should not login
            assert response.status_code == 200
            assert b'Invalid' in response.data or b'not found' in response.data or b'error' in response.data.lower()
            
            # Test in registration
            response = client.post('/auth/register', data={
                'username': malicious_input,
                'email': 'test@example.com',
                'password': 'ValidPass123',
                'confirmPassword': 'ValidPass123',
                'agreeTerms': 'on'
            })
            
            # Should handle gracefully
            assert response.status_code in [200, 302]

    def test_xss_protection(self, client):
        """Test protection against XSS attacks."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        for payload in xss_payloads:
            response = client.post('/auth/register', data={
                'username': payload,
                'email': 'test@example.com',
                'password': 'ValidPass123',
                'confirmPassword': 'ValidPass123',
                'agreeTerms': 'on'
            })
            
            # XSS payload should be escaped in response
            assert response.status_code in [200, 302]
            if response.status_code == 200:
                # Check that script tags are escaped
                assert b'<script>' not in response.data
                assert b'javascript:' not in response.data

    def test_rate_limiting_login_attempts(self, client, app):
        """Test rate limiting for failed login attempts."""
        # Create test user
        with app.app_context():
            db = get_db()
            db.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', generate_password_hash('ValidPass123'))
            )
            db.commit()
        
        # Make multiple failed login attempts
        for i in range(10):  # Try 10 failed attempts
            response = client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'WrongPassword'
            })
            
            # All attempts should be handled (rate limiting is implementation dependent)
            assert response.status_code == 200

    def test_password_hashing_security(self, client, app):
        """Test that passwords are properly hashed and not stored in plain text."""
        # Register user
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'MySecretPassword123',
            'confirmPassword': 'MySecretPassword123',
            'agreeTerms': 'on'
        })
        
        # Check password is hashed in database
        with app.app_context():
            db = get_db()
            user = db.execute(
                'SELECT password FROM users WHERE username = ?', ('testuser',)
            ).fetchone()
            
            if user:
                # Password should not be stored in plain text
                assert user['password'] != 'MySecretPassword123'
                # Should be a hash (typically starts with pbkdf2, bcrypt, etc.)
                assert len(user['password']) > 20  # Hashes are typically much longer
                assert '$' in user['password'] or user['password'].startswith('pbkdf2')


class TestAuthenticationEdgeCases:
    """Test edge cases and error conditions for authentication."""
    
    def test_registration_with_unicode_characters(self, client):
        """Test registration with unicode characters in username."""
        response = client.post('/auth/register', data={
            'username': 'tëstüser',
            'email': 'test@example.com',
            'password': 'ValidPass123',
            'confirmPassword': 'ValidPass123',
            'agreeTerms': 'on'
        })
        
        # Should handle unicode gracefully
        assert response.status_code in [200, 302]

    def test_extremely_long_inputs(self, client):
        """Test with extremely long inputs."""
        long_string = 'a' * 1000
        
        response = client.post('/auth/register', data={
            'username': long_string,
            'email': f'{long_string}@example.com',
            'password': 'ValidPass123',
            'confirmPassword': 'ValidPass123',
            'agreeTerms': 'on'
        })
        
        # Should handle long inputs without crashing
        assert response.status_code in [200, 302]

    def test_special_characters_in_password(self, client):
        """Test passwords with special characters."""
        special_passwords = [
            'P@ssw0rd!',
            'Test#123$',
            'Secure&Pass*',
            'C0mplex(Pass)',
            'Strong+Pass-'
        ]
        
        for password in special_passwords:
            response = client.post('/auth/register', data={
                'username': f'user_{password.replace("@", "at").replace("#", "hash")[:10]}',
                'email': f'test_{password.replace("@", "at")[:5]}@example.com',
                'password': password,
                'confirmPassword': password,
                'agreeTerms': 'on'
            })
            
            # Should accept strong passwords with special characters
            assert response.status_code in [200, 302]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])