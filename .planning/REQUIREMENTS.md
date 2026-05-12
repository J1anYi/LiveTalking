# Requirements: LiveTalking RAG Knowledge Base

## Functional Requirements

### FR-1: Knowledge Base Construction
- **FR-1.1** 支持从本地文档（PDF、TXT、Markdown、Word）导入知识
- **FR-1.2** 支持从数据库（MySQL、PostgreSQL、SQLite）导入知识
- **FR-1.3** 支持从 REST API 服务获取知识
- **FR-1.4** 支持文档分块（chunking）配置
- **FR-1.5** 支持增量更新知识库

### FR-2: Vector Embedding
- **FR-2.1** 支持多种 Embedding 模型选择
- **FR-2.2** 支持使用 DashScope/OpenAI Embedding API
- **FR-2.3** 支持本地 Embedding 模型（如 text2vec）
- **FR-2.4** 向量存储支持持久化

### FR-3: Retrieval
- **FR-3.1** 支持语义相似度检索（top-k）
- **FR-3.2** 检索延迟 < 500ms
- **FR-3.3** 支持检索结果相关性评分
- **FR-3.4** 支持元数据过滤

### FR-4: LLM Integration
- **FR-4.1** 在 chat 模式自动注入知识库上下文
- **FR-4.2** 保持现有流式输出机制
- **FR-4.3** 支持多轮对话上下文管理
- **FR-4.4** 兼容现有 echo 模式（无知识库检索）

### FR-5: Configuration
- **FR-5.1** 支持通过 CLI 参数启用/禁用知识库
- **FR-5.2** 支持配置知识库路径
- **FR-5.3** 支持配置检索参数（top-k, threshold）
- **FR-5.4** 支持环境变量配置

## Non-Functional Requirements

### NFR-1: Performance
- 检索延迟 < 500ms（P95）
- 向量索引构建支持增量更新
- 内存占用 < 2GB（100万向量）

### NFR-2: Compatibility
- Python 3.10+
- 兼容现有 LiveTalking 架构
- 支持所有现有传输协议（WebRTC/RTMP/VirtualCam）

### NFR-3: Maintainability
- 代码符合现有项目规范
- 添加必要日志记录
- 提供使用文档

## Technical Decisions (To Research)

### TD-1: Vector Database
Options:
- **ChromaDB**: 轻量级，易于集成，支持本地持久化
- **FAISS**: 高性能，适合大规模向量检索
- **Milvus**: 分布式，适合企业级部署

**Decision Criteria**: 
- 易用性与集成复杂度
- 性能（检索延迟、内存占用）
- 社区活跃度与文档质量

### TD-2: Embedding Model
Options:
- **DashScope Embedding API**: 与现有 LLM 服务一致
- **OpenAI text-embedding-3**: 高质量，但需翻墙
- **text2vec-base-chinese**: 开源本地模型，中文优化

**Decision Criteria**:
- 中文支持质量
- 成本（API vs 本地）
- 延迟

### TD-3: Document Chunking Strategy
Options:
- **固定长度分块**: 简单，但可能切断语义
- **语义分块**: 基于段落/句子，语义完整
- **滑动窗口**: 有重叠，减少信息丢失

**Decision Criteria**:
- 检索精度
- 实现复杂度

## Out of Scope

- 前端界面改动
- 实时知识库更新（WebSocket 推送）
- 多租户知识库隔离
- 知识库管理后台
