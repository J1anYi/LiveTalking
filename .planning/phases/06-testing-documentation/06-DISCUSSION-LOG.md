# Phase 6: Testing & Documentation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-12
**Phase:** 06-testing-documentation
**Areas discussed:** 测试覆盖范围, 集成测试策略, 文档内容结构, 示例和演示

---

## 测试覆盖范围

| Option | Description | Selected |
|--------|-------------|----------|
| 全部补齐单元测试 | 为每个缺失模块创建完整单元测试，目标覆盖率 > 80% | |
| 核心模块优先 | 优先测试 config_loader 和 SQLiteConnector（关键路径），APILoader 和 SourceRegistry 可选 | ✓ |
| 仅集成测试 | 不新增单独单元测试，通过扩展 test_integration.py 覆盖新模块 | |

**User's choice:** 核心模块优先
**Notes:** 现有 6 个测试文件，缺失 APILoader、SQLiteConnector、SourceConfig、config_loader 的测试

---

## 集成测试策略 - API 依赖

| Option | Description | Selected |
|--------|-------------|----------|
| 完全 Mock | 所有测试使用 mock，不依赖外部服务，CI/CD 稳定 | |
| 部分真实 API | 关键路径使用真实 API，需要设置 DASHSCOPE_API_KEY 环境变量 | ✓ |
| 可选真实 API 测试 | 使用 pytest marker 区分，如 @pytest.mark.integration，可选择性运行 | |

**User's choice:** 部分真实 API
**Notes:** API Key: sk-a3451ca04a30450a97c5da171f6be961, Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1

---

## 端到端测试场景

| Option | Description | Selected |
|--------|-------------|----------|
| RAG 全流程测试 | 文档加载 → 分块 → Embedding → 存储 → 检索的完整流程 | ✓ |
| LLM 集成测试 | 配置加载 → 初始化 RAG → 检索集成（验证 Phase 4 集成） | ✓ |
| 配置系统测试 | YAML 配置 → 环境变量 → CLI 参数的优先级测试（验证 Phase 5） | ✓ |

**User's choice:** 全部选择
**Notes:** 三个场景都需要覆盖

---

## 文档内容

| Option | Description | Selected |
|--------|-------------|----------|
| 使用指南 | 快速开始、安装、基本用法，适合新用户 | ✓ |
| API 参考文档 | 所有公共类和函数的详细说明 | ✓ |
| FAQ/故障排除 | 常见问题解答，如配置问题、错误处理 | ✓ |
| 示例代码 | 配置示例、代码示例、完整使用示例 | |

**User's choice:** 使用指南, API 参考文档, FAQ/故障排除
**Notes:** 示例代码通过使用流程演示提供

---

## 文档位置

| Option | Description | Selected |
|--------|-------------|----------|
| 项目文档 | 在项目根目录创建 rag/README.md 或 docs/rag.md | ✓ |
| 模块文档 | 在 rag/ 模块目录创建 README.md | |
| 合并到主 README | 更新主 README.md 添加 RAG 章节 | |

**User's choice:** 项目文档
**Notes:** 独立文档便于维护

---

## 示例和演示

| Option | Description | Selected |
|--------|-------------|----------|
| 示例知识库数据 | 提供示例知识库文档（如 FAQ 文档、产品说明） | ✓ |
| 完整配置示例 | 完整的 YAML 配置示例（数据源、参数） | |
| 使用流程演示 | 从命令行启动到检索结果的完整流程 | ✓ |

**User's choice:** 示例知识库数据, 使用流程演示
**Notes:** 完整配置示例已在 Phase 5 提供 (rag_config.yaml.example)

---

## Claude's Discretion

- 测试覆盖率目标具体值（建议 80%+）
- 示例知识库数据的具体内容
- 是否添加 pytest marker 区分 mock 测试和真实 API 测试
- 文档是否需要中英文双语

## Deferred Ideas

None — discussion stayed within phase scope
