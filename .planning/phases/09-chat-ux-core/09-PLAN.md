# Phase 9: Chat UX Core — Plan

## Tasks

### Task 1: SSE Endpoint
Create `GET /sse/chat` endpoint that pushes LLM stream chunks to frontend via EventSource.

- `server/sse_manager.py` — Singleton SSE connection manager (Dict[sessionid, queue])
- `server/routes.py` — Add SSE route
- `llm.py` — Push text chunks to SSE manager during streaming

### Task 2: Alpine.js + Chat Panel UI
Replace dashboard.html chat section with Alpine.js reactive chat panel.

- Alpine.js, marked.js, DOMPurify CDN scripts
- `x-data` chat state: messages[], inputText, loading, sessionId
- `x-for` message list rendering
- `x-model` input binding
- EventSource connection to `/sse/chat`
- Message append on SSE events

### Task 3: Message Bubbles CSS
- `.chat-bubble.user` — right-aligned, blue
- `.chat-bubble.assistant` — left-aligned, gray
- `.chat-bubble.system` — centered
- `.timestamp` — small gray text
- Smooth appear animation

### Task 4: Auto-scroll
- `isAtBottom` detection before `scrollTop = scrollHeight`
- IntersectionObserver for "scroll to bottom" button

## Verification
1. SSE endpoint returns proper event-stream headers
2. Frontend receives and displays streaming text
3. Message bubbles show correct alignment by role
4. Auto-scroll only triggers when user is at bottom
5. Timestamps display correctly
