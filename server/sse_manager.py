"""SSE connection manager for streaming LLM text to frontend."""
import asyncio
from typing import Dict, Set
from utils.logger import logger


class SSEManager:
    _instance = None
    _connections: Dict[str, Set[asyncio.Queue]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def subscribe(self, sessionid: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        if sessionid not in self._connections:
            self._connections[sessionid] = set()
        self._connections[sessionid].add(q)
        return q

    def unsubscribe(self, sessionid: str, q: asyncio.Queue):
        if sessionid in self._connections:
            self._connections[sessionid].discard(q)
            if not self._connections[sessionid]:
                del self._connections[sessionid]

    async def push_chunk(self, sessionid: str, data: dict):
        if sessionid in self._connections:
            dead = set()
            for q in self._connections[sessionid]:
                try:
                    await asyncio.wait_for(q.put(data), timeout=1)
                except asyncio.TimeoutError:
                    dead.add(q)
            for q in dead:
                self._connections[sessionid].discard(q)

    def get_connection_count(self, sessionid: str) -> int:
        return len(self._connections.get(sessionid, set()))
