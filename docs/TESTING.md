# PROJEK DENGKIS - Testing Guide

## Overview

PROJEK DENGKIS uses pytest for unit and integration testing with async support.

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=engine --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_core_session.py
```

### Run specific test
```bash
pytest tests/test_core_session.py::TestTestSession::test_session_initialization
```

### Run async tests
```bash
pytest --asyncio-mode=auto
```

## Test Structure

- `tests/conftest.py` - Pytest configuration and fixtures
- `tests/test_core_*.py` - Unit tests for core modules
- `tests/test_integration_*.py` - Integration tests
- `tests/test_storage_*.py` - Storage tests
- `tests/test_filters.py` - Filter/search tests

## Coverage

Generate coverage reports:
```bash
pytest --cov=engine --cov-report=html --cov-report=term
```

View coverage report:
```bash
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows
```

## Writing Tests

### Unit Test Example
```python
def test_session_initialization(test_session):
    assert test_session.target == "test.example.com"
    assert test_session.authorized is True
```

### Async Test Example
```python
@pytest.mark.asyncio
async def test_network_request():
    async with AggressiveRequestHandler() as handler:
        result = await handler.extract_behavioral_fingerprint("example.com")
        assert result is not None
```

## Test Fixtures

Available fixtures:
- `test_session` - Test session object
- `config_manager` - Config manager with temp directory
- `session_store` - Session store with temp directory
- `temp_dir` - Temporary directory for tests
- `sample_findings` - Sample findings data
- `sample_session_data` - Sample session data
