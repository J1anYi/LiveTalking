# Roadmap: LiveTalking RAG Knowledge Base

## Milestones

- ✅ **v1.0 RAG Knowledge Base** — Phases 1-6 (shipped 2026-05-12)
- ✅ **v1.1 Bug Fixes & UX Enhancement** — Phases 7-8 (shipped 2026-05-12)

## Phases

<details>
<summary>✅ v1.0 RAG Knowledge Base (Phases 1-6) — SHIPPED 2026-05-12</summary>

- [x] Phase 1: Research & Design (2 plans) — completed 2026-05-11
- [x] Phase 2: Core RAG Module (1 plan) — completed 2026-05-11
- [x] Phase 3: Data Source Connectors (4 plans) — completed 2026-05-12
- [x] Phase 4: LLM Integration (3 plans) — completed 2026-05-12
- [x] Phase 5: CLI & Configuration (5 plans) — completed 2026-05-12
- [x] Phase 6: Testing & Documentation (5 plans) — completed 2026-05-12

</details>

---

## v1.1 Bug Fixes & UX Enhancement

### Phase 7: Graceful Exit

**Goal:** 修复 Ctrl+C 后进程无法正常退出的问题

**Requirements:** EXIT-01, EXIT-02, EXIT-03

**Status:** ✅ Completed (2026-05-12)

**Success Criteria:**
1. 用户按 Ctrl+C 后，服务在 5 秒内完全退出
2. 退出后 8010 端口立即释放
3. 所有后台线程正确停止，无残留进程

**Plans:**
- [x] 7.1: 分析并修复 asyncio 信号处理
- [x] 7.2: 添加 Avatar session 清理逻辑
- [x] 7.3: 添加 Output 模块清理逻辑
- [x] 7.4: 测试验证优雅退出

---

### Phase 8: RAG Mode Toggle

**Goal:** 添加 RAG 模式切换功能，支持 RAG-only 和 RAG+模型知识 两种模式

**Requirements:** RAG-01, RAG-02, RAG-03, RAG-04, RAG-05

**Status:** ✅ Completed (2026-05-12)

**Success Criteria:**
1. Dashboard 显示 RAG 模式切换按钮
2. 用户可切换"仅 RAG"和"RAG+模型知识"两种模式
3. 切换后 LLM 回答使用正确的模式
4. 模式状态刷新页面后保持

**Plans:**
- [x] 8.1: 添加 `/set_rag_mode` API 端点
- [x] 8.2: 修改 llm.py 支持混合模式 prompt
- [x] 8.3: 添加 session 级 RAG 模式状态管理
- [x] 8.4: Dashboard 前端添加切换按钮
- [x] 8.5: 测试验证模式切换功能

---

## v1.2 Chat UI & History

### Phase 9: Chat UX Core

**Goal:** SSE 流式推送 + 消息气泡 UI + Alpine.js 前端框架集成

**Requirements:** CHAT-01, CHAT-02, CHAT-04, UI-01, UI-02, UI-03

**Status:** 🔲 Planned

**Success Criteria:**
1. 新建 SSE 端点推送 LLM 流式文字，前端 EventSource 逐 chunk 追加到气泡
2. 消息气泡 user/assistant 左右对齐、不同底色，时间戳清晰
3. 自动滚动 + 用户滚动检测，不干扰用户手动滚动
4. Alpine.js 集成，x-for 渲染消息列表，x-model 绑定输入框
5. 消息气泡 CSS 动画（平滑出现、过渡）

**Key decisions:**
- Alpine.js CDN 引入，零构建，与现有 jQuery 共存
- SSE 端点独立于 `/human`，避免改造现有流式管道
- Append-only DOM 更新（稳定元素 ID，不重建列表）

---

### Phase 10: SQLite History

**Goal:** 对话历史持久化 + LLM streaming 完成后自动保存

**Requirements:** HIST-01, HIST-02, HIST-03, HIST-04, HIST-05, UI-04

**Status:** 🔲 Planned

**Success Criteria:**
1. `db/chat_history.py` 模块：conversations + messages 表，aiosqlite async 访问
2. API 端点：`/conversations/create`, `/conversations/list`, `/conversations/get`, `/conversations/delete`, `/history`
3. LLM streaming 完成后自动写入 DB，中断时标记 `is_interrupted=1`
4. Session 启动时从 DB 加载 `_llm_history`，双数据源一致
5. 线程安全：threading.Lock + WAL journal mode，自增 seq 列保证顺序

---

### Phase 11: Session Management

**Goal:** 对话侧边栏 + 会话列表 + 新建/切换/删除

**Requirements:** CONV-01, CONV-02, CONV-03, CONV-04, CHAT-05

**Status:** 🔲 Planned

**Success Criteria:**
1. 左侧对话侧边栏，按更新时间排序，显示摘要和消息数
2. 新建/切换/删除会话，首次 `/human` 调用自动创建
3. 历史滚动加载（IntersectionObserver + before_id 分页）
4. 打断消息在 UI 中标记为"已中断"

---

### Phase 12: Polish & Edge Cases

**Goal:** Markdown 渲染、消息状态、Debounce、边防情况处理

**Requirements:** CHAT-03, CHAT-06, HIST-05（防线验证）

**Status:** 🔲 Planned

**Success Criteria:**
1. Markdown 渲染（marked.js + DOMPurify），视听分离
2. 消息状态指示：发送中/完成/中断/错误
3. 发送按钮 debounce 防止重复提交
4. 消息防重（client_msg_id UNIQUE）
5. 超长消息截断 + 展开

---

## Progress

| Phase | Milestone | Plans | Status | Completed |
|-------|-----------|-------|--------|-----------|
| 1. Research & Design | v1.0 | 2/2 | Complete | 2026-05-11 |
| 2. Core RAG Module | v1.0 | 1/1 | Complete | 2026-05-11 |
| 3. Data Source Connectors | v1.0 | 4/4 | Complete | 2026-05-12 |
| 4. LLM Integration | v1.0 | 3/3 | Complete | 2026-05-12 |
| 5. CLI & Configuration | v1.0 | 5/5 | Complete | 2026-05-12 |
| 6. Testing & Documentation | v1.0 | 5/5 | Complete | 2026-05-12 |
| 7. Graceful Exit | v1.1 | 1/1 | Complete | 2026-05-12 |
| 8. RAG Mode Toggle | v1.1 | 1/1 | Complete | 2026-05-12 |
| 9. Chat UX Core | v1.2 | 0/0 | 🔲 Planned | — |
| 10. SQLite History | v1.2 | 0/0 | 🔲 Planned | — |
| 11. Session Management | v1.2 | 0/0 | 🔲 Planned | — |
| 12. Polish & Edge Cases | v1.2 | 0/0 | 🔲 Planned | — |

**Total Progress: 100% (22/22 plans) — v1.2: 0/0 planned**

---

_Archive: `.planning/milestones/v1.0-ROADMAP.md`_
