# PITFALLS: Chat UI + SQLite History in LiveTalking

## 1. Race Conditions: Streaming + Interrupt + Partial Save

### The Problem

In `llm.py:128-154`, the LLM streams tokens in a thread executor. At `llm.py:145`, interrupt is detected by checking `_gen_id`. When an interrupt fires:

1. One segment may be mid-write to the DB
2. LLM stops streaming, but the *user's interrupt request* itself is a message that also needs saving
3. Both the partial AI response and the new user message hit the DB simultaneously from different threads

### Concrete Scenario

```
Time ──────────────────────────────────────────>
User:  "讲个故事"  →  POST /human
                    →  llm_response() starts streaming
                    →  gen_id=1
                    →  chunk "从前有座山..." written to avatar_session.put_msg_txt()
                    →  DB save of "从前有座山..." fires async
User:  "换一个"     →  POST /human (interrupt=true)
                    →  flush_talk() → gen_id=2
                    →  llm_response() new thread for "换一个"
                    →  DB save of "换一个" and DB save of "从前有座山" race
```

**Result**: The partial "从前有座山" message may appear in the DB as a *complete* AI response even though it was interrupted. Or the ordering might be: "换一个" then "从前有座山", which is nonsensical.

### Prevention

- **Don't save partial AI output at all.** Only persist AI messages after the LLM stream fully completes (or is confirmed interrupted). Use `_gen_id` at save-time to verify the generation wasn't superseded.
- **Save at a single point.** Add a callback/hook in `llm.py` that fires *once* after the stream ends, not per-chunk. The current code already does this — `_llm_history.append()` at line 165 happens after the loop — but if you add per-segment DB writes (e.g. for real-time chat bubble updates), you'll hit this race.
- **Use a write-ahead log or queue.** Push save tasks to a single consumer so ordering is deterministic.
- **Assign a server-side `message_id`** (UUID) to every message at creation time. The DB can use this to deduplicate.

---

## 2. Performance: SQLite Blocking the Async Event Loop

### The Problem

`app.py:199` runs a single asyncio event loop. `routes.py` handlers are async coroutines. If you use the synchronous `sqlite3` module for DB writes, every `INSERT` or `SELECT` blocks the loop:

```
HTTP Request → routes.py (async) → db.execute("INSERT ...") → BLOCK 5-50ms
                                                              → all other WebRTC/HTTP tasks delayed
```

In a streaming system, 5ms blocking matters — audio/video frame timing is driven by the same loop.

### Prevention

- **Use `aiosqlite`**. It wraps SQLite in an async context so writes yield the event loop.
- **Or: delegate DB writes to a thread pool executor** (`loop.run_in_executor(None, db_write, data)`).
- **Or: use an in-memory queue** (`asyncio.Queue`) that a background task drains to SQLite in batches.
- **Warning: Do NOT mix `aiosqlite` with sync `sqlite3` on the same file** — this causes `SQLITE_BUSY` errors.

### Benchmark Reference

| Operation | sync `sqlite3` | `aiosqlite` | `run_in_executor` |
|-----------|---------------|-------------|-------------------|
| INSERT (1 row) | 5-15ms blocking | 0ms blocking | 0ms blocking |
| SELECT 100 rows | 1-3ms blocking | 0ms blocking | 0ms blocking |
| Transaction (10 rows) | 10-30ms blocking | 0ms blocking | 0ms blocking |

For a 25fps system where each frame has ~40ms budget, even a single 15ms block risks frame drops.

---

## 3. Session Mismatch: In-Memory History vs DB History

### The Problem

Currently, conversation history lives in `avatar_session._llm_history` (`llm.py:76-77`). When you add a DB, you now have **two sources of truth**:

| Session state | In-Memory `_llm_history` | SQLite DB |
|--------------|--------------------------|-----------|
| New session (first message) | `[]` | No rows |
| After 10 messages | 10 messages | 10 messages |
| After server restart | **GONE** | Still there |
| After DB compaction | Still there | Truncated |

### Three Specific Failure Modes

#### 3a. Stale in-memory history after DB load
Session resumes from DB history, but `_llm_history` is empty because the session was newly created. The avatar generates LLM context from `_llm_history[-4:]` (`llm.py:97-98`) which is empty, so RAG context-building uses only the current message — losing multi-turn context.

#### 3b. DB history grows unbounded
Every turn adds 2 rows (user + AI). Over hours of conversation, `SELECT * FROM history WHERE session_id = ?` returns thousands of rows. The frontend tries to render them all → browser freezes.

#### 3c. Deleted/archived DB rows still exist in memory
If a user deletes a conversation from the UI (DB delete), the session's `_llm_history` still has the data. LLM prompt-building will include messages the user thought were gone.

### Prevention

- **Single source of truth.** Load history from DB into `_llm_history` at session creation. Never bypass the DB.
- **Implement a sync boundary after DB writes.** After `llm_response()` appends to `_llm_history`, also write to DB in the same transaction scope.
- **Cap history length.** Truncate `_llm_history` and DB to the last N turns (e.g. last 50) to bound memory and context length.
- **Add a `deleted` flag** instead of hard-deleting rows. Filter both in-memory and DB queries by `deleted=0`.
- **On session resume** (e.g., page refresh), load DB history into `_llm_history` via a new API endpoint `GET /history?session_id=X`.

---

## 4. Frontend: Auto-Scroll Fighting User Scroll

### The Problem

The current dashboard uses a simple `scrollTop = scrollHeight` pattern (`dashboard.html:477`). In a chat UI with streaming responses:

1. User scrolls **up** to read earlier messages
2. A new token arrives → JS calls `scrollTop = scrollHeight`
3. User is violently yanked back to the bottom
4. User gets annoyed

### Detection Logic

```js
// ❌ NAIVE — always scrolls down
container.scrollTop = container.scrollHeight;

// ✅ CORRECT — only scroll if user was already at bottom
const isAtBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 50;
if (isAtBottom) {
    container.scrollTop = container.scrollHeight;
}
```

### Additional Frontend Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Re-rendering entire message list on each token | DOM rebuild, janky scroll | Append-only DOM: insert one `<div>` per message, never rebuild |
| Streaming text flicker | AI response text appears character by character in a recreated element | Use a stable element ID per message; update `innerText` in-place |
| Too many DOM nodes | 500+ messages → browser lags | Virtual scrolling (IntersectionObserver) or paginate (load last 50, "load more" button) |
| `innerHTML` without sanitization | XSS if AI response contains `<script>` | Use `textContent` not `innerHTML`, or sanitize server-side in `llm.py` |
| Emoji in message text | Rendering glitches with legacy font stacks | Ensure `<meta charset="UTF-8">` and use a font that supports emoji (Segoe UI Emoji, Noto) |

---

## 5. Edge Cases: Duplicate Messages, Ordering, Unicode/Emoji

### 5a. Duplicate Messages

**How duplicates happen:**
- User double-clicks "Send" → two identical POST `/human` requests → two identical DB rows
- Network retry (e.g., axios auto-retry on timeout) → same message inserted twice
- Page refresh + re-send of last message

**Prevention:**
- **Client-side debounce**: Disable send button until the previous request completes.
- **Server-side idempotency key**: Accept a client-generated `client_msg_id` (UUID) in the POST body. DB has `UNIQUE(client_msg_id)`. Duplicate inserts fail silently.
- **Or: deduplicate on (session_id, content, created_at) within a 1-second window** using a `UNIQUE` constraint or application-level check.

### 5b. Message Ordering

**How ordering breaks:**
- LLM streaming completes → AI response saved to DB with `created_at=T1`
- User sends next message → saved with `created_at=T2`
- But if the final AI save happens via an async queue that's delayed, `T2 < T1` is possible

**Prevention:**
- DB schema must include a monotonically increasing `seq` column (auto-increment `INTEGER PRIMARY KEY`), not just a timestamp. Order by `seq` for display.
- Or: assign sequence numbers server-side. The `/human` handler can atomically increment a session counter.

### 5c. Unicode/Emoji in SQLite

**SQLite handles UTF-8 natively** — emoji like 😊 and CJK characters like 中文 work fine as `TEXT` columns. But there are traps:

| Trap | Why | Fix |
|------|-----|-----|
| `VARCHAR` length limits count bytes not chars | `VARCHAR(10)` may reject a 5-emoji string | Use `TEXT` (unbounded) for message content |
| `LIKE` with emoji | `SELECT ... WHERE content LIKE '%😊%'` may not match | Use `INSTR(content, '😊') > 0` or full-text search |
| Python `sqlite3` + `str` | Works fine, but `None` handling trips people | Always `str(x) if x else ''` before insert |
| `json.dumps()` on message with emoji | Works in Python 3, but ensure ensure_ascii=False if persisting JSON | `json.dumps(..., ensure_ascii=False)` |

### 5d. Very Long Messages

LLM can produce extremely long responses if the user asks "write a novel". Without length limits:
- DB row stores 100KB+ of text
- Frontend renders huge DOM node → jank
- Full-text search on the message column becomes slow

**Prevention:**
- Cap message length at the API layer (e.g., 10,000 chars)
- Or: truncate display but store full text (show "..." with expand button)
- Use `SELECT content` only when needed, not in list queries

---

## 6. Migration: Existing Sessions Have No History in DB

### The Problem

After deploying the DB-backed system, **all existing sessions** have `_llm_history` in memory but zero rows in the DB. When the service restarts, the in-memory history is gone. The user's ongoing conversation loses all context.

### Affected Scenarios

| Scenario | Before DB | After DB | Problem |
|----------|-----------|----------|---------|
| Active session (mid-conversation) | `_llm_history` has 5 turns | DB has 0 rows | After restart, session resumes with no memory |
| Long-running server (days) | History accumulates in RAM | DB has nothing | Memory leak + lost context on restart |
| Multi-session support | Each avatar_session has its own `_llm_history` | No DB records | Session isolation breaks after restart |

### Prevention

- **Add a startup migration.** Before accepting new requests, scan all active sessions. For each session with non-empty `_llm_history`, bulk-insert into DB.
  ```python
  # In app.py main(), after session_manager init:
  for sid, session in session_manager.sessions.items():
      history = getattr(session, '_llm_history', [])
      if history:
          await bulk_insert_history(sid, history)
  ```
- **Or: lazy migration.** Intercept the first `/history` or `/human` request for a session. If DB rows == 0 but session exists, dump `_llm_history` to DB before proceeding.
- **Or: just accept the loss.** Document that "history persistence starts from the moment of deployment; prior conversations are ephemeral." This is simplest but may confuse users.

### Schema Migration Strategy

Don't assume the DB file exists. Use `CREATE TABLE IF NOT EXISTS` and `PRAGMA user_version` for schema versioning:

```sql
PRAGMA user_version = 1;
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    client_msg_id TEXT UNIQUE,
    seq INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    deleted INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_session_seq ON conversations(session_id, seq);
```

---

## Summary: Critical Path Checklist

| # | Check | Prevented Pitfall |
|---|-------|-------------------|
| 1 | **Streaming saves only on completion** | Partial/interrupted messages in DB |
| 2 | **aiosqlite or thread executor for DB** | Event loop blocking → frame drops |
| 3 | **Load DB history into `_llm_history` on session start** | Two sources of truth mismatch |
| 4 | **Debounce send button on client side** | Duplicate messages from double-click |
| 5 | **Client-generated `client_msg_id` with UNIQUE constraint** | Duplicate messages from network retry |
| 6 | **Auto-increment `seq` column for ordering** | Async save causing wrong message order |
| 7 | **User-scroll detection before auto-scroll** | Fighting user's scroll position |
| 8 | **Append-only DOM + stable element IDs** | Janky re-render of entire message list |
| 9 | **History length cap (last N turns)** | Unbounded DB growth and memory usage |
| 10 | **Migration hook for existing sessions** | Lost history on server restart |
