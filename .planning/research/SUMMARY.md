# Research Summary: Chat UI & History

**Key findings synthesized from STACK + FEATURES + ARCHITECTURE + PITFALLS**

## Stack Recommendations

| Component | Choice | Why |
|-----------|--------|-----|
| 前端框架 | **Alpine.js 3.x** (CDN) | 15KB, 零构建, 与现有 jQuery 共存 |
| SQLite | **aiosqlite** | 原生 async, 不阻塞事件循环 |
| Markdown | **marked** + **DOMPurify** | 消息气泡富文本渲染 |
| 流式推送 | **SSE (EventSource)** | 单向推送, 自动重连, 比 WebSocket 轻量 |

## Core Features (Table Stakes)

1. **消息气泡 UI** — 问答气泡区分, 系统消息独立样式
2. **SSE 流式输出** — LLM 文字逐 chunk 推送到前端, 打字机效果
3. **自动滚动** — 检测用户位置决定是否自动滚
4. **时间戳 + 消息状态** — 发送中/完成/中断/错误
5. **SQLite 持久化** — `conversations` + `messages` 两张表
6. **History API** — 保存/获取/清除历史

## Key Architecture Decisions

- **新模块**: `db/chat_history.py` (单例, 与 SessionManager 同级)
- **保存时机**: LLM 流完成后一次性写入, 非逐 segment
- **线程安全**: threading.Lock + WAL journal mode
- **会话管理**: `session_manager` 增加 `active_conversations` 追踪
- **消息排序**: 自增 `seq` 列, 非时间戳

## Critical Pitfalls to Address

| Pitfall | Solution |
|---------|----------|
| 中断时部分回复被持久化 | 完成后一次性写入 + `_gen_id` 校验 |
| sqlite3 阻塞事件循环 | 必须用 `aiosqlite` |
| 内存历史 vs DB 历史不一致 | session 启动时从 DB 加载到 `_llm_history` |
| 前端自动滚动与用户滚动冲突 | `isAtBottom` 检测 |
| 重复消息 | 前端 debounce + 后端 `client_msg_id UNIQUE` |
| 消息乱序 | 自增 `seq` 列排序 |
