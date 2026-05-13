# Requirements: LiveTalking RAG Knowledge Base

**Defined:** 2026-05-12
**Core Value:** 数字人在对话时能基于知识库内容回答问题，具备完整的对话交互体验

## v1.0 Requirements (Shipped)

### FR-1: Knowledge Base Construction
- ✅ **FR-1.1** 支持从本地文档（PDF、TXT、Markdown、Word）导入知识
- ✅ **FR-1.2** 支持从数据库（MySQL、PostgreSQL、SQLite）导入知识
- ✅ **FR-1.3** 支持从 REST API 服务获取知识
- ✅ **FR-1.4** 支持文档分块（chunking）配置
- ✅ **FR-1.5** 支持增量更新知识库

### FR-2: Vector Embedding
- ✅ **FR-2.1** 支持多种 Embedding 模型选择
- ✅ **FR-2.2** 支持使用 DashScope/OpenAI Embedding API
- ✅ **FR-2.3** 支持本地 Embedding 模型（如 text2vec）
- ✅ **FR-2.4** 向量存储支持持久化

### FR-3: Retrieval
- ✅ **FR-3.1** 支持语义相似度检索（top-k）
- ✅ **FR-3.2** 检索延迟 < 500ms
- ✅ **FR-3.3** 支持检索结果相关性评分
- ✅ **FR-3.4** 支持元数据过滤

### FR-4: LLM Integration
- ✅ **FR-4.1** 在 chat 模式自动注入知识库上下文
- ✅ **FR-4.2** 保持现有流式输出机制
- ✅ **FR-4.3** 支持多轮对话上下文管理
- ✅ **FR-4.4** 兼容现有 echo 模式（无知识库检索）

### FR-5: Configuration
- ✅ **FR-5.1** 支持通过 CLI 参数启用/禁用知识库
- ✅ **FR-5.2** 支持配置知识库路径
- ✅ **FR-5.3** 支持配置检索参数（top-k, threshold）
- ✅ **FR-5.4** 支持环境变量配置

## v1.1 Requirements (Shipped)

### Graceful Exit
- ✅ **EXIT-01**: Ctrl+C 后服务在 5 秒内完全退出，释放 8010 端口
- ✅ **EXIT-02**: 退出时所有后台线程正确停止
- ✅ **EXIT-03**: 退出时清理所有资源

### RAG Mode Toggle
- ✅ **RAG-01**: Dashboard 前端添加 RAG 模式切换按钮
- ✅ **RAG-02**: 支持"仅 RAG"模式
- ✅ **RAG-03**: 支持"RAG+模型知识"模式
- ✅ **RAG-04**: 模式状态持久化（刷新保持）
- ✅ **RAG-05**: API 端点 `/set_rag_mode` 完成

## v1.2 Requirements

### Chat UX 核心体验

- [x] **CHAT-01**: SSE 端点推送 LLM 流式文字到前端，前端 EventSource 逐 chunk 追加到气泡
- [x] **CHAT-02**: 消息气泡 UI，user 和 assistant 消息视觉区分（左右对齐/不同底色）
- [x] **CHAT-03**: 消息状态指示（发送中 loading / 完成 / 中断 / 错误）
- [x] **CHAT-04**: 自动滚动 + 用户滚动检测（仅用户位于底部时自动滚）
- [x] **CHAT-05**: 打断/中断指示，中断消息标记为"已中断"并显示 UI 提示
- [x] **CHAT-06**: Markdown 渲染（marked.js + DOMPurify），视听分离（文字富文本、TTS 朗读纯文本）

### 历史记录持久化

- [x] **HIST-01**: SQLite 数据库（conversations + messages 两张表），aiosqlite async 访问
- [x] **HIST-02**: API 端点：保存消息 / 获取历史（分页）/ 列表会话 / 删除会话
- [x] **HIST-03**: LLM streaming 完成后自动保存到 DB，中断时标记 `is_interrupted`
- [x] **HIST-04**: Session 启动时从 DB 加载历史到 `_llm_history`，双数据源一致
- [x] **HIST-05**: 线程安全（asyncio.Lock + WAL journal mode），自增 `seq` 列排序

### 会话管理

- [x] **CONV-01**: 对话侧边栏（会话列表，按时间排序，显示摘要和消息数）
- [x] **CONV-02**: 新建/切换/删除会话
- [x] **CONV-03**: 历史滚动加载（分页，`before_id` 参数，IntersectionObserver）
- [x] **CONV-04**: 首次 `/human` 调用时自动创建会话

### 前端框架

- [x] **UI-01**: Alpine.js 集成（CDN 引入），x-for/x-model/x-show 驱动聊天面板
- [x] **UI-02**: 消息气泡 CSS 样式 + 平滑过渡动画
- [x] **UI-03**: 时间戳显示（同天 HH:MM，跨天 月/日 时:分）
- [x] **UI-04**: 前端发送按钮 debounce，防止重复提交

## v1.3 Requirements

### 前端重构 (UI)

- [ ] **UI-05**: 新配色方案（暖白 `#f5f0eb` 背景 + 柔和紫 `#8B8CF8` 点缀，替代 `#4361ee` 蓝色调）
- [ ] **UI-06**: 视频+对话一体化布局（统一圆角白色卡片 `max-w-7xl` 居中，视觉融合）
- [ ] **UI-07**: RAG 模式切换移至顶部或对话框上方，触手可及
- [ ] **UI-08**: 对话框扩大至 6/12 分栏，气泡更大、间距更舒适
- [ ] **UI-09**: 响应式适配（桌面/平板），过渡动效平滑

## v2 Requirements

Deferred to future milestone.

- **音频波形可视化**：数字人说话时气泡旁显示电平条
- **多模态消息**：用户可发送图片，数字人回复含视觉理解
- **会话导出**：导出 JSON/Markdown/TXT
- **全文搜索**：跨会话消息搜索

## Out of Scope

| Feature | Reason |
|---------|--------|
| 富文本编辑器（Tiptap/Quill） | 用户输入纯文本或语音即可，过度工程 |
| WebSocket 全双工通信 | SSE (EventSource) 更轻量，足以满足单向推送需求 |
| 用户认证/登录系统 | 单用户本地部署，不需要 JWT/OAuth |
| 实时协作/多用户同屏 | 数字人 1:1 交互，非多人聊天 |
| PWA / Service Worker | 服务端是流媒体服务，非 SPA |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CHAT-01 | Phase 9 | Complete |
| CHAT-02 | Phase 9 | Complete |
| CHAT-04 | Phase 9 | Complete |
| CHAT-05 | Phase 11 | Complete |
| CHAT-03 | Phase 12 | Complete |
| CHAT-06 | Phase 12 | Complete |
| HIST-01 | Phase 10 | Complete |
| HIST-02 | Phase 10 | Complete |
| HIST-03 | Phase 10 | Complete |
| HIST-04 | Phase 10 | Complete |
| HIST-05 | Phase 10 | Complete |
| CONV-01 | Phase 11 | Complete |
| CONV-02 | Phase 11 | Complete |
| CONV-03 | Phase 11 | Complete |
| CONV-04 | Phase 11 | Complete |
| UI-01 | Phase 9 | Complete |
| UI-02 | Phase 9 | Complete |
| UI-03 | Phase 9 | Complete |
| UI-04 | Phase 10 | Complete |
| UI-05 | Phase 13 | Pending |
| UI-06 | Phase 13 | Pending |
| UI-07 | Phase 13 | Pending |
| UI-08 | Phase 13 | Pending |
| UI-09 | Phase 13 | Pending |

**Coverage:**
- v1.3 requirements: 5 total
- Mapped to phases: 5
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-12*
*Last updated: 2026-05-12 after v1.2 definition*
