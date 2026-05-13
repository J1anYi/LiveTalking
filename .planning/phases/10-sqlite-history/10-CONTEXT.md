# Phase 10: SQLite History - Context

**Status:** Auto-generated (smart discuss)
**Requirements:** HIST-01, HIST-02, HIST-03, HIST-04, HIST-05, UI-04

## Scope
- SQLite chat_history module with aiosqlite
- API endpoints for conversation CRUD
- LLM streaming save integration
- Session history loading from DB
- Thread safety (Lock + WAL)

## Files to Create/Modify
- `server/chat_db.py` — NEW: aiosqlite wrapper, schema, CRUD
- `server/routes.py` — ADD: conversation API endpoints
- `llm.py` — MODIFY: save user/assistant messages to DB
- `server/session_manager.py` — MODIFY: add active_conversation tracking
- `app.py` — MODIFY: init ChatHistory on startup
- `requirements.txt` — ADD: aiosqlite>=0.20.0
