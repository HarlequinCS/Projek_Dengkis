"""
Unit tests for engine.filters.search module.
"""
import pytest
from datetime import datetime, timedelta

from engine.filters.search import FilterManager, create_filter


class TestFilterManager:
    """Tests for FilterManager class."""
    
    @pytest.fixture
    def filter_manager(self):
        """Create filter manager."""
        return FilterManager()
    
    @pytest.fixture
    def sample_sessions(self):
        """Sample sessions for testing."""
        return [
            {
                'session_id': 'session1',
                'target': 'example.com',
                'status': 'completed',
                'started_at': '2024-01-01T00:00:00',
                'risk_score': 0.5
            },
            {
                'session_id': 'session2',
                'target': 'test.com',
                'status': 'active',
                'started_at': '2024-01-02T00:00:00',
                'risk_score': 0.7
            },
            {
                'session_id': 'session3',
                'target': 'example.com',
                'status': 'completed',
                'started_at': '2024-01-03T00:00:00',
                'risk_score': 0.3
            }
        ]
    
    @pytest.fixture
    def sample_findings(self):
        """Sample findings for testing."""
        return [
            {
                'id': 'finding1',
                'title': 'Missing Headers',
                'severity': 'high',
                'category': 'configuration'
            },
            {
                'id': 'finding2',
                'title': 'Weak TLS',
                'severity': 'medium',
                'category': 'encryption'
            },
            {
                'id': 'finding3',
                'title': 'Information Disclosure',
                'severity': 'low',
                'category': 'information_disclosure'
            }
        ]
    
    def test_filter_by_target(self, filter_manager, sample_sessions):
        """Test filtering by target."""
        filters = {'target': 'example.com'}
        filtered = filter_manager.filter_sessions(sample_sessions, filters)
        
        assert len(filtered) == 2
        assert all(s['target'] == 'example.com' for s in filtered)
    
    def test_filter_by_status(self, filter_manager, sample_sessions):
        """Test filtering by status."""
        filters = {'status': 'completed'}
        filtered = filter_manager.filter_sessions(sample_sessions, filters)
        
        assert len(filtered) == 2
        assert all(s['status'] == 'completed' for s in filtered)
    
    def test_filter_by_severity(self, filter_manager, sample_findings):
        """Test filtering findings by severity."""
        filters = {'severity': 'high'}
        filtered = filter_manager.filter_findings(sample_findings, filters)
        
        assert len(filtered) == 1
        assert filtered[0]['severity'] == 'high'
    
    def test_filter_by_category(self, filter_manager, sample_findings):
        """Test filtering findings by category."""
        filters = {'category': 'configuration'}
        filtered = filter_manager.filter_findings(sample_findings, filters)
        
        assert len(filtered) == 1
        assert filtered[0]['category'] == 'configuration'
    
    def test_filter_by_risk_score(self, filter_manager, sample_sessions):
        """Test filtering by risk score range."""
        filters = {'risk_score': {'min': 0.4, 'max': 0.6}}
        filtered = filter_manager.filter_sessions(sample_sessions, filters)
        
        assert len(filtered) == 1
        assert filtered[0]['session_id'] == 'session1'
    
    def test_fuzzy_search(self, filter_manager, sample_sessions):
        """Test fuzzy search."""
        results = filter_manager.search(sample_sessions, 'example')
        
        assert len(results) == 2
        assert all('example' in s['target'] for s in results)
    
    def test_create_filter(self):
        """Test filter creation helper."""
        filters = create_filter(
            target='example.com',
            status='completed',
            search_query='test'
        )
        
        assert filters['target'] == 'example.com'
        assert filters['status'] == 'completed'
        assert filters['fuzzy_search'] == 'test'
