"""Tests for authentication functionality."""

import pytest
from flask import g, session
from db import get_db

class TestAuth:
    """Test cases for authentication."""
    
    def test_register_get(self, client):
        """Test GET request to register page."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Sign Up' in response.data
        
    def test_register_post_success(self, client, app):
        """Test successful user registration."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@uncc.edu',
            'password': 'validpassword',
            'confirm_password': 'validpassword',
            'student_id': '801234567',
            'security_question_1': 'What is your favorite color?',
            'security_answer_1': 'Blue',
            'security_question_2': 'What is your pet\'s name?',
            'security_answer_2': 'Max'
        })
        
        assert response.status_code == 302  # Redirect after successful registration
        
        # Verify user was created in database
        with app.app_context():
            db = get_db()
            user = db.execute('SELECT * FROM users WHERE username = ?', ('newuser',)).fetchone()
            assert user is not None
            assert user['email'] == 'newuser@uncc.edu'
    
    def test_register_validation(self, client):
        """Test registration form validation."""
        # Test missing fields
        response = client.post('/auth/register', data={})
        assert response.status_code == 200
        assert b'This field is required' in response.data or b'required' in response.data
        
        # Test password mismatch
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@uncc.edu',
            'password': 'password1',
            'confirm_password': 'password2',
            'student_id': '801234567'
        })
        assert response.status_code == 200
        
        # Test invalid email domain
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@gmail.com',
            'password': 'validpassword',
            'confirm_password': 'validpassword',
            'student_id': '801234567'
        })
        assert response.status_code == 200
    
    def test_login_get(self, client):
        """Test GET request to login page."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_success(self, client, auth):
        """Test successful login."""
        auth.register()
        response = auth.login()
        assert response.status_code == 302  # Redirect after login
        
        # Test that user is logged in
        with client.session_transaction() as sess:
            assert sess.get('user_id') is not None
    
    def test_login_invalid_credentials(self, client, auth):
        """Test login with invalid credentials."""
        auth.register()
        
        # Wrong password
        response = auth.login(password='wrongpassword')
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'incorrect' in response.data.lower()
        
        # Wrong username
        response = auth.login(username='wronguser')
        assert response.status_code == 200
    
    def test_logout(self, client, auth):
        """Test user logout."""
        auth.register()
        auth.login()
        
        response = auth.logout()
        assert response.status_code == 302
        
        # Test that user is logged out
        with client.session_transaction() as sess:
            assert sess.get('user_id') is None
    
    def test_login_required_decorator(self, client):
        """Test that login_required decorator works."""
        # Try to access protected page without login
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login
        
        response = client.get('/budget')
        assert response.status_code == 302
        
        response = client.get('/transactions')
        assert response.status_code == 302
    
    def test_password_recovery(self, client, auth, app):
        """Test password recovery functionality."""
        auth.register()
        
        # Test GET request
        response = client.get('/auth/forgot-password')
        assert response.status_code == 200
        
        # Test POST with valid username
        response = client.post('/auth/forgot-password', data={
            'username': 'testuser'
        })
        assert response.status_code == 302 or response.status_code == 200
    
    def test_profile_update(self, client, auth, app):
        """Test profile update functionality."""
        auth.register()
        auth.login()
        
        # Test GET request
        response = client.get('/auth/profile')
        assert response.status_code == 200
        
        # Test profile update
        response = client.post('/auth/profile', data={
            'email': 'updated@uncc.edu',
            'student_id': '801234568'
        })
        assert response.status_code == 302 or response.status_code == 200
        
        # Verify update in database
        with app.app_context():
            db = get_db()
            user = db.execute('SELECT * FROM users WHERE username = ?', ('testuser',)).fetchone()
            assert user['email'] == 'updated@uncc.edu'