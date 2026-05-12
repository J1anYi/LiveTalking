# Phase 5: CLI & Configuration - Context

**Gathered:** 2026-05-12
**Status:** Ready for planning

<domain>
## Phase Boundary

完善 RAG 模块的配置支持，添加环境变量和 YAML 配置文件支持，实现配置优先级机制，并更新相关文档。

**In scope:**
- 环境变量配置支持 (RAG_*)
- YAML 配置文件支持 (data/rag_config.yaml)
- 配置优先级机制 (CLI > 环境变量 > 配置文件)
- CLI 参数 --rag_config 指定配置文件
- 文档更新 (README, requirements.txt, 示例配置)

**Out of scope:**
- 知识库管理界面
- 动态配置热更新
- 新的数据源类型

**Note:** CLI 参数 (--rag_enabled, --rag_top_k, --rag_persist_dir, --rag_collection) 已在 Phase 4 实现，本阶段在此基础上扩展。

</domain>

<decisions>
## Implementation Decisions

### Configuration Methods
- **D-01:** 支持三种配置方式：CLI 参数、环境变量、YAML 配置文件
  - **Why:** 满足不同部署场景需求，CLI 适合开发测试，环境变量适合容器化部署，配置文件适合生产环境
  - **How to apply:** 在 config.py 中实现配置加载优先级逻辑

### Priority Mechanism
- **D-02:** 配置优先级：CLI > 环境变量 > 配置文件
  - **Why:** CLI 参数最灵活，应覆盖其他配置；环境变量次之；配置文件作为默认值
  - **How to apply:** 按顺序加载配置，后加载的不覆盖已存在的值

### Environment Variables
- **D-03:** 环境变量使用 RAG_* 前缀
  - **Why:** 简洁明了，与功能模块对应
  - **How to apply:** 
    - RAG_ENABLED (bool)
    - RAG_TOP_K (int)
    - RAG_PERSIST_DIR (str)
    - RAG_COLLECTION (str)
    - RAG_CONFIG_FILE (str, optional)

### Config File
- **D-04:** 使用 YAML 格式，默认路径 data/rag_config.yaml
  - **Why:** 与 Phase 3 数据源配置风格一致，易于阅读和编辑
  - **How to apply:** 添加 PyYAML 依赖，实现 YAML 配置加载函数

### CLI Parameter
- **D-05:** 添加 --rag_config 参数指定配置文件路径
  - **Why:** 灵活指定不同环境的配置文件
  - **How to apply:** 在 config.py 添加 --rag_config 参数

### Documentation
- **D-06:** 更新以下文档
  - 使用文档：README.md 或 docs/rag_usage.md
  - requirements.txt：添加 PyYAML 依赖
  - 示例配置：data/rag_config.yaml.example

### Claude's Discretion
- 配置文件不存在时的处理方式（警告并使用默认值 vs 报错）
- 配置值类型转换和验证
- 日志记录配置加载过程

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Implementation
- `config.py` — CLI 参数定义，需扩展配置加载逻辑
- `rag/__init__.py` — RAG 模块公共 API
- `.planning/phases/04-llm-integration/04-01-SUMMARY.md` — Phase 4 CLI 参数实现

### Prior Config Patterns
- `.planning/phases/03-data-source-connectors/example_sources.yaml` — Phase 3 数据源配置示例
- `data/avatars/` — 数据目录结构参考

### Project Requirements
- `.planning/REQUIREMENTS.md` — FR-5.4 环境变量配置需求

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `config.py` — 现有 argparse 配置，需扩展
- Phase 3 SourceConfig — YAML 配置解析模式可参考

### Established Patterns
- CLI 参数默认值覆盖机制
- os.environ.get() 环境变量读取
- argparse store_true action

### Integration Points
- `config.py:parse_args()` — 配置解析入口
- `app.py:main()` — 配置使用入口

</code_context>

<specifics>
## Specific Ideas

- 环境变量格式：
  ```bash
  RAG_ENABLED=true
  RAG_TOP_K=5
  RAG_PERSIST_DIR=./data/chromadb
  RAG_COLLECTION=knowledge_base
  ```

- YAML 配置示例：
  ```yaml
  rag:
    enabled: true
    top_k: 3
    persist_dir: ./data/chromadb
    collection: knowledge_base
  ```

- 配置加载顺序：
  1. 加载 YAML 配置文件（如果存在）
  2. 读取环境变量覆盖
  3. CLI 参数覆盖

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-cli-configuration*
*Context gathered: 2026-05-12*
