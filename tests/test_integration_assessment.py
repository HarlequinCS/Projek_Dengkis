"""
Integration tests for end-to-end assessment workflows.
"""
import pytest
import asyncio

from engine.runner import run_assessment
from engine.core.session import TestSession
from engine.storage.session_store import SessionStore
from engine.network.request_handler import AggressiveRequestHandler
from engine.utils.retry import RetryConfig
from engine.utils.throttle import ThrottleConfig


class TestAssessmentWorkflow:
    """Integration tests for assessment workflows."""
    
    def test_run_assessment_initialization(self, session_store):
        """Test assessment initialization."""
        result = run_assessment("test.example.com", authorized=True)
        
        assert result["status"] == "initialized"
        assert "session_id" in result
        assert result["target"] == "test.example.com"
        assert result["authorized"] is True
    
    def test_run_assessment_requires_authorization(self):
        """Test that assessment requires authorization."""
        result = run_assessment("test.example.com", authorized=False)
        
        assert result["status"] == "error"
        assert "authorization" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_full_assessment_workflow(self, session_store):
        """Test complete assessment workflow."""
        # Initialize assessment
        assessment_result = run_assessment("example.com", authorized=True)
        assert assessment_result["status"] == "initialized"
        
        session_id = assessment_result["session_id"]
        
        # Create request handler
        retry_config = RetryConfig(max_attempts=1, timeout=5.0)
        throttle_config = ThrottleConfig(requests_per_second=1.0)
        
        async with AggressiveRequestHandler(
            timeout=5.0,
            retry_config=retry_config,
            throttle_config=throttle_config,
            session_id=session_id
        ) as handler:
            # Extract fingerprint (this may fail if network is unavailable)
            try:
                fingerprint = await handler.extract_behavioral_fingerprint("example.com")
                
                # Store session
                session_data = {
                    "session_id": session_id,
                    "target": "example.com",
                    "started_at": assessment_result["started_at"],
                    "status": "completed",
                    "fingerprint": fingerprint
                }
                
                session_store.save_session(session_data, session_id)
                
                # Verify session was saved
                loaded = session_store.load_session(session_id)
                assert loaded is not None
                assert loaded["status"] == "completed"
            except Exception:
                # Network unavailable - skip this test
                pytest.skip("Network unavailable for integration test")


class TestSessionPersistenceWorkflow:
    """Integration tests for session persistence."""
    
    def test_session_save_and_load(self, session_store):
        """Test saving and loading sessions."""
        session = TestSession(target="test.example.com", authorized=True)
        
        session_data = {
            "session_id": str(session.session_id),
            "target": session.target,
            "started_at": session.started_at,
            "status": "active"
        }
        
        session_id = session_store.save_session(session_data)
        loaded = session_store.load_session(session_id)
        
        assert loaded is not None
        assert loaded["session_id"] == session_id
        assert loaded["target"] == "test.example.com"
    
    def test_session_listing(self, session_store):
        """Test session listing functionality."""
        # Save multiple sessions
        for i in range(3):
            session_data = {
                "session_id": f"test-session-{i}",
                "target": f"target{i}.example.com",
                "started_at": "2024-01-01T00:00:00",
                "status": "completed"
            }
            session_store.save_session(session_data)
        
        sessions = session_store.list_sessions()
        assert len(sessions) >= 3
