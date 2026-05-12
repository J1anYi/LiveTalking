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

**Total Progress: 100% (22/22 plans)**

---

_Archive: `.planning/milestones/v1.0-ROADMAP.md`_
