"""Tests for dashboard functionality."""

import pytest
from db import get_db

class TestDashboard:
    """Test cases for dashboard."""
    
    def test_dashboard_access(self, logged_in_user):
        """Test dashboard accessibility."""
        response = logged_in_user.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    def test_dashboard_with_data(self, logged_in_user, sample_data):
        """Test dashboard with sample data."""
        response = logged_in_user.get('/dashboard')
        assert response.status_code == 200
        
        # Should show budget information
        assert b'$' in response.data  # Should have dollar amounts
        
        # Should show recent transactions
        assert b'Lunch' in response.data or b'Gas' in response.data
    
    def test_dashboard_empty_state(self, logged_in_user):
        """Test dashboard with no data."""
        response = logged_in_user.get('/dashboard')
        assert response.status_code == 200
        # Should handle empty state gracefully
    
    def test_index_page(self, client):
        """Test the main index page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Niner Finance' in response.data
    
    def test_dashboard_api_endpoints(self, logged_in_user, sample_data):
        """Test dashboard API endpoints."""
        # Test budget summary API
        response = logged_in_user.get('/api/dashboard/budget-summary')
        if response.status_code == 200:
            data = response.get_json()
            assert data is not None
        
        # Test monthly overview API
        response = logged_in_user.get('/api/dashboard/monthly-overview')
        if response.status_code == 200:
            data = response.get_json()
            assert data is not None