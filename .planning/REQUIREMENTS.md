# Requirements: LiveTalking RAG Knowledge Base

## v1.0 Requirements (Shipped)

### FR-1: Knowledge Base Construction
- **FR-1.1** 支持从本地文档（PDF、TXT、Markdown、Word）导入知识 ✓
- **FR-1.2** 支持从数据库（MySQL、PostgreSQL、SQLite）导入知识 ✓
- **FR-1.3** 支持从 REST API 服务获取知识 ✓
- **FR-1.4** 支持文档分块（chunking）配置 ✓
- **FR-1.5** 支持增量更新知识库 ✓

### FR-2: Vector Embedding
- **FR-2.1** 支持多种 Embedding 模型选择 ✓
- **FR-2.2** 支持使用 DashScope/OpenAI Embedding API ✓
- **FR-2.3** 支持本地 Embedding 模型（如 text2vec） ✓
- **FR-2.4** 向量存储支持持久化 ✓

### FR-3: Retrieval
- **FR-3.1** 支持语义相似度检索（top-k） ✓
- **FR-3.2** 检索延迟 < 500ms ✓
- **FR-3.3** 支持检索结果相关性评分 ✓
- **FR-3.4** 支持元数据过滤 ✓

### FR-4: LLM Integration
- **FR-4.1** 在 chat 模式自动注入知识库上下文 ✓
- **FR-4.2** 保持现有流式输出机制 ✓
- **FR-4.3** 支持多轮对话上下文管理 ✓
- **FR-4.4** 兼容现有 echo 模式（无知识库检索） ✓

### FR-5: Configuration
- **FR-5.1** 支持通过 CLI 参数启用/禁用知识库 ✓
- **FR-5.2** 支持配置知识库路径 ✓
- **FR-5.3** 支持配置检索参数（top-k, threshold） ✓
- **FR-5.4** 支持环境变量配置 ✓

---

## v1.1 Requirements (Current Milestone)

### Graceful Exit（优雅退出）

- [ ] **EXIT-01**: 用户按 Ctrl+C 后，服务应在 5 秒内完全退出，释放 8010 端口
- [ ] **EXIT-02**: 退出时所有后台线程（avatar session、output 模块）应正确停止
- [ ] **EXIT-03**: 退出时应清理所有资源（WebRTC 连接、临时文件等）

### RAG Mode Toggle（RAG 模式切换）

- [ ] **RAG-01**: Dashboard 前端添加 RAG 模式切换按钮
- [ ] **RAG-02**: 支持"仅 RAG"模式 - 只使用知识库内容回答
- [ ] **RAG-03**: 支持"RAG+模型知识"模式 - 同时使用知识库和 LLM 自身知识
- [ ] **RAG-04**: 模式状态应持久化（刷新页面后保持选择）
- [ ] **RAG-05**: API 端点 `/set_rag_mode` 支持模式切换

---

## Out of Scope

- 实时知识库更新（WebSocket 推送）
- 多租户知识库隔离
- 知识库管理后台

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| EXIT-01 | Phase 7 | Pending |
| EXIT-02 | Phase 7 | Pending |
| EXIT-03 | Phase 7 | Pending |
| RAG-01 | Phase 8 | Pending |
| RAG-02 | Phase 8 | Pending |
| RAG-03 | Phase 8 | Pending |
| RAG-04 | Phase 8 | Pending |
| RAG-05 | Phase 8 | Pending |

**Coverage:**
- v1.1 requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-12*
*Last updated: 2026-05-12 after v1.1 milestone start*
