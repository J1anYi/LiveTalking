# Conventions

**Generated:** 2026-05-12
**Type:** Codebase Mapping

## Code Style

- **Language:** Python 3.10+, currently running 3.13
- **Formatting:** PEP 8, 4-space indentation
- **Imports:** Standard library → third-party → local (grouped with blank lines)
- **Line length:** Varies (no strict limit enforced by tooling)
- **Type hints:** Used in new code (`BaseAvatar`, `AudioFrameData`, `NDArray[np.float32]`)
- **Docstrings:** Used for public APIs (`build_rag_prompt()`, `register()`), minimal for internals
- **Logging:** Custom `utils.logger` wraps logging with `INFO`/`DEBUG`/`ERROR`/`WARNING`, prefix `[module_name]`

## Commenting

- Functions start with brief comment describing purpose (English or Chinese)
- `# ─── Section headers ───` used in larger files for section demarcation
- `# Task N: ...` comments in summary implementations
- Inline comments for non-obvious logic (e.g., `# 降低阈值，更快发送`)

## Error Handling

| Pattern | Usage | Example File |
|---------|-------|-------------|
| `try/except` + `logger.exception()` | Top-level exception catch-all | `llm.py:167`, `edge.py:75` |
| `try/except` + `logger.warning()` | Non-fatal failures (e.g., RAG fail) | `llm.py:116` |
| JSON error responses | All API endpoints use `json_error()` | `server/routes.py:26` |
| Queue timeout + continue | Thread loops use `queue.get(timeout=1)` + `continue` | `base_avatar.py:324` |

## Concurrency Patterns

- **Threads:** `Thread(target=..., args=(quit_event,))` with `Event` for signaling
- **Async:** `asyncio` via aiohttp, `run_in_executor()` for blocking operations
- **Queues:** `queue.Queue` / `queue.Empty` for cross-thread data transfer
- **Event Loop:** Each TTS call creates its own via `asyncio.new_event_loop().run_until_complete()`
- **Multiprocessing:** `torch.multiprocessing` for inference (avoid GIL)

## Plugin Development Pattern

```python
from registry import register
from .base_tts import BaseTTS

@register("tts", "mytts")
class MyTTS(BaseTTS):
    def txt_to_audio(self, msg: tuple[str, dict]):
        # Process text → audio frames
        # Call self.parent.put_audio_frame() for each chunk
        pass
```

New plugins **auto-register** when the file is imported (`app.py` imports all TTS modules).

## Git Conventions

- **Branch:** `main` only
- **Commit prefix:** `feat()`, `fix()`, `docs()`, `test()`, `chore`
- **Scope:** Phase number or subsystem (e.g., `feat(08):`, `fix(llm):`)
- **Commit style:** Conventional Commits (`type(scope): description`)

## RAG Config Merge Order

```
CLI args (highest priority) > Env vars > YAML file (lowest priority)
```
