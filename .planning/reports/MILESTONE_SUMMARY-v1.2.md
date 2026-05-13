# Milestone v1.2 — LiveTalking Chat UI & History

**Generated:** 2026-05-12
**Purpose:** Team onboarding and project review

---

## 1. Project Overview

为 LiveTalking 数字人项目添加完整聊天界面和对话历史持久化功能。v1.2 在 v1.1 RAG 知识库基础上，大幅提升了用户交互体验。

**里程碑目标:** 重构聊天界面 + 添加对话历史持久化存储
**状态:** ✅ 已全部完成

---

## 2. Architecture & Technical Decisions

- **SSE 流式推送 (Server-Sent Events):** 取代 WebSocket，单方向推送 LLM 流式文字到前端，EventSource 自动重连
  - *Phase: 09-chat-ux-core*
- **Alpine.js 前端框架 (CDN):** 零构建步骤，15KB，与现有 jQuery/Bootstrap 共存，`x-for`/`x-model` 驱动聊天面板
  - *Phase: 09-chat-ux-core*
- **aiosqlite 异步数据库:** 替代同步 sqlite3，不阻塞 aiohttp 事件循环，WAL journal mode 提升并发
  - *Phase: 10-sqlite-history*
- **ChatHistory 单例模块:** `server/chat_db.py` 独立封装，`conversations` + `messages` 两张表，自增 seq 列保证顺序
  - *Phase: 10-sqlite-history*
- **线程安全:** `asyncio.Lock` + WAL 模式，`llm_response()` 在线程池中创建独立事件循环
  - *Phase: 10-sqlite-history*
- **写穿透策略:** LLM streaming 完成后一次性写入 DB，非逐 segment 写入，避免中断时保存不完整回复
  - *Phase: 10-sqlite-history*
- **视听分离渲染:** 前端 marked.js 渲染 Markdown 富文本，TTS 用 `clean_text_for_tts()` 朗读纯文本
  - *Phase: 12-polish-edge-cases*

---

## 3. Phases Delivered

| Phase | Name | Status | One-Liner |
|-------|------|--------|-----------|
| 9 | Chat UX Core | ✅ Complete | SSE 流式推送 + 消息气泡 UI + Alpine.js 前端框架集成 |
| 10 | SQLite History | ✅ Complete | aiosqlite 持久化 + History API + LLM 保存集成 |
| 11 | Session Management | ✅ Complete | 对话侧边栏 + 新建/切换/删除会话 |
| 12 | Polish & Edge Cases | ✅ Complete | Markdown 渲染、消息状态、防重、边防情况 |

---

## 4. Requirements Coverage

### Chat UX 核心体验
- ✅ **CHAT-01**: SSE 推送 LLM 流式文字到前端
- ✅ **CHAT-02**: 消息气泡 UI (user/assistant 视觉区分)
- ✅ **CHAT-03**: 消息状态指示 (发送中/完成/中断/错误)
- ✅ **CHAT-04**: 自动滚动 + 用户滚动检测
- ✅ **CHAT-05**: 打断/中断指示
- ✅ **CHAT-06**: Markdown 渲染 (marked.js + DOMPurify)

### 历史记录持久化
- ✅ **HIST-01**: SQLite conversations + messages 表，aiosqlite async 访问
- ✅ **HIST-02**: API 端点 (创建/列表/获取/删除会话)
- ✅ **HIST-03**: LLM streaming 完成后自动保存，中断标记 is_interrupted
- ✅ **HIST-04**: Session 从 DB 加载历史，双数据源一致
- ✅ **HIST-05**: 线程安全 + WAL + 自增 seq 排序

### 会话管理
- ✅ **CONV-01**: 对话侧边栏 (按时间排序、摘要、消息数)
- ✅ **CONV-02**: 新建/切换/删除会话
- ✅ **CONV-03**: 历史滚动加载 (分页)
- ✅ **CONV-04**: 首次 `/human` 自动创建会话

### 前端框架
- ✅ **UI-01**: Alpine.js CDN 集成
- ✅ **UI-02**: 消息气泡 CSS + 过渡动画
- ✅ **UI-03**: 时间戳显示
- ✅ **UI-04**: 发送按钮 debounce 防重

**覆盖: 19/19 需求全部完成**

---

## 5. Key Decisions Log

| ID | Decision | Rationale | Phase |
|----|----------|-----------|-------|
| D-01 | SSE over WebSocket | 单方向推送，EventSource 自动重连，更轻量 | 09 |
| D-02 | Alpine.js CDN over React/Vue | 零构建，15KB，与现有 jQuery 共存 | 09 |
| D-03 | aiosqlite over sqlite3 | 不阻塞 asyncio 事件循环，原生 async/await | 10 |
| D-04 | 完成后一次性写入 DB | 避免中断时保存不完整回复 | 10 |
| D-05 | asyncio.Lock 线程安全 | llm_response 在线程池运行 | 10 |
| D-06 | 自增 seq 列排序 | 防止异步写入导致消息乱序 | 10 |
| D-07 | marked.js + DOMPurify | 轻量 Markdown 渲染 + XSS 防护 | 12 |
| D-08 | 线程内创建独立事件循环 | 避免跨线程 `get_event_loop()` 失败 | 10 |

---

## 6. Tech Debt & Deferred Items

- **Playwright 浏览器未安装:** 前端 UI 自动化测试无法运行 (`playwright install` needed)
- **SSE 长连接管理:** 30s 超时静默断开，高频交互场景可考虑调整超时时间
- **历史加载全量返回:** `get_messages` 返回全部消息，大量消息时可加分页
- **无 ESModule 方案:** 当前脚本通过 `<script>` 标签加载，无模块化构建

---

## 7. Getting Started

- **Run the project:**
  ```bash
  set DASHSCOPE_API_KEY=sk-xxx
  python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar1 --rag_enabled
  ```
- **Key new files:**
  - `server/chat_db.py` — aiosqlite 历史记录模块 (singleton)
  - `server/sse_manager.py` — SSE 连接管理器
- **Key modified files:**
  - `llm.py` — SSE 推送 + DB 保存 + 线程内事件循环
  - `server/routes.py` — SSE 端点 + 4 个会话 API
  - `web/dashboard.html` — Alpine.js 聊天面板 + 会话侧边栏
  - `app.py` — ChatHistory 初始化
- **Tests:**
  ```bash
  pytest tests/ -v
  ```
- **Test coverage gaps:**
  - SSE 端点 — 需手动或 Playwright 验证
  - Chat UI 前端 — 无自动化测试
  - aiosqlite 模块 — 需 mock 测试

---

## Stats

| Metric | Value |
|--------|-------|
| **Timeline** | 2026-05-12 (single day, ~4 hours) |
| **Phases** | 4 / 4 complete |
| **Commits** | 29 |
| **Files changed (code)** | 8 (+628 / -42) |
| **Contributors** | J1anYi |
