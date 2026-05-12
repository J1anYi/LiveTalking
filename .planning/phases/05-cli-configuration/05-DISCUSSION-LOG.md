# Phase 5: CLI & Configuration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-12
**Phase:** 05-cli-configuration
**Areas discussed:** 配置方式, 配置优先级, 环境变量命名, 配置文件格式, 配置文件位置, CLI参数, 文档更新

---

## 配置方式

| Option | Description | Selected |
|--------|-------------|----------|
| 环境变量 + 配置文件 | 完整支持三种配置方式：CLI 参数、环境变量、YAML 配置文件 | ✓ |
| 仅环境变量 | 只添加环境变量支持，配置文件留到后续 | |
| 跳过此 Phase | CLI 参数已足够，Phase 5 标记为 N/A | |

**User's choice:** 环境变量 + 配置文件 (推荐)

---

## 配置优先级

| Option | Description | Selected |
|--------|-------------|----------|
| CLI > 环境变量 > 配置文件 | CLI 参数优先，环境变量次之，配置文件最低 | ✓ |
| 配置文件 > 环境变量 > CLI | 配置文件为基础，环境变量可覆盖，CLI 最高优先级 | |

**User's choice:** CLI > 环境变量 > 配置文件 (推荐)

---

## 环境变量命名

| Option | Description | Selected |
|--------|-------------|----------|
| RAG_* 前缀 | 例如 RAG_ENABLED, RAG_TOP_K, RAG_PERSIST_DIR | ✓ |
| LIVETALKING_RAG_* 前缀 | 例如 LIVETALKING_RAG_ENABLED | |

**User's choice:** RAG_* 前缀 (推荐)

---

## 配置文件格式

| Option | Description | Selected |
|--------|-------------|----------|
| YAML | 与 Phase 3 数据源配置一致，使用 data/rag_config.yaml | ✓ |
| Python 配置文件 | 与现有 Python 风格配置一致 | |

**User's choice:** YAML (推荐)

---

## 配置文件位置

| Option | Description | Selected |
|--------|-------------|----------|
| 项目根目录 | 与 data/avatars 同级，例如 data/rag_config.yaml | ✓ |
| rag/ 模块内 | 在 rag/ 模块内部，例如 rag/config.yaml | |

**User's choice:** 项目根目录 (推荐)

---

## CLI 参数

| Option | Description | Selected |
|--------|-------------|----------|
| 添加 --rag_config 参数 | 指定配置文件路径，默认 data/rag_config.yaml | ✓ |
| 不需要 CLI 参数 | 只通过环境变量 RAG_CONFIG_FILE 或默认路径 | |

**User's choice:** 添加 --rag_config 参数 (推荐)

---

## 文档更新

| Option | Description | Selected |
|--------|-------------|----------|
| 使用文档 | 在 README.md 或 docs/ 中添加 RAG 使用说明 | ✓ |
| requirements.txt | 添加 PyYAML 依赖 | ✓ |
| 示例配置文件 | 创建 data/rag_config.yaml.example | ✓ |

**User's choice:** 全部选择

---

## Claude's Discretion

- 配置文件不存在时的处理方式
- 配置值类型转换和验证
- 日志记录配置加载过程

## Deferred Ideas

None — discussion stayed within phase scope
