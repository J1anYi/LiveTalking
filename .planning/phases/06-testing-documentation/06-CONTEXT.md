# Phase 6: Testing & Documentation - Context

**Gathered:** 2026-05-12
**Status:** Ready for planning

<domain>
## Phase Boundary

完善 RAG 模块的测试覆盖和用户文档，确保代码质量和可用性。

**In scope:**
- 单元测试（补充缺失的核心模块测试）
- 集成测试（端到端流程验证）
- 使用文档（使用指南、API 参考、FAQ）
- 示例知识库数据和使用流程演示

**Out of scope:**
- 前端界面改动
- 新功能开发
- 性能基准测试（可作为后续阶段）

**Existing tests (6 files):**
- `tests/test_retriever.py` - RAGRetriever (16 tests)
- `tests/test_vector_store.py` - VectorStore (8 tests)
- `tests/test_embeddings.py` - DashScopeEmbedding (9 tests)
- `tests/test_document_processor.py` - DocumentProcessor (12 tests)
- `tests/test_file_loader.py` - FileLoader (12 tests)
- `tests/test_integration.py` - 集成测试 (7 tests)

**Missing tests (Phase 3 & 5 modules):**
- `APILoader` - 无测试
- `SQLiteConnector` / `BaseDatabaseConnector` - 无测试
- `SourceConfig`, `SourceRegistry` - 无测试
- `config_loader.py` - 无测试

</domain>

<decisions>
## Implementation Decisions

### Test Coverage Strategy
- **D-01:** 核心模块优先 - 优先为 config_loader 和 SQLiteConnector 创建单元测试
  - **Why:** 这两个模块是关键路径，影响配置加载和数据源连接
  - **How to apply:** 创建 test_config_loader.py 和 test_database_connector.py
- **D-02:** APILoader 和 SourceRegistry 测试可选
  - **Why:** APILoader 依赖外部 API，SourceRegistry 是配置管理，优先级较低
  - **How to apply:** 可通过集成测试覆盖，或后续补充

### Integration Test Strategy
- **D-03:** 部分真实 API 测试 - 使用真实 DashScope Embedding API
  - **Why:** 验证真实 API 调用的兼容性，发现 mock 无法覆盖的问题
  - **How to apply:** 设置 DASHSCOPE_API_KEY 环境变量运行集成测试
- **D-04:** API 配置
  - API Key: `sk-xxx`
  - Base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- **D-05:** 端到端测试覆盖三个场景
  - RAG 全流程测试：文档加载 → 分块 → Embedding → 存储 → 检索
  - LLM 集成测试：配置加载 → 初始化 RAG → 检索集成
  - 配置系统测试：YAML 配置 → 环境变量 → CLI 参数优先级

### Documentation Strategy
- **D-06:** 文档内容包含三个部分
  - 使用指南：快速开始、安装、基本用法
  - API 参考文档：所有公共类和函数的详细说明
  - FAQ/故障排除：常见问题解答
- **D-07:** 文档位置：项目文档 (`docs/rag.md` 或 `rag/README.md`)
  - **Why:** 独立文档便于维护，不与主 README 混淆
  - **How to apply:** 创建 `docs/rag.md` 或 `rag/README.md`

### Examples and Demos
- **D-08:** 提供示例知识库数据
  - **Why:** 用户可快速体验 RAG 功能，无需准备数据
  - **How to apply:** 在 `data/knowledge_base/` 目录提供示例文档（FAQ、产品说明等）
- **D-09:** 提供使用流程演示
  - **Why:** 展示从命令行启动到检索结果的完整流程
  - **How to apply:** 文档中包含完整的命令行示例和预期输出

### Claude's Discretion
- 测试覆盖率目标具体值（建议 80%+）
- 示例知识库数据的具体内容
- 是否添加 pytest marker 区分 mock 测试和真实 API 测试
- 文档是否需要中英文双语

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Test Structure
- `tests/test_integration.py` — 现有集成测试模式
- `tests/test_retriever.py` — 单元测试模式参考

### Prior Phase Implementations
- `.planning/phases/03-data-source-connectors/03-SUMMARY.md` — Phase 3 数据源实现
- `.planning/phases/04-llm-integration/04-SUMMARY.md` — Phase 4 LLM 集成实现
- `.planning/phases/05-cli-configuration/05-CONTEXT.md` — Phase 5 配置系统决策

### Project Requirements
- `.planning/REQUIREMENTS.md` — NFR-3 可维护性需求（添加必要日志记录、提供使用文档）

### RAG Module
- `rag/__init__.py` — 公共 API 定义
- `rag/config_loader.py` — 配置加载器（需测试）
- `rag/loaders/database_connector.py` — 数据库连接器（需测试）

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/test_integration.py` — 现有集成测试模式可扩展
- `pytest` + `unittest.mock` — 已建立的测试框架
- `data/rag_config.yaml.example` — 已有配置示例

### Established Patterns
- 测试文件命名：`test_<module>.py`
- Mock 使用：`patch.object()` 和 `Mock()`
- 临时目录：`tempfile.TemporaryDirectory()`

### Integration Points
- `tests/` — 测试文件目录
- `docs/` — 文档目录（需创建或确认存在）
- `data/knowledge_base/` — 示例知识库目录（需创建）

</code_context>

<specifics>
## Specific Ideas

- 使用 pytest marker 区分测试类型：
  ```python
  @pytest.mark.unit
  def test_something(): ...

  @pytest.mark.integration
  def test_real_api(): ...
  ```

- 示例知识库内容建议：
  - `data/knowledge_base/faq.txt` — 常见问题解答
  - `data/knowledge_base/product.md` — 产品功能说明

- 使用流程演示示例：
  ```bash
  # 1. 配置环境变量
  export DASHSCOPE_API_KEY=sk-xxx

  # 2. 运行应用
  python app.py --rag_enabled --rag_top_k 3

  # 3. 测试检索
  curl -X POST http://localhost:8010/human -d '{"text": "什么是 RAG？"}'
  ```

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-testing-documentation*
*Context gathered: 2026-05-12*
