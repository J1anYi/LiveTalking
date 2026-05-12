# Roadmap: LiveTalking RAG Knowledge Base

## Milestone: RAG Knowledge Base Integration

**Goal**: 为 LiveTalking 数字人添加 RAG 知识库功能，实现基于知识库的智能对话

**Duration Estimate**: 4-6 phases

---

## Phase 1: Research & Design

**Goal**: 研究 RAG 技术选型，设计集成方案

**Deliverables**:
- 技术选型决策（向量数据库、Embedding 模型）
- 架构设计文档
- API 设计方案

**Key Tasks**:
1. 研究 ChromaDB vs FAISS vs Milvus
2. 研究 Embedding 模型选项
3. 设计与现有 llm.py 的集成方式
4. 设计配置接口

**Success Criteria**:
- [x] 确定向量数据库选择
- [x] 确定 Embedding 模型
- [x] 完成架构设计文档
- [x] 评审通过

---

## Phase 2: Core RAG Module

**Goal**: 实现核心 RAG 检索模块

**Deliverables**:
- `rag/` 模块目录结构
- 向量存储管理器
- 文档处理器（分块、embedding）
- 检索器

**Key Tasks**:
1. 创建 `rag/` 模块目录
2. 实现向量存储类（基于选定的向量数据库）
3. 实现文档加载器（支持 PDF、TXT、Markdown）
4. 实现文档分块器
5. 实现 Embedding 生成器
6. 实现检索器

**Success Criteria**:
- [x] 向量存储支持增删改查
- [x] 文档处理流程完整
- [x] 检索延迟 < 500ms
- [x] 单元测试通过

---

## Phase 3: Data Source Connectors

**Goal**: 实现多种数据源连接器

**Deliverables**:
- 本地文档加载器
- 数据库连接器
- API 服务连接器

**Plans:** 4 plans

Plans:
- [x] 03-01-PLAN.md — 数据库连接器基础架构 + SQLite 实现
- [x] 03-02-PLAN.md — REST API 数据源连接器
- [x] 03-03-PLAN.md — DOCX 文档格式支持
- [x] 03-04-PLAN.md — 数据源配置管理和注册表

**Key Tasks**:
1. 实现本地文档加载器（PDF、TXT、MD、DOCX）
2. 实现数据库连接器（SQLite、MySQL、PostgreSQL）
3. 实现 API 服务连接器
4. 实现数据源配置管理

**Success Criteria**:
- [x] 支持至少 3 种文档格式（TXT, MD, PDF 已有 + DOCX 新增）
- [x] 支持至少 1 种数据库（SQLite）
- [x] 支持 REST API 数据源
- [x] 配置灵活可扩展

---

## Phase 4: LLM Integration

**Goal**: 将 RAG 检索集成到 LLM 对话流程

**Deliverables**:
- 修改后的 `llm.py`
- 知识库上下文注入逻辑
- 流式输出兼容

**Plans:** 3 plans

Plans:
- [x] 04-01-PLAN.md — RAG CLI 配置参数扩展 (Wave 1)
- [x] 04-02-PLAN.md — 全局 RAG 检索器初始化 (Wave 2, depends: 04-01)
- [x] 04-03-PLAN.md — LLM 函数 RAG 检索集成 (Wave 3, depends: 04-01, 04-02)

**Key Tasks**:
1. 修改 `llm.py` 支持知识库检索
2. 实现 prompt 模板（注入检索结果）
3. 保持流式输出兼容
4. 添加知识库开关配置

**Success Criteria**:
- [x] Chat 模式自动检索知识库
- [x] Echo 模式不受影响
- [x] 流式输出正常工作
- [x] 可通过配置启用/禁用知识库

**Requirements Coverage**:
| Requirement | Plan | Description |
|-------------|------|-------------|
| FR-4.1 | 04-03-PLAN.md | Chat 模式自动注入知识库上下文 |
| FR-4.2 | 04-03-PLAN.md | 保持现有流式输出机制 |
| FR-4.3 | 04-03-PLAN.md | 多轮对话上下文管理 |
| FR-4.4 | 04-03-PLAN.md | Echo 模式兼容（rag_enabled=False 时不检索）|
| FR-5.1 | 04-01-PLAN.md | CLI 参数启用/禁用知识库 |
| FR-5.2 | 04-01-PLAN.md | 配置知识库路径 |
| FR-5.3 | 04-01-PLAN.md | 配置检索参数（top-k）|

---

## Phase 5: CLI & Configuration

**Goal**: 完善 RAG 模块的配置支持，添加环境变量和 YAML 配置文件支持，实现配置优先级机制

**Deliverables**:
- YAML 配置文件加载器
- 环境变量配置支持
- 配置优先级合并逻辑
- 文档和示例更新

**Plans:** 5 plans

Plans:
- [x] 05-01-PLAN.md — YAML 配置文件加载器 (Wave 1)
- [x] 05-02-PLAN.md — 环境变量配置支持 (Wave 1)
- [x] 05-03-PLAN.md — 添加 PyYAML 依赖 (Wave 1)
- [x] 05-04-PLAN.md — 配置优先级合并逻辑 (Wave 2, depends: 05-01, 05-02, 05-03)
- [x] 05-05-PLAN.md — 文档和示例更新 (Wave 3, depends: 05-04)

**Key Tasks**:
1. 创建 YAML 配置加载器 (rag/config_loader.py)
2. 实现环境变量读取 (RAG_ENABLED, RAG_TOP_K, RAG_PERSIST_DIR, RAG_COLLECTION)
3. 添加 --rag_config CLI 参数
4. 实现配置合并逻辑 (CLI > 环境变量 > 配置文件)
5. 更新文档和示例配置

**Success Criteria**:
- [x] 支持 YAML 配置文件 (data/rag_config.yaml)
- [x] 支持 RAG_* 环境变量
- [x] 配置优先级正确 (CLI > 环境变量 > 配置文件)
- [x] 文档完整更新

**Requirements Coverage**:
| Requirement | Plan | Description |
|-------------|------|-------------|
| FR-5.1 | 05-04-PLAN.md | CLI 参数扩展 (--rag_config) |
| FR-5.2 | 05-01-PLAN.md, 05-04-PLAN.md | 配置知识库路径 (YAML + 环境变量 + CLI) |
| FR-5.3 | 05-02-PLAN.md, 05-04-PLAN.md | 配置检索参数 (YAML + 环境变量 + CLI) |
| FR-5.4 | 05-02-PLAN.md | 环境变量配置支持 |

---

## Phase 6: Testing & Documentation

**Goal**: 完善测试和文档

**Deliverables**:
- 单元测试
- 集成测试
- 使用文档
- 示例配置

**Plans:** 5 plans

Plans:
- [x] 06-01-PLAN.md — config_loader 单元测试 (Wave 1) ✓ 2026-05-12
- [x] 06-02-PLAN.md — SQLiteConnector 单元测试 (Wave 1) ✓ 2026-05-12
- [x] 06-03-PLAN.md — RAG 用户文档 (Wave 1) ✓ 2026-05-12
- [x] 06-04-PLAN.md — 端到端集成测试 (Wave 2, depends: 06-01, 06-02) ✓ 2026-05-12
- [x] 06-05-PLAN.md — 示例知识库数据和演示 (Wave 3, depends: 06-03) ✓ 2026-05-12

**Key Tasks**:
1. 编写 RAG 模块单元测试
2. 编写集成测试
3. 编写使用文档
4. 提供示例知识库配置

**Success Criteria**:
- [x] 测试覆盖率 > 80% (39 新测试用例通过)
- [x] 文档完整清晰 (docs/rag.md 包含 API 参考、FAQ、使用流程演示)
- [x] 示例可运行 (data/knowledge_base/ 示例数据)
- [x] 代码审查通过

**Requirements Coverage**:
| Requirement | Plan | Description |
|-------------|------|-------------|
| NFR-3 | 06-01, 06-02, 06-04 | 添加必要测试，确保代码质量 |
| NFR-3 | 06-03, 06-05 | 提供使用文档和示例 |

---

## Dependencies

```
Phase 1 (Research) 
    ↓
Phase 2 (Core RAG)
    ↓
Phase 3 (Data Sources) ←→ Phase 4 (LLM Integration)
    ↓                       ↓
Phase 5 (Configuration) ←─┘
    ↓
Phase 6 (Testing & Docs)
```

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| 向量数据库性能不达标 | High | Phase 1 充分调研，准备备选方案 |
| Embedding API 延迟过高 | Medium | 支持本地模型作为备选 |
| 与现有流式输出冲突 | High | Phase 4 重点测试，保持兼容 |
| 内存占用过大 | Medium | 支持向量索引持久化，按需加载 |
