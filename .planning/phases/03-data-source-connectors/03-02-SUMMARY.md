---
phase: 03-data-source-connectors
plan: 02
subsystem: rag
tags: [api, data-source, loader, rest]
depends_on: []
provides: [APILoader]
tech_stack:
  added:
    - urllib.request (标准库 HTTP 客户端)
    - JSONPath 数据提取
  patterns:
    - REST API 数据源连接器
    - Bearer Token / API Key 认证
    - 响应数据到文档格式转换
key_files:
  created:
    - rag/loaders/api_loader.py
  modified:
    - rag/loaders/__init__.py
    - rag/__init__.py
decisions:
  - D-06: 支持 GET/POST HTTP 方法
  - D-07: 支持完整 API 配置 (url, method, headers, body, data_path)
  - D-08: 支持 Bearer Token 和 API Key 认证
metrics:
  duration: 5min
  completed_at: 2026-05-12
  tasks_completed: 2
  files_created: 1
  files_modified: 2
---

# Phase 03 Plan 02: REST API Data Source Connector Summary

实现了 REST API 数据源连接器，支持从外部 API 服务获取知识数据。

## One-liner

APILoader 类实现 GET/POST 请求、Bearer/API Key 认证、JSONPath 数据提取。

## Tasks Completed

| Task | Name | Status | Commit |
|------|------|--------|--------|
| 1 | Create APILoader class | Complete | 6bb60fa |
| 2 | Update module exports | Complete | 24f5c92 |

## Implementation Details

### APILoader Class (`rag/loaders/api_loader.py`)

**初始化参数：**
- `url`: API 端点 URL
- `method`: HTTP 方法 (GET/POST)，默认 GET
- `headers`: 可选 HTTP 头
- `body`: POST 请求体 (dict)
- `data_path`: JSONPath 表达式，从响应中提取数据
- `auth`: 认证配置
  - `{"type": "bearer", "token": "xxx"}` - Bearer Token
  - `{"type": "api_key", "key": "xxx", "header": "X-API-Key"}` - API Key
- `timeout`: 请求超时 (秒)，默认 30

**load() 方法：**
1. 构建带认证的 HTTP 请求
2. 发送请求并解析 JSON 响应
3. 使用 JSONPath 提取数据
4. 转换为文档格式 `(content, metadata)`

**元数据格式：**
```python
{
    "source": "https://api.example.com/data",
    "type": "api",
    "method": "GET",
    "retrieved_at": "2026-05-12T10:30:00",
    "item_index": 0,
    "size": 1234
}
```

**JSONPath 支持：**
- 字段访问: `$.data.items`
- 数组索引: `$.results[0].content`
- 通配符: `$.items[*]`

## Deviations from Plan

None - plan executed exactly as written.

## Files Modified

```
rag/loaders/api_loader.py    # 新建: APILoader 类 (307 行)
rag/loaders/__init__.py      # 更新: 导出 APILoader
rag/__init__.py              # 更新: 顶层导出 APILoader
```

## Commits

| Hash | Message |
|------|---------|
| 6bb60fa | feat(03-02): implement APILoader for REST API data source |
| 24f5c92 | feat(03-02): export APILoader from rag.loaders module |
| d84fea8 | feat(03-02): add APILoader to rag module top-level exports |

## Self-Check: PASSED

- [x] `class APILoader` 存在于 `rag/loaders/api_loader.py` (第 13 行)
- [x] `def load` 存在于 `rag/loaders/api_loader.py` (第 55 行)
- [x] `APILoader` 在 `rag/loaders/__init__.py` 导出 (第 5, 7 行)
- [x] 提交历史正确 (6bb60fa, 24f5c92, d84fea8)

## Requirements Coverage

| Requirement | Status |
|-------------|--------|
| FR-1.3: REST API 支持 | Complete |
