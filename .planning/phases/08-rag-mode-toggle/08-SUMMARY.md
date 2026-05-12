---
phase: 08
plan: 01
subsystem: llm, api, frontend
tags:
  - rag
  - mode-toggle
  - ux
requires:
  - rag-module
provides:
  - rag-mode-switching
  - rag-plus-model-mode
affects:
  - llm.py
  - server/routes.py
  - server/session_manager.py
  - web/dashboard.html
tech-stack:
  added:
    - rag_mode state tracking
    - /set_rag_mode API
    - /get_rag_mode API
  patterns:
    - per-session state management
    - localStorage persistence
key-files:
  created: []
  modified:
    - llm.py
    - server/routes.py
    - server/session_manager.py
    - web/dashboard.html
decisions:
  - Use per-session RAG mode tracking in SessionManager
  - Persist UI selection in localStorage
  - RAG+Model mode uses KB as reference context
metrics:
  duration: 15 minutes
  tasks_completed: 4
  files_modified: 4
  completed_date: 2026-05-12
---

# Phase 8 Plan 01: RAG Mode Toggle Implementation Summary

## One-liner

Added RAG mode switching functionality supporting "RAG-only" and "RAG+Model" modes with per-session tracking, API endpoints, and UI controls.

## Tasks Completed

| Task | Description | Status | Commit |
|------|-------------|--------|--------|
| 1 | Add RAG mode state to SessionManager | Done | 716b69e |
| 2 | Add /set_rag_mode API endpoint | Done | 0ee5bd4 |
| 3 | Update llm.py for RAG+Model mode | Done | 5e42228 |
| 4 | Add RAG mode toggle to dashboard.html | Done | f7cbb7c |

## Changes Made

### Task 1: SessionManager State (716b69e)

- Added `rag_modes: Dict[str, str]` to track per-session RAG mode
- Added `set_rag_mode(sessionid, mode)` method with validation
- Added `get_rag_mode(sessionid)` method returning "rag_only" by default

### Task 2: API Endpoints (0ee5bd4)

- Added `POST /set_rag_mode` endpoint to set mode per session
- Added `POST /get_rag_mode` endpoint to query current mode
- Both endpoints return standard JSON response format

### Task 3: LLM Integration (5e42228)

- Imported `session_manager` for mode lookup
- Added `rag_mode = session_manager.get_rag_mode(avatar_session.sessionid)`
- Implemented conditional prompt building:
  - `rag_only`: Uses `build_rag_prompt()` (original behavior)
  - `rag_plus_model`: Formats KB content as reference context

### Task 4: Frontend UI (f7cbb7c)

- Added radio button group in settings panel for mode selection
- JavaScript handler calls `/set_rag_mode` API on change
- Mode persisted to `localStorage` for page refresh persistence
- Mode restored from `localStorage` on page load

## Verification

### must_haves Checklist

- [x] Dashboard displays RAG mode toggle button
- [x] LLM uses correct mode after switching
- [x] Mode persists after page refresh
- [x] API endpoints `/set_rag_mode` and `/get_rag_mode` work correctly

## Deviations from Plan

None - plan executed exactly as written.

## Key Decisions

1. **Per-session tracking**: RAG mode stored per session ID, allowing different modes for different users/sessions
2. **localStorage persistence**: Frontend persists mode choice locally, restoring on page load
3. **RAG+Model prompt format**: Uses "参考信息:\n{context}\n\n用户问题: {message}\n\n请结合参考信息和你的知识回答问题:" format to allow LLM to use both KB content and its own knowledge

## Testing Notes

Manual verification steps:
1. Start service and open dashboard.html
2. Connect to avatar
3. Switch RAG mode to "知识库+模型"
4. Send question, verify response includes model's own knowledge
5. Switch back to "仅知识库" mode
6. Send same question, verify response only from knowledge base
7. Refresh page, verify mode selection persists

---

*Phase: 08-rag-mode-toggle*
*Completed: 2026-05-12*
