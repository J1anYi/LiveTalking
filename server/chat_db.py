"""SQLite chat history module with aiosqlite (async)."""
import os
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Optional
from utils.logger import logger

try:
    import aiosqlite
except ImportError:
    aiosqlite = None


class ChatHistory:
    _instance = None
    _lock = None  # initialized in init()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._db_path = None
            self._lock = None
            self._initialized = False

    def init(self, db_path: str = "data/chat.db"):
        self._db_path = db_path
        if self._lock is None:
            self._lock = asyncio.Lock()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._initialized = True
        logger.info(f"ChatHistory initialized: {db_path}")

    async def _get_db(self):
        if not self._initialized:
            raise RuntimeError("ChatHistory not initialized. Call init() first.")
        db = await aiosqlite.connect(self._db_path)
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        return db

    async def _ensure_tables(self, db):
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL DEFAULT '新对话',
                session_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK(role IN ('user','assistant','system')),
                content TEXT NOT NULL,
                seq INTEGER NOT NULL DEFAULT 0,
                is_interrupted INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id, seq);
            CREATE INDEX IF NOT EXISTS idx_conv_session ON conversations(session_id, updated_at DESC);
        """)
        await db.commit()

    async def create_conversation(self, session_id: str, title: str = "新对话") -> str:
        conv_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        async with self._lock:
            db = await self._get_db()
            try:
                await self._ensure_tables(db)
                await db.execute(
                    "INSERT INTO conversations (id, title, session_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (conv_id, title, session_id, now, now),
                )
                await db.commit()
            finally:
                await db.close()
        logger.info(f"Created conversation {conv_id} for session {session_id}")
        return conv_id

    async def list_conversations(self, session_id: str = None, limit: int = 50) -> list:
        async with self._lock:
            db = await self._get_db()
            try:
                await self._ensure_tables(db)
                if session_id:
                    cursor = await db.execute(
                        "SELECT id, title, session_id, created_at, updated_at FROM conversations WHERE session_id=? ORDER BY updated_at DESC LIMIT ?",
                        (session_id, limit),
                    )
                else:
                    cursor = await db.execute(
                        "SELECT id, title, session_id, created_at, updated_at FROM conversations ORDER BY updated_at DESC LIMIT ?",
                        (limit,),
                    )
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]
            finally:
                await db.close()

    async def get_conversation(self, conv_id: str) -> Optional[dict]:
        async with self._lock:
            db = await self._get_db()
            try:
                await self._ensure_tables(db)
                cursor = await db.execute("SELECT id, title, session_id, created_at, updated_at FROM conversations WHERE id=?", (conv_id,))
                row = await cursor.fetchone()
                if not row:
                    return None
                conv = dict(row)
                msg_cursor = await db.execute(
                    "SELECT id, role, content, seq, is_interrupted, created_at FROM messages WHERE conversation_id=? ORDER BY seq",
                    (conv_id,),
                )
                conv["messages"] = [dict(m) for m in await msg_cursor.fetchall()]
                return conv
            finally:
                await db.close()

    async def delete_conversation(self, conv_id: str) -> bool:
        async with self._lock:
            db = await self._get_db()
            try:
                await self._ensure_tables(db)
                await db.execute("DELETE FROM messages WHERE conversation_id=?", (conv_id,))
                await db.execute("DELETE FROM conversations WHERE id=?", (conv_id,))
                await db.commit()
                return True
            finally:
                await db.close()

    async def add_message(self, conv_id: str, role: str, content: str, seq: int = None) -> str:
        msg_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        async with self._lock:
            db = await self._get_db()
            try:
                await self._ensure_tables(db)
                if seq is None:
                    cursor = await db.execute("SELECT COALESCE(MAX(seq), 0) + 1 FROM messages WHERE conversation_id=?", (conv_id,))
                    row = await cursor.fetchone()
                    seq = row[0] if row else 1
                await db.execute(
                    "INSERT INTO messages (id, conversation_id, role, content, seq, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (msg_id, conv_id, role, content, seq, now),
                )
                await db.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, conv_id))
                await db.commit()
            finally:
                await db.close()
        return msg_id

    async def set_message_interrupted(self, msg_id: str):
        async with self._lock:
            db = await self._get_db()
            try:
                await self._ensure_tables(db)
                await db.execute("UPDATE messages SET is_interrupted=1 WHERE id=?", (msg_id,))
                await db.commit()
            finally:
                await db.close()
