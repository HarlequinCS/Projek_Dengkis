"""
Pytest configuration and fixtures for PROJEK DENGKIS tests.
"""
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
import sys
from typing import Generator

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.core.session import TestSession
from engine.config.manager import ConfigManager
from engine.storage.session_store import SessionStore


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_session():
    """Create test session."""
    return TestSession(target="test.example.com", authorized=True)


@pytest.fixture
def config_manager(temp_dir):
    """Create config manager with temp directory."""
    config_dir = temp_dir / "config"
    config_dir.mkdir()
    return ConfigManager(config_dir=str(config_dir))


@pytest.fixture
def session_store(temp_dir):
    """Create session store with temp directory."""
    storage_dir = temp_dir / "storage"
    return SessionStore(storage_dir=str(storage_dir))


@pytest.fixture
def mock_httpx_response():
    """Create mock httpx response."""
    response = Mock()
    response.status_code = 200
    response.headers = {"Server": "nginx/1.18.0", "Content-Type": "text/html"}
    response.content = b"<html>Test</html>"
    response.text = "<html>Test</html>"
    response.json.return_value = {}
    return response


@pytest.fixture
def sample_findings():
    """Sample findings for testing."""
    return [
        {
            "id": "finding_1",
            "title": "Missing Security Headers",
            "severity": "medium",
            "category": "configuration",
            "description": "Missing X-Frame-Options header",
            "recommendation": "Add security headers"
        },
        {
            "id": "finding_2",
            "title": "Weak TLS Configuration",
            "severity": "high",
            "category": "encryption",
            "description": "TLS 1.0 detected",
            "recommendation": "Upgrade to TLS 1.2+"
        },
        {
            "id": "finding_3",
            "title": "Information Disclosure",
            "severity": "low",
            "category": "information_disclosure",
            "description": "Server version disclosed",
            "recommendation": "Suppress server version"
        }
    ]


@pytest.fixture
def sample_session_data():
    """Sample session data for testing."""
    return {
        "session_id": "test-session-123",
        "target": "test.example.com",
        "started_at": "2024-01-01T00:00:00",
        "status": "completed",
        "findings": [],
        "risk_score": 0.5
    }
