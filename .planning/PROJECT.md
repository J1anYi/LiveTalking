# Project: LiveTalking RAG Knowledge Base

## Overview

为 LiveTalking 数字人项目的 LLM 模块添加 RAG（检索增强生成）知识库功能，使数字人在对话时能基于知识库内容回答问题，而非仅依赖通用 LLM 能力。

## Project Type

Brownfield — 基于现有 LiveTalking 代码库扩展

## Current State

LiveTalking 当前使用 `llm.py` 直接调用通义千问（Qwen）LLM API 进行对话，无知识库检索能力。数字人只能回答 LLM 训练数据中的通用问题。

## Target State

数字人在 chat 模式下，先通过 RAG 检索知识库相关内容，将检索结果作为上下文注入 LLM prompt，实现基于知识库的精准回答。

## Current Milestone: v1.2 Chat UI & History

**Goal:** 重构聊天界面 + 添加对话历史持久化存储

**Target features:**
- SSE 流式推送 LLM 文字到前端，打字机效果
- 消息气泡 UI（user/assistant 视觉区分）
- Alpine.js 轻量前端框架重构
- SQLite 持久化存储对话记录 + History API
- 会话管理侧边栏（新建/切换/删除）

**Key context:**
- 当前 `_llm_history` 存储在 `avatar_session` 内存中，服务重启即丢失
- LLM 流式输出只喂给 TTS/音频管道，文字从未到达前端
- dashboard 无聊天展示面板，仅显示当前播放的语音文本
- 前两轮对话历史用于 RAG 上下文增强（`llm.py:95-97`），需要保持兼容
- 调研结论：前端用 Alpine.js (CDN, 零构建), 后端用 aiosqlite (async, 不阻塞事件循环)

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| 检索方案 | 向量检索 (RAG) | 支持语义搜索，效果优于关键词匹配 |
| 数据源 | 本地文档 + 数据库 + API | 覆盖多种知识来源 |
| 集成方式 | 扩展现有 llm.py | 保持简洁，与现有架构一致 |
| 向量数据库 | ChromaDB | 已验证，效果良好 |
| Embedding 模型 | DashScope text-embedding-v3 | 已验证，1024维 |
| LLM 服务 | DashScope Qwen-Plus | 已验证，流式输出正常 |
| 前端框架 | 轻量化框架（待定） | 需要在 Phase 1 中调研确定 |

## Constraints

- 必须兼容现有 `llm.py` 的流式输出机制
- 不能破坏现有 echo/chat 双模式
- 需要支持现有 registry 插件体系
- 知识库检索延迟应 < 500ms，不影响实时性
- 保持 Python 3.10+ 兼容
- 聊天历史必须支持 session 隔离

## Success Criteria

1. 支持从本地文档（PDF/TXT/Markdown）构建知识库
2. 支持从数据库和 API 服务获取知识
3. Chat 模式下自动检索知识库并注入 LLM prompt
4. 检索延迟 < 500ms
5. 通过现有 API 端点 `/human` 使用，无需前端改动
