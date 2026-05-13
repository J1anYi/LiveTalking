# Phase 11: Session Management - Context

**Status:** Auto-generated
**Requirements:** CONV-01, CONV-02, CONV-03, CONV-04, CHAT-05

## Scope
- Conversation sidebar in dashboard
- New/switch/delete conversations
- History loading from DB API
- Interrupt message indicator in UI
- Auto-create conversation on first `/human`

## Key Decisions
- Sidebar on the left side of the chat panel
- Conversations sorted by updated_at DESC
- Auto-title from first user message
- Interrupt indicator: "⚠ 已中断" badge on interrupted messages

## Files to Modify
- `web/dashboard.html` — Alpine.js sidebar + interrupt indicator
