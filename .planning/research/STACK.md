# Stack Recommendations: Chat UI + History

**Date:** 2026-05-13
**Context:** Adding chat UI panel (message bubbles, conversation list, history scrolling) and SQLite persistence to LiveTalking's dashboard.

## 1. Frontend Framework: Alpine.js 3.x

**Choice: Alpine.js 3 (via CDN) — no bundler, no build step**

| Option | Verdict |
|--------|---------|
| React/Vue | ❌ Overkill; requires build tooling; project uses jQuery+Bootstrap |
| **Alpine.js 3.x** | ✅ **Recommended** — 15KB min+gzip, `x-data`/`x-for`/`x-model` for reactive chat panel |
| htmx 2.x | ⚠ Viable alternative but existing code uses fetch() + jQuery patterns, not HATEOAS |
| Vanilla JS | ⚠ Works but will be messy for reactive state (message list, scroll position, loading states) |

**Why Alpine.js:**
- Zero build step — drop a `<script>` tag, works with existing aiohttp static serving
- Declarative rendering of message list via `x-for` with transition animations
- `x-model` for textarea binding, `x-show` for loading/typing indicators
- Coexists with existing jQuery code (no conflict)
- Component reuse via `x-data` functions (no SFC, no bundler)

**CDN import** (add to dashboard.html):
```html
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.8/dist/cdn.min.js" defer></script>
```

**Alternative — htmx:** If the team prefers server-rendered HTML fragments via `/api/chat/history` endpoints, htmx 2.x works too. But Alpine.js is a better fit given the existing client-side fetch patterns.

---

## 2. SQLite Persistence: aiosqlite

**Choice: aiosqlite — async-first SQLite for aiohttp**

| Option | Verdict |
|--------|---------|
| `sqlite3` stdlib | ❌ Synchronous; blocks the asyncio event loop; must be wrapped in `run_in_executor` |
| **aiosqlite** | ✅ **Recommended** — native async/await, wraps stdlib sqlite3, zero extra C deps |
| SQLAlchemy 2.x + aiosqlite | ❌ Overkill for flat chat history (no ORM needed for single-table append-log) |
| peewee | ❌ Synchronous only; no async driver |
| datasets (HuggingFace) | ❌ Wrong abstraction for append-only conversation log |
| TinyDB | ❌ JSON-based, no concurrent safety, no SQL queries |

**Why aiosqlite:**
- Native `async with` context manager — integrates cleanly with aiohttp handlers
- Single-table schema: `conversations(id, session_id, role, content, created_at)`
- Row-based, supports time-range queries for history scrolling
- Connection pooling: single shared aiosqlite connection with WAL journal mode
- No ORM overhead — raw SQL is < 20 lines for the entire API surface

**Add to `requirements.txt`:**
```
aiosqlite>=0.20.0
```

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
```

---

## 3. Frontend Dependencies

| Library | Version | Purpose | CDN |
|---------|---------|---------|-----|
| **Alpine.js** | 3.14.8 | Reactive chat panel | `cdn.jsdelivr.net/npm/alpinejs@3.14.8/dist/cdn.min.js` |
| **marked** | 15.0.7 | Markdown → HTML in message bubbles | `cdn.jsdelivr.net/npm/marked@15.0.7/marked.min.js` |
| **DOMPurify** | 3.2.4 | XSS sanitization before innerHTML | `cdn.jsdelivr.net/npm/dompurify@3.2.4/dist/purify.min.js` |

All three are existing jQuery-era compatible (no module system needed — global UMD build).

---

## 4. API Endpoints (New)

Add to `server/routes.py`:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/chat/history?session_id=...&before_id=...&limit=50` | Paginated history (infinite scroll) |
| `POST` | `/api/chat/clear` | Clear current conversation history |
| `GET` | `/api/chat/conversations?limit=20` | List recent conversation sessions |
| `POST` | `/api/chat/save` | Force-save a message (or write-through) |

Write-through strategy: on every `/human` response, persist to SQLite in the `llm_response` callback. For GET history, read from SQLite.

---

## 5. Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `server/chat_db.py` | **Create** | aiosqlite wrapper: init, insert, query, get/clean |
| `server/routes.py` | **Modify** | Add 4 history endpoints |
| `llm.py` | **Modify** | Save user/assistant messages to SQLite in `llm_response()` |
| `web/dashboard.html` | **Modify** | Add Alpine.js + marked + DOMPurify; replace manual DOM chat with reactive panel |
| `requirements.txt` | **Modify** | Add `aiosqlite>=0.20.0` |

---

## 6. Why Not...

- **WebSocket for chat history:** Overkill — REST works fine for paginated history reads; `/human` endpoint already uses POST.
- **ChromaDB for history:** Vector DB is for RAG retrieval, not append-only conversation logs. Wrong tool.
- **Redis:** Single-server deployment; Redis adds operational complexity for zero benefit here.
- **Server-Sent Events (SSE):** Could be used for live message push, but current architecture uses `llm_response` callback thread → `put_msg_txt` → avatar pipeline; SSE is useful if we want real-time message display in the chat panel without polling.
