# Chat UI + History — Architecture Research

## 1. Current State

| Module | Role | Relevant Details |
|--------|------|-----------------|
| `app.py` | aiohttp server init | Calls `setup_routes(appasync)`, stores `llm_response` in `app["llm_response"]` |
| `server/routes.py` | API endpoints | `/human`, `/humanaudio`, `/interrupt_talk`, etc. No DB access |
| `server/session_manager.py` | Singleton session mgr | Holds `sessions: Dict[str, BaseAvatar]`, `_llm_history` is on `avatar_session` |
| `llm.py` | Streaming LLM | `llm_response()` runs in executor thread, segments go to `put_msg_txt()`, appends to `_llm_history` at end |
| `web/dashboard.html` | Vanilla JS frontend | Chat tab: text input → POST `/human`, adds message to DOM only (no persistence) |

## 2. New Components

```
LiveTalking/
├── db/
│   └── chat_history.py      # NEW: SQLite layer (schema, CRUD, singleton)
├── server/
│   ├── routes.py            # MODIFY: add history API endpoints
│   └── session_manager.py   # MODIFY: optionally store active conversation_id
├── llm.py                   # MODIFY: save messages during streaming flow
├── app.py                   # MODIFY: init ChatHistory on startup
└── web/
    ├── dashboard.html       # MODIFY: add history panel UI
    └── chat-history.js      # NEW: JS module for history sidebar/logic
```

### 2.1 `db/chat_history.py` — SQLite Layer

**Why a separate module:**
- Clean separation of concerns (routes.py stays lean)
- Testable in isolation
- Single point of DB schema changes

**API (exposed class `ChatHistory`, singleton pattern matching SessionManager):**

```python
class ChatHistory:
    def create_conversation(self, session_id: str, title: str = "新对话") -> str  # returns conv_id
    def delete_conversation(self, conv_id: str) -> bool
    def rename_conversation(self, conv_id: str, title: str) -> bool
    def list_conversations(self, session_id: str = None, limit: int = 50) -> list[dict]
    def get_conversation(self, conv_id: str) -> dict | None  # includes messages

    def add_message(self, conv_id: str, role: str, content: str) -> str  # returns msg_id
    def get_messages(self, conv_id: str) -> list[dict]
    def clear_messages(self, conv_id: str) -> bool
    def set_message_interrupted(self, msg_id: str) -> bool
```

**Schema:**

```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,          -- UUID
    title TEXT NOT NULL DEFAULT '新对话',
    session_id TEXT NOT NULL,
    created_at TEXT NOT NULL,     -- ISO8601
    updated_at TEXT NOT NULL      -- ISO8601
);

CREATE TABLE messages (
    id TEXT PRIMARY KEY,          -- UUID
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK(role IN ('user','assistant','system')),
    content TEXT NOT NULL,
    audio_url TEXT,               -- nullable, for future voice playback
    is_interrupted INTEGER DEFAULT 0,
    created_at TEXT NOT NULL      -- ISO8601
);

CREATE INDEX idx_messages_conv ON messages(conversation_id, created_at);
CREATE INDEX idx_conversations_session ON conversations(session_id, updated_at DESC);
```

**Thread safety:** Use `sqlite3.connect(check_same_thread=False)` with a `threading.Lock` since `llm.py` runs in executor threads while routes.py runs in async loop.

### 2.2 `session_manager.py` Modification

Add tracking of active conversation per session:

```python
class SessionManager:
    def __init__(self):
        # ... existing fields ...
        self.active_conversations: Dict[str, str] = {}  # sessionid -> conv_id

    def get_active_conversation(self, sessionid: str) -> str | None
    def set_active_conversation(self, sessionid: str, conv_id: str)
```

### 2.3 `llm.py` Modification — Saving Messages

The `llm_response()` function is the integration point:

```
llm_response(message, avatar_session, datainfo)
```

**Flow changes:**

1. **Before streaming:** Save user message to DB via ChatHistory singleton
2. **On streaming complete (line 164-166):** Save assistant response to DB
3. **On interrupt (gen_id mismatch):** Mark the last assistant message as interrupted

```python
# At start of llm_response():
chat_history = ChatHistory.get_instance()
conv_id = session_manager.get_active_conversation(avatar_session.sessionid)
if conv_id:
    chat_history.add_message(conv_id, "user", message)
    _current_msg_id = None  # will hold assistant msg id

# After streaming loop completes (line 164):
if conv_id and result:
    _current_msg_id = chat_history.add_message(conv_id, "assistant", result)

# On interrupt detection (line 147):
if _current_msg_id:
    chat_history.set_message_interrupted(_current_msg_id)
```

**Why save during streaming (not after):**
- User message is saved immediately on submission
- Assistant message is saved once the full response is assembled (streaming is per-segment, but the full text is accumulated in `result`)
- This is simpler than saving partial segments and avoids fragmenting the conversation

### 2.4 `routes.py` — New API Endpoints

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| `POST` | `/conversations/create` | `create_conversation` | Create new conversation, returns `{conv_id}` |
| `POST` | `/conversations/list` | `list_conversations` | List conversations for session |
| `POST` | `/conversations/get` | `get_conversation` | Get conversation with messages |
| `POST` | `/conversations/rename` | `rename_conversation` | Update title |
| `POST` | `/conversations/delete` | `delete_conversation` | Delete conversation + messages |
| `POST` | `/conversations/clear` | `clear_messages` | Clear messages in conversation (keep conv) |
| `POST` | `/conversations/switch` | `switch_conversation` | Set active conversation for session |

**Style:** Follow existing `/human` pattern — all `POST`, JSON in/out, `{"code": 0, "data": ...}` format.

### 2.5 `app.py` — Startup

```python
# Near line 156, after session_manager.init_builder():
from db.chat_history import ChatHistory
ChatHistory.get_instance(db_path="data/chat.db")
```

The `ChatHistory` constructor creates tables on first access (idempotent `CREATE TABLE IF NOT EXISTS`).

## 3. Data Flow

### Chat with History

```
User types text
    │
    ▼
dashboard.html
  └─ POST /human {text, type:chat, sessionid}
       │
       ▼
    routes.py: human()
      └─ llm_response(text, avatar_session, datainfo)  [executor thread]
           │
           ├─ 1. chat_history.add_message(conv_id, "user", text)
           │
           ├─ 2. LLM streaming loop (existing)
           │      └─ avatar_session.put_msg_txt(segment)  [existing]
           │
           └─ 3. On complete:
                  chat_history.add_message(conv_id, "assistant", result)
                  avatar_session._llm_history.append(...)  [existing]
```

### Page Load: History Recovery

```
dashboard.html loaded
    │
    ├─ GET /conversations/list  →  populate sidebar
    │
    └─ If active conversation exists:
         GET /conversations/get  →  render messages in chat panel
```

### Conversation Management

```
[New Chat] button
    └─ POST /conversations/create → get conv_id → switch active → clear chat panel

[Delete] button on conversation
    └─ POST /conversations/delete → remove from sidebar

[Click] conversation in sidebar
    └─ POST /conversations/switch + /get → load messages
```

## 4. Data Model

### Conversations

| Field | Type | Notes |
|-------|------|-------|
| `id` | TEXT UUID | Primary key |
| `title` | TEXT | Default "新对话", auto-generate or user-rename |
| `session_id` | TEXT | Links to WebRTC session |
| `created_at` | TEXT | ISO8601 |
| `updated_at` | TEXT | ISO8601 |

### Messages

| Field | Type | Notes |
|-------|------|-------|
| `id` | TEXT UUID | Primary key |
| `conversation_id` | TEXT FK | Cascade delete |
| `role` | TEXT | `user` / `assistant` / `system` |
| `content` | TEXT | Full text (not segments) |
| `audio_url` | TEXT | Nullable, for future TTS audio replay |
| `is_interrupted` | INT | 0=complete, 1=user interrupted before finish |
| `created_at` | TEXT | ISO8601 |

## 5. Build Order

| Step | Files | Description | Verification |
|------|-------|-------------|-------------|
| 1 | `db/chat_history.py` | SQLite module: schema, CRUD, singleton | Unit test create/list/add/get/delete |
| 2 | `server/routes.py`, `app.py` | Add history API endpoints, init on startup | `curl` test all endpoints |
| 3 | `llm.py`, `session_manager.py` | Save messages during streaming flow | Full conversation round-trip via curl |
| 4 | `web/chat-history.js` | JS module: history sidebar, message loading | Browser console test |
| 5 | `web/dashboard.html` | Integrate history panel into UI | Visual + functional test |

**Step 1-2 can be parallelized** with Step 4-5 (backend vs frontend).

## 6. Edge Cases

| Case | Handling |
|------|----------|
| No active conversation | Create one automatically on first `/human` call with `type:chat` |
| Interrupted response | Save assistant message with `is_interrupted=1`, show "回答被中断" in UI |
| Multiple sessions | Each session has its own `active_conversation_id` |
| DB file missing | Auto-create on init (SQLite creates db file) |
| Concurrent writes | Thread lock + `WAL` journal mode for better concurrency |
| Very long conversation | `list_conversations` returns latest 50, `get_messages` returns all (pagination optional) |
