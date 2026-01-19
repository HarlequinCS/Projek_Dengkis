"""
Unit tests for engine.storage.session_store module.
"""
import pytest

from engine.storage.session_store import SessionStore


class TestSessionStore:
    """Tests for SessionStore class."""
    
    def test_initialization(self, session_store):
        """Test session store initialization."""
        assert session_store.storage_dir.exists()
        assert session_store.json_dir.exists()
    
    def test_save_session(self, session_store, sample_session_data):
        """Test saving session."""
        session_id = session_store.save_session(sample_session_data)
        
        assert session_id == sample_session_data["session_id"]
        assert (session_store.json_dir / f"{session_id}.json").exists()
    
    def test_load_session(self, session_store, sample_session_data):
        """Test loading session."""
        session_id = session_store.save_session(sample_session_data)
        loaded = session_store.load_session(session_id)
        
        assert loaded is not None
        assert loaded["session_id"] == session_id
        assert loaded["target"] == sample_session_data["target"]
    
    def test_load_session_not_found(self, session_store):
        """Test loading non-existent session."""
        loaded = session_store.load_session("non-existent")
        
        assert loaded is None
    
    def test_list_sessions(self, session_store, sample_session_data):
        """Test listing sessions."""
        session_store.save_session(sample_session_data)
        sessions = session_store.list_sessions()
        
        assert len(sessions) >= 1
        assert any(s["session_id"] == sample_session_data["session_id"] for s in sessions)
    
    def test_list_sessions_filtered(self, session_store, sample_session_data):
        """Test listing sessions with target filter."""
        session_store.save_session(sample_session_data)
        sessions = session_store.list_sessions(target="test.example.com")
        
        assert all(s["target"] == "test.example.com" for s in sessions)
    
    def test_compare_sessions(self, session_store, sample_session_data):
        """Test session comparison."""
        session1_data = sample_session_data.copy()
        session2_data = sample_session_data.copy()
        session2_data["session_id"] = "test-session-456"
        session2_data["risk_score"] = 0.7
        
        session1_id = session_store.save_session(session1_data)
        session2_id = session_store.save_session(session2_data)
        
        comparison = session_store.compare_sessions(session1_id, session2_id)
        
        assert "differences" in comparison
        assert "risk_score" in comparison["differences"]
    
    def test_delete_session(self, session_store, sample_session_data):
        """Test deleting session."""
        session_id = session_store.save_session(sample_session_data)
        
        deleted = session_store.delete_session(session_id)
        assert deleted is True
        
        loaded = session_store.load_session(session_id)
        assert loaded is None
