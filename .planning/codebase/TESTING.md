# Testing

**Generated:** 2026-05-12
**Type:** Codebase Mapping

## Framework

- **Test runner:** pytest
- **Location:** `tests/` directory
- **Config:** Standard pytest config (no `pytest.ini`/`pyproject.toml` found)

## Test Inventory

| File | Type | Tests | Purpose |
|------|------|-------|---------|
| `tests/test_config_loader.py` | Unit | 16 | Config loading, merge, env vars |
| `tests/test_database_connector.py` | Unit | 12 | DB connection, CRUD |
| `tests/test_document_processor.py` | Unit | — | Document chunking |
| `tests/test_embeddings.py` | Unit | — | Embedding API client |
| `tests/test_file_loader.py` | Unit | — | File format loading |
| `tests/test_retriever.py` | Unit | — | Document retrieval |
| `tests/test_vector_store.py` | Unit | — | Vector store operations |
| `tests/test_e2e_rag.py` | Integration | 11 | End-to-end RAG pipeline |
| `tests/test_integration.py` | Integration | — | Cross-module integration |

## Coverage

| Area | Status |
|------|--------|
| Config loader | ✅ Full coverage (16 tests) |
| Database connector | ✅ Full coverage (12 tests) |
| RAG E2E pipeline | ✅ Basic integration (11 tests) |
| LLM module | ❌ No tests |
| Avatar models | ❌ No tests (requires GPU) |
| TTS engines | ❌ No tests |
| Server routes | ❌ No tests |
| Frontend | ❌ No tests |

## Test Patterns

**Unit tests** (e.g., `test_config_loader.py`):
- Mock external dependencies (ChromaDB, APIs)
- Test each function in isolation
- Use pytest fixtures for setup

**Integration tests** (`test_e2e_rag.py`):
- Full RAG pipeline: embed → store → retrieve → prompt build
- Skip with `@pytest.mark.skipif` when env/DashScope unavailable

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_config_loader.py -v

# Skip integration tests
pytest tests/ -v -m "not integration"
```

## Known Gaps

- No LLM unit tests (streaming logic in `llm.py` untested)
- No TTS integration tests (requires network to Microsoft/DashScope)
- No avatar model tests (requires GPU + model files)
- No frontend tests (no Selenium/Playwright setup)
