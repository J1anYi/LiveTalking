# Testing

**Analysis Date:** 2026-05-11

## Test Framework

**Current Status:** No test framework is configured.

The codebase does not include any testing infrastructure:
- No test files found (`test_*.py` or `*_test.py`)
- No `tests/` directory
- No test dependencies in `requirements.txt` (e.g., pytest, unittest, mock)
- No test configuration files (e.g., `pytest.ini`, `setup.cfg`, `pyproject.toml` test sections)

**Recommendation:** Adopt `pytest` as the testing framework:
- Industry standard for Python testing
- Rich plugin ecosystem (pytest-asyncio, pytest-cov, pytest-mock)
- Simple assertion syntax
- Excellent fixture system for complex setup

## Test Coverage

**Current Status:** 0% - No tests exist.

**Recommended Coverage Targets:**

| Component | Target Coverage | Priority |
|-----------|-----------------|----------|
| `utils/audio.py` | 80% | High - Pure functions, easy to test |
| `utils/image.py` | 80% | High - Pure functions, easy to test |
| `utils/device.py` | 70% | Medium - Device detection logic |
| `registry.py` | 90% | High - Core plugin system |
| `server/routes.py` | 70% | Medium - API handlers (use fixtures) |
| `server/session_manager.py` | 70% | Medium - Session lifecycle |
| `tts/base_tts.py` | 60% | Medium - Abstract base class |
| `streamout/base_output.py` | 60% | Medium - Abstract base class |
| `avatars/base_avatar.py` | 50% | Low - Complex, needs mocking |

## Test Locations

**Recommended Structure:**
```
LiveTalking/
  tests/
    conftest.py           # Shared fixtures
    test_utils/
      __init__.py
      test_audio.py       # Tests for utils/audio.py
      test_image.py       # Tests for utils/image.py
      test_device.py      # Tests for utils/device.py
    test_registry.py      # Tests for registry.py
    test_server/
      __init__.py
      test_routes.py      # Tests for server/routes.py
      test_session_manager.py
    test_tts/
      __init__.py
      test_base_tts.py    # Tests for TTS base class
    test_streamout/
      __init__.py
      test_base_output.py
```

## Running Tests

**Recommended Commands:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_registry.py

# Run tests matching pattern
pytest -k "audio"

# Run with verbose output
pytest -v

# Run async tests (requires pytest-asyncio)
pytest --asyncio-mode=auto
```

**Test Dependencies to Add:**
```
# requirements-dev.txt (create new file)
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
aioresponses>=0.7.0   # For mocking aiohttp requests
```

## Testing Recommendations

### 1. Start with Utility Functions

The `utils/` module contains pure functions ideal for initial testing:

**Example: `test_utils/test_audio.py`**
```python
import numpy as np
from utils.audio import pcm_to_float32, float32_to_pcm, resample_audio

def test_pcm_to_float32_int16():
    # Test int16 PCM conversion
    pcm = np.array([0, 32767, -32768], dtype=np.int16).tobytes()
    result = pcm_to_float32(pcm, sample_width=2)
    expected = np.array([0.0, 1.0, -1.0], dtype=np.float32)
    np.testing.assert_array_almost_equal(result, expected)

def test_float32_to_pcm_roundtrip():
    # Test conversion roundtrip
    original = np.array([0.5, -0.5, 0.0], dtype=np.float32)
    pcm = float32_to_pcm(original, sample_width=2)
    result = pcm_to_float32(pcm, sample_width=2)
    np.testing.assert_array_almost_equal(result, original, decimal=4)
```

**Example: `test_utils/test_image.py`**
```python
from utils.image import mirror_index

def test_mirror_index_first_cycle():
    assert mirror_index(10, 0) == 0
    assert mirror_index(10, 5) == 5
    assert mirror_index(10, 9) == 9

def test_mirror_index_second_cycle():
    # Second cycle should reverse
    assert mirror_index(10, 10) == 9
    assert mirror_index(10, 15) == 4
    assert mirror_index(10, 19) == 0

def test_mirror_index_third_cycle():
    # Third cycle should forward again
    assert mirror_index(10, 20) == 0
    assert mirror_index(10, 25) == 5
```

### 2. Test Plugin Registry

**Example: `test_registry.py`**
```python
import pytest
import registry

def setup_function():
    # Clear registry before each test
    registry._REGISTRY["test"] = {}

def test_register_decorator():
    @registry.register("test", "mock")
    class MockPlugin:
        pass
    
    assert "mock" in registry._REGISTRY["test"]
    assert registry._REGISTRY["test"]["mock"] is MockPlugin

def test_create_instance():
    @registry.register("test", "mock2")
    class MockPlugin2:
        def __init__(self, value):
            self.value = value
    
    instance = registry.create("test", "mock2", value=42)
    assert instance.value == 42

def test_create_unknown_plugin():
    with pytest.raises(ValueError, match="Plugin 'unknown' not found"):
        registry.create("test", "unknown")

def test_list_plugins():
    registry._REGISTRY["test"] = {"a": object, "b": object}
    result = registry.list_plugins("test")
    assert result == {"test": ["a", "b"]}
```

### 3. Test API Routes with Fixtures

**Example: `test_server/test_routes.py`**
```python
import pytest
from aiohttp import web
from server.routes import setup_routes, json_ok, json_error

@pytest.fixture
def app():
    app = web.Application()
    setup_routes(app)
    return app

@pytest.fixture
async def client(aiohttp_client, app):
    return await aiohttp_client(app)

async def test_json_ok():
    response = json_ok({"key": "value"})
    assert response.status == 200
    # Additional assertions...

async def test_json_error():
    response = json_error("test error", code=-1)
    assert response.status == 200
    # Additional assertions...
```

### 4. Test Async Components

Use `pytest-asyncio` for async testing:

**Example:**
```python
import pytest
from server.session_manager import SessionManager

@pytest.mark.asyncio
async def test_create_session():
    manager = SessionManager()
    manager.init_builder(lambda sid, p: f"avatar_{sid}")
    
    session_id = await manager.create_session({"param": "value"})
    assert session_id is not None
    
    session = manager.get_session(session_id)
    assert session is not None
```

### 5. Mock External Dependencies

For TTS and external services, use mocking:

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_edge_tts():
    with patch('edge_tts.Communicate') as mock_comm:
        mock_instance = MagicMock()
        mock_instance.stream = AsyncMock(return_value=[
            {"type": "audio", "data": b"test_audio"}
        ])
        mock_comm.return_value = mock_instance
        
        # Test TTS implementation
```

### 6. Integration Tests

Create a separate marker for slow integration tests:

```python
# conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )

# test_integration.py
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_pipeline():
    # Test complete pipeline with real components
    pass
```

### 7. Test Configuration

Create `pytest.ini`:
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### 8. CI/CD Integration

Add to GitHub Actions workflow:
```yaml
- name: Run tests
  run: |
    pip install pytest pytest-asyncio pytest-cov
    pytest --cov=. --cov-report=xml
  
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Test Priority Order

1. **High Priority (Start Here)**
   - `utils/audio.py` - Pure functions, no external dependencies
   - `utils/image.py` - Pure functions, simple logic
   - `registry.py` - Core system, easy to test

2. **Medium Priority**
   - `server/session_manager.py` - Singleton pattern, needs care
   - `server/routes.py` - API handlers, requires aiohttp fixtures
   - Base classes (`base_tts.py`, `base_output.py`)

3. **Low Priority**
   - Avatar implementations (require heavy mocking: models, GPU, etc.)
   - TTS implementations (require mocking external services)
   - WebRTC components (complex async interactions)

## Testing Challenges

**1. GPU Dependencies**
- Avatar models require CUDA/MPS
- Use `pytest.mark.skipif` for GPU-dependent tests
- Consider mock implementations for CI

**2. External Services**
- TTS services (Edge TTS, Azure, etc.)
- LLM APIs (OpenAI, Qwen)
- Use `aioresponses` or `responses` library for HTTP mocking

**3. Audio/Video Processing**
- Requires test fixtures (audio files, video frames)
- Create `tests/fixtures/` directory with sample files

**4. Async/Threading**
- Mix of asyncio and threading
- Use `pytest-asyncio` for async tests
- Be careful with thread synchronization in tests

---

*Testing analysis: 2026-05-11*
