# Milestone v1.1 — LiveTalking Bug Fixes & UX Enhancement

**Generated:** 2026-05-12
**Purpose:** Team onboarding and project review

---

## 1. Project Overview

为 LiveTalking 数字人项目添加 RAG（检索增强生成）知识库功能，使数字人对话时能基于知识库内容回答问题。v1.1 是 v1.0 RAG 知识库基础版的改进里程碑。

**里程碑目标:** 修复优雅退出问题并添加 RAG 模式切换功能
**状态:** ✅ 已全部完成

---

## 2. Architecture & Technical Decisions

- **Signal Handling (asyncio.Event):** Phase 7 使用 `asyncio.Event` 作为关闭信号，处理 Windows `NotImplementedError` 回退到 `signal.signal()`
  - *Phase: 07-graceful-exit*
- **Per-Session RAG Mode:** Phase 8 在 `SessionManager` 中按 session ID 跟踪 RAG 模式，支持不同会话使用不同模式
  - *Phase: 08-rag-mode-toggle*
- **localStorage Persistence:** 前端模式选择持久化在浏览器 `localStorage`，页面刷新后保持
  - *Phase: 08-rag-mode-toggle*
- **RAG+Model 混合 Prompt:** 使用 `"参考信息:\n{context}\n\n用户问题: {message}\n\n请结合参考信息和你的知识回答问题:"` 格式，允许多模型同时使用知识库和自身知识
  - *Phase: 08-rag-mode-toggle*
- **DashScope OpenAI 兼容模式:** LLM 和 Embedding 共用 `DASHSCOPE_API_KEY` 环境变量，通过 DashScope 的 OpenAI 兼容端点调用
  - *全域*

---

## 3. Phases Delivered

| Phase | Name | Status | One-Liner |
|-------|------|--------|-----------|
| 7 | Graceful Exit | ✅ Complete | 修复 Ctrl+C 后进程无法正常退出，通过信号处理器、会话清理和线程超时机制实现优雅退出 |
| 8 | RAG Mode Toggle | ✅ Complete | 添加 RAG 模式切换，支持"RAG-only"和"RAG+Model"两种模式，含 API 端点和前端 UI 控制 |

---

## 4. Requirements Coverage

### Graceful Exit（优雅退出）
- ✅ **EXIT-01**: Ctrl+C 后服务在 5 秒内完全退出，释放 8010 端口
- ✅ **EXIT-02**: 退出时所有后台线程正确停止
- ✅ **EXIT-03**: 退出时清理所有资源（WebRTC 连接、临时文件等）

### RAG Mode Toggle（RAG 模式切换）
- ✅ **RAG-01**: Dashboard 前端添加 RAG 模式切换按钮
- ✅ **RAG-02**: 支持"仅 RAG"模式
- ✅ **RAG-03**: 支持"RAG+模型知识"模式
- ✅ **RAG-04**: 模式状态持久化（刷新保持）
- ✅ **RAG-05**: API 端点 `/set_rag_mode` 完成

**覆盖: 8/8 需求全部完成**

---

## 5. Key Decisions Log

| ID | Decision | Rationale | Phase |
|----|----------|-----------|-------|
| D-01 | 使用 asyncio.Event 做关闭信号 | 异步友好，避免竞争条件 | 07 |
| D-02 | Signal handler 兼容 Windows | Windows 不支持 add_signal_handler，使用 signal.signal() 回退 | 07 |
| D-03 | 线程 join 添加 5 秒超时 | 防止死锁，保证强制退出能力 | 07 |
| D-04 | RAG 模式按 session 存储 | 支持多用户/多会话不同配置 | 08 |
| D-05 | 前端模式持久化用 localStorage | 零后端改动，刷新即恢复 | 08 |
| D-06 | RAG+Model 使用混合 prompt | 既可回答问题又能引用知识库 | 08 |
| D-07 | LLM 切换到 DashScope Qwen-Plus | 本地 LLM 服务端延迟高，DashScope 响应更快 | 08 |

---

## 6. Tech Debt & Deferred Items

- **首次回复延迟**: LLM TTFT（首 token 时间）仍有 1-8 秒波动，取决于服务端负载
- **Edge-TTS 可靠性**: 依赖微软 Edge-TTS API，可能因接口变更或限流导致服务中断（已知问题）
- **无前端错误提示**: 当 edge-tts 失败时，前端无用户可见的错误提示
- **RAG 模式无默认同步**: 重启后前端需从服务端获取模式（已在 debug 会话中修复）
- **回答溢出**: LLM 可能返回过长内容，已在 prompt 中加入"简短"约束

---

## 7. Getting Started

- **Run the project:**
  ```bash
  set DASHSCOPE_API_KEY=sk-xxx
  python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar1 --rag_enabled
  ```
- **Key directories:**
  - `rag/` — RAG 模块（Embedding、检索、向量存储）
  - `avatars/` — 数字人模型（wav2lip、musetalk 等）
  - `tts/` — TTS 引擎（edge_tts、cosyvoice 等）
  - `server/` — 服务器路由、会话管理、WebRTC
  - `web/` — 前端页面（dashboard.html、webrtcapi.html）
  - `data/avatars/` — 数字人 avatar 数据
- **Tests:**
  ```bash
  pytest tests/ -v
  ```
- **Where to look first:**
  - `llm.py` — LLM 响应入口（含 RAG prompt 构建、流式输出逻辑）
  - `app.py` — 服务启动入口
  - `server/routes.py` — API 路由定义
  - `server/session_manager.py` — 会话生命周期管理

---

## Stats

| Metric | Value |
|--------|-------|
| **Timeline** | 2026-05-12 16:53 → 2026-05-12 17:43 (~50 min) |
| **Phases** | 2 / 2 complete |
| **Commits** | 12 |
| **Files changed** | 7 (+164 / -13) |
| **Contributors** | J1anYi |
