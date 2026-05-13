# Phase 12: Polish & Edge Cases - Context

**Status:** Auto-generated
**Requirements:** CHAT-03, CHAT-06

## Scope
- Markdown rendering with marked.js + DOMPurify ✅ (done in Phase 9)
- Message status: sending/typing/complete ✅ (done in Phase 9)
- Send button debounce ✅ (done in Phase 9, `sending` flag)
- Interrupt indicator ✅ (done in Phase 11)
- Client-side message dedup (client_msg_id + UNIQUE constraint)
- Frontend debounce for rapid sends
- Long message truncation

## Files to Modify
- `llm.py` — Add client_msg_id support
- `web/dashboard.html` — Message truncation display
