# Phase 9: Chat UX Core - Context

**Status:** Auto-generated (smart discuss)
**Requirements:** CHAT-01, CHAT-02, CHAT-04, UI-01, UI-02, UI-03

## Scope
- Add SSE endpoint for streaming LLM text to frontend
- Alpine.js CDN integration in dashboard.html
- Message bubbles UI (user left, assistant right, system center)
- Auto-scroll with user scroll detection
- Timestamp display

## Key Decisions

### SSE vs WebSocket
Use Server-Sent Events (SSE) — unidirectional, auto-reconnect, simpler than WebSocket.

### Alpine.js (CDN)
Zero build step. Drop `<script>` tag, use `x-data`/`x-for`/`x-model` for reactive chat panel.

### Message Format
- user messages: right-aligned, blue background
- assistant messages: left-aligned, gray background
- system messages: centered, small text
- Each message has a timestamp (HH:MM)

### Auto-scroll
Only scroll to bottom if user is already near the bottom (< 50px from bottom).

## Files to Create/Modify
- `server/routes.py` — Add SSE endpoint (`GET /sse/chat`)
- `llm.py` — Push text chunks to SSE subscribers
- `web/dashboard.html` — Alpine.js + chat panel UI
- `web/css/chat.css` — Chat bubble styles
