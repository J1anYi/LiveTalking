# Phase 4: LLM Integration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-12
**Phase:** 04-llm-integration
**Areas discussed:** 集成方式, Prompt策略, 降级策略, 配置传递, 多轮对话, RAG初始化

---

## 集成方式

| Option | Description | Selected |
|--------|-------------|----------|
| 修改现有 llm_response() | 在现有函数中添加 RAG 检索逻辑，通过配置开关控制 | ✓ |
| 创建新函数 llm_response_rag() | 保留原函数不变，创建新函数 | |
| 装饰器包装 | 用装饰器在原函数前添加检索逻辑 | |

**User's choice:** 修改现有 llm_response() (推荐)
**Notes:** 简单直接，保持单一入口

---

## Prompt策略

| Option | Description | Selected |
|--------|-------------|----------|
| 使用 build_rag_prompt() | rag/__init__.py 已提供此函数 | ✓ |
| 修改系统提示 | 在系统消息中添加知识库内容 | |
| 自定义注入格式 | 根据实际效果调整注入格式 | |

**User's choice:** 使用 build_rag_prompt() (推荐)
**Notes:** 保持一致性，rag/__init__.py 已提供

---

## 降级策略

| Option | Description | Selected |
|--------|-------------|----------|
| 静默降级 | 记录日志，继续无知识库对话 | ✓ |
| 提示用户 | 告知用户知识库暂不可用 | |
| 抛出异常 | 中断对话流程 | |

**User's choice:** 静默降级 (推荐)
**Notes:** 用户体验平滑，不中断对话

---

## 配置传递

| Option | Description | Selected |
|--------|-------------|----------|
| 通过 avatar_session.opt | 利用现有配置传递机制 | ✓ |
| 全局配置模块 | 创建 rag_config.py 管理配置 | |
| 环境变量 | 通过 os.getenv() 读取 | |

**User's choice:** 通过 avatar_session.opt (推荐)
**Notes:** 与现有架构一致

---

## 多轮对话

| Option | Description | Selected |
|--------|-------------|----------|
| 仅当前消息检索 | 每次调用仅使用当前用户消息检索 | |
| 对话历史检索 | 维护对话历史，用完整上下文检索 | ✓ |
| 滑动窗口检索 | 用最近 N 轮对话拼接后检索 | |

**User's choice:** 对话历史检索
**Notes:** 多轮对话场景下，历史上下文能提供更准确的检索

---

## RAG初始化

| Option | Description | Selected |
|--------|-------------|----------|
| 启动时初始化 | 在应用启动时初始化 RAG 检索器 | ✓ |
| 调用时创建 | 每次 llm_response 调用时创建 | |
| 懒加载 | 首次使用时初始化，后续复用 | |

**User's choice:** 启动时初始化 (推荐)
**Notes:** 避免每次调用创建新实例，提高检索性能

---

## Claude's Discretion

- 对话历史存储位置
- 历史消息最大数量限制
- 检索超时配置具体值

## Deferred Ideas

None — discussion stayed within phase scope
