# Phase 3: Data Source Connectors - Context

**Gathered:** 2026-05-12
**Status:** Ready for planning

<domain>
## Phase Boundary

实现多种数据源连接器，扩展现有 FileLoader 功能，支持数据库和 API 数据源的知识获取。

**In scope:**
- 数据库连接器（SQLite、MySQL、PostgreSQL）
- REST API 连接器
- DOCX 文档格式支持
- 数据源配置管理
- 统一的加载器接口（遵循 DocumentLoader Protocol）

**Out of scope:**
- 实时数据同步（WebSocket 推送）
- 数据源管理 UI
- 多租户数据隔离

</domain>

<decisions>
## Implementation Decisions

### Database Connector Architecture
- **D-01:** 使用统一 `BaseDatabaseConnector` 基类 + 数据库特定实现
- **D-02:** 遵循现有 `DocumentLoader` Protocol 模式（`load() -> list[tuple[str, dict]]`）
- **D-03:** 使用 SQL 查询配置（非 ORM），保持轻量级

### Database Priority
- **D-04:** Phase 3 首先实现 SQLite（无额外依赖，满足 ROADMAP 要求）
- **D-05:** MySQL/PostgreSQL 作为可选扩展，需要额外依赖

### API Connector Design
- **D-06:** 简单 REST API fetcher，支持 GET/POST 请求
- **D-07:** 配置支持：`url`, `method`, `headers`, `body`, `data_path`（JSONPath 提取数据）
- **D-08:** 支持 API 认证（Bearer token, API key）

### Document Format Extension
- **D-09:** 扩展 FileLoader 支持 DOCX 格式（使用 python-docx 库）
- **D-10:** DOCX 文档按段落分块，保留标题层级作为 metadata

### Configuration Management
- **D-11:** 使用 YAML 配置文件管理多数据源
- **D-12:** 数据源注册表支持动态加载（基于 `source_type` 字段）
- **D-13:** 支持数据源启用/禁用开关

### Claude's Discretion
- 数据库连接池配置（使用标准库或简单实现）
- API 请求超时和重试策略
- 错误处理和日志记录方式

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Architecture
- `rag/__init__.py` — DocumentLoader Protocol 定义
- `rag/loaders/file_loader.py` — 现有 FileLoader 实现（作为参考模板）
- `rag/retriever.py` — RAGRetriever.ingest() 摄入接口

### Project Requirements
- `.planning/REQUIREMENTS.md` — FR-1.1 ~ FR-1.3 数据源需求
- `.planning/ROADMAP.md` — Phase 3 成功标准

### Prior Phase Context
- `.planning/phases/02-core-rag/02-SUMMARY.md` — Phase 2 实现总结

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `DocumentLoader` Protocol (`rag/__init__.py:39-41`) — 数据加载器接口，新连接器需实现
- `FileLoader` (`rag/loaders/file_loader.py`) — 现有文件加载器，可扩展 DOCX 支持
- `RAGRetriever.ingest()` (`rag/retriever.py`) — 文档摄入入口

### Established Patterns
- Protocol-based 类型定义（`@runtime_checkable`）
- 元数据返回格式：`{"source": str, "type": str, ...}`
- 错误处理：抛出具体异常（ValueError, FileNotFoundError）

### Integration Points
- `rag/loaders/__init__.py` — 需要导出新连接器
- `rag/__init__.py` — 需要导出公共 API
- requirements.txt — 需要添加新依赖

</code_context>

<specifics>
## Specific Ideas

- 数据库连接器返回的每一行作为一个文档块
- API 连接器支持分页（通过 `next_page_path` 配置）
- 数据源配置支持环境变量替换（如 `${DB_PASSWORD}`）

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-data-source-connectors*
*Context gathered: 2026-05-12*
