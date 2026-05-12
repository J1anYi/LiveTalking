---
phase: 03-data-source-connectors
plan: 04
subsystem: rag/sources
tags: [config, registry, yaml, data-source]
dependency:
  requires:
    - rag/loaders (FileLoader, SQLiteConnector, APILoader)
  provides:
    - SourceConfig: data source configuration dataclass
    - SourceRegistry: dynamic source registry
    - load_sources_config: YAML config parser
  affects:
    - rag module public API
tech-stack:
  added:
    - PyYAML (for config parsing)
  patterns:
    - dataclass for configuration
    - registry pattern for dynamic loading
    - factory pattern for loader creation
key-files:
  created:
    - rag/sources/__init__.py
    - rag/sources/config.py
    - rag/sources/registry.py
    - rag/sources/example_sources.yaml
  modified:
    - rag/__init__.py
decisions:
  - D-11: YAML 配置文件管理多数据源
  - D-12: 数据源注册表支持动态加载
  - D-13: 支持数据源启用/禁用开关
metrics:
  duration: 5min
  tasks_completed: 4
  files_created: 4
  files_modified: 1
---

# Phase 3 Plan 04: Data Source Configuration Summary

实现数据源配置管理和注册表，提供统一的数据源管理机制。

## 实现内容

### 1. SourceConfig 配置解析

**文件**: `rag/sources/config.py`

- `SourceConfig` dataclass：数据源配置的数据结构
  - `name`: 数据源名称
  - `type`: 加载器类型 (file, sqlite, mysql, postgresql, api)
  - `enabled`: 启用/禁用开关
  - `config`: 类型特定的配置参数

- `load_sources_config(path)`: YAML 配置文件解析
  - 支持环境变量替换 `${VAR_NAME}` 和 `$VAR_NAME` 语法
  - 递归处理嵌套配置结构
  - 验证必需字段 (name, type)

- `save_sources_config(configs, path)`: 保存配置到 YAML

### 2. SourceRegistry 注册表

**文件**: `rag/sources/registry.py`

- `SourceRegistry` 类：动态管理数据源加载器
  - `register(name, loader, config)`: 注册数据源
  - `unregister(name)`: 注销数据源
  - `get(name)`: 获取加载器
  - `load_all()`: 加载所有注册源
  - `load_from_source(name)`: 加载指定源

- `create_loader_from_config(config)`: 工厂函数
  - file -> FileLoader
  - sqlite -> SQLiteConnector
  - api -> APILoader
  - mysql/postgresql -> 未实现（抛出异常）

- `setup_registry_from_config(path)`: 便捷函数
  - 从 YAML 配置设置整个注册表

### 3. 示例配置文件

**文件**: `rag/sources/example_sources.yaml`

包含三种数据源类型的完整配置示例：
- 本地文件源 (file)
- SQLite 数据库源 (sqlite)
- REST API 源 (api)

每个示例都包含详细注释说明。

### 4. 模块导出更新

**文件**: `rag/__init__.py`

- 导出 `SourceConfig`, `SourceRegistry`, `load_sources_config`
- 更新 `__all__` 列表

## 使用示例

```python
from rag import SourceConfig, SourceRegistry, load_sources_config
from rag.sources import setup_registry_from_config, create_loader_from_config

# 方式1: 从配置文件设置
registry = setup_registry_from_config("./data/sources.yaml")
documents = registry.load_all()

# 方式2: 手动创建和注册
config = SourceConfig(
    name="my_docs",
    type="file",
    enabled=True,
    config={"path": "./docs", "extensions": [".md", ".txt"]}
)
loader = create_loader_from_config(config)
registry = SourceRegistry()
registry.register("my_docs", loader, config)
documents = registry.load_from_source("my_docs")
```

## 配置格式

```yaml
sources:
  - name: local_docs
    type: file
    enabled: true
    config:
      path: ./data/knowledge
      extensions: [".txt", ".md", ".pdf"]
      recursive: true

  - name: product_db
    type: sqlite
    enabled: true
    config:
      connection_string: ./data/products.db
      query: "SELECT id, name, description FROM products"
      content_columns: ["name", "description"]

  - name: external_api
    type: api
    enabled: false
    config:
      url: https://api.example.com/knowledge
      method: GET
      auth:
        type: bearer
        token: ${API_TOKEN}
```

## Deviations from Plan

None - plan executed exactly as written.

## Commits

| Commit | Message |
|--------|---------|
| b0dde8c | feat(03-04): add SourceConfig for data source configuration |
| df93d20 | feat(03-04): add SourceRegistry for dynamic source loading |
| 0a3bfed | feat(03-04): add example_sources.yaml sample configuration |
| 8e2890f | feat(03-04): export sources module from rag package |

## Self-Check: PASSED

- [x] All files created exist
- [x] All commits exist in git log
- [x] Module imports correctly (`from rag import SourceConfig, SourceRegistry, load_sources_config`)
- [x] Acceptance criteria verified for all tasks
