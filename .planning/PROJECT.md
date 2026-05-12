# Project: LiveTalking RAG Knowledge Base

## Overview

为 LiveTalking 数字人项目的 LLM 模块添加 RAG（检索增强生成）知识库功能，使数字人在对话时能基于知识库内容回答问题，而非仅依赖通用 LLM 能力。

## Project Type

Brownfield — 基于现有 LiveTalking 代码库扩展

## Current State

LiveTalking 当前使用 `llm.py` 直接调用通义千问（Qwen）LLM API 进行对话，无知识库检索能力。数字人只能回答 LLM 训练数据中的通用问题。

## Target State

数字人在 chat 模式下，先通过 RAG 检索知识库相关内容，将检索结果作为上下文注入 LLM prompt，实现基于知识库的精准回答。

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| 检索方案 | 向量检索 (RAG) | 支持语义搜索，效果优于关键词匹配 |
| 数据源 | 本地文档 + 数据库 + API | 覆盖多种知识来源 |
| 集成方式 | 扩展现有 llm.py | 保持简洁，与现有架构一致 |
| 向量数据库 | 待定 (ChromaDB/FAISS) | 需要研究后决定 |
| Embedding 模型 | 待定 | 需要研究后决定 |

## Constraints

- 必须兼容现有 `llm.py` 的流式输出机制
- 不能破坏现有 echo/chat 双模式
- 需要支持现有 registry 插件体系
- 知识库检索延迟应 < 500ms，不影响实时性
- 保持 Python 3.10+ 兼容

## Success Criteria

1. 支持从本地文档（PDF/TXT/Markdown）构建知识库
2. 支持从数据库和 API 服务获取知识
3. Chat 模式下自动检索知识库并注入 LLM prompt
4. 检索延迟 < 500ms
5. 通过现有 API 端点 `/human` 使用，无需前端改动
