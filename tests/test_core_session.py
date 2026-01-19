"""
Unit tests for engine.core.session module.
"""
import pytest
import uuid
from datetime import datetime

from engine.core.session import TestSession


class TestTestSession:
    """Tests for TestSession class."""
    
    def test_session_initialization(self):
        """Test session initialization."""
        session = TestSession(target="test.example.com", authorized=True)
        
        assert session.target == "test.example.com"
        assert session.authorized is True
        assert isinstance(session.session_id, uuid.UUID)
        assert isinstance(session.started_at, str)
    
    def test_add_test_vector(self, test_session):
        """Test adding test vector."""
        vector = {"type": "http_probe", "path": "/"}
        test_session.add_test_vector(vector)
        
        assert len(test_session.test_vectors) == 1
        assert "timestamp" in test_session.test_vectors[0]
    
    def test_record_response_pattern(self, test_session):
        """Test recording response pattern."""
        pattern_data = {"response_time": 0.5, "status_code": 200}
        test_session.record_response_pattern("timing", pattern_data)
        
        assert "timing" in test_session.response_patterns
        assert len(test_session.response_patterns["timing"]) == 1
    
    def test_add_anomaly_indicator(self, test_session):
        """Test adding anomaly indicator."""
        indicator = {"type": "slow_response", "severity": "low"}
        test_session.add_anomaly_indicator(indicator)
        
        assert len(test_session.anomaly_indicators) == 1
        assert "timestamp" in test_session.anomaly_indicators[0]
    
    def test_get_status(self, test_session):
        """Test getting session status."""
        status = test_session.get_status()
        
        assert "session_id" in status
        assert "target" in status
        assert "authorized" in status
        assert status["target"] == "test.example.com"
    
    def test_behavioral_fingerprint(self, test_session):
        """Test behavioral fingerprint generation."""
        fingerprint = test_session.behavioral_fingerprint()
        
        assert "target" in fingerprint
        assert "session_id" in fingerprint
        assert "response_characteristics" in fingerprint
        assert fingerprint["target"] == "test.example.com"
    
    def test_analyze_response_patterns(self, test_session):
        """Test response pattern analysis."""
        test_session.add_test_vector({"type": "test"})
        analysis = test_session.analyze_response_patterns()
        
        assert "patterns_identified" in analysis
        assert "anomalies_detected" in analysis
    
    def test_comparative_security_metrics(self, test_session):
        """Test security metrics generation."""
        metrics = test_session.comparative_security_metrics()
        
        assert "target" in metrics
        assert "session_id" in metrics
        assert "security_score" in metrics
    
    def test_technical_debt_assessment(self, test_session):
        """Test technical debt assessment."""
        assessment = test_session.technical_debt_assessment()
        
        assert "target" in assessment
        assert "debt_score" in assessment
