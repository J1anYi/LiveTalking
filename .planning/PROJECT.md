# Project: LiveTalking RAG Knowledge Base

## Overview

为 LiveTalking 数字人项目的 LLM 模块添加 RAG（检索增强生成）知识库功能，使数字人在对话时能基于知识库内容回答问题，而非仅依赖通用 LLM 能力。

## Project Type

Brownfield — 基于现有 LiveTalking 代码库扩展

## Current State

LiveTalking 当前使用 `llm.py` 直接调用通义千问（Qwen）LLM API 进行对话，无知识库检索能力。数字人只能回答 LLM 训练数据中的通用问题。

## Target State

数字人在 chat 模式下，先通过 RAG 检索知识库相关内容，将检索结果作为上下文注入 LLM prompt，实现基于知识库的精准回答。

## Current Milestone: v1.3 Frontend Redesign

**Goal:** 数字人前端界面全面重构，清新浅色设计，布局融合优化

**Target features:**
- 全新配色方案（暖白基底 + 柔和紫点缀，替代原有蓝色调）
- 视频 + 对话一体化布局（统一圆角卡片，视觉融合）
- RAG 模式切换移至顶栏，操作顺手
- 对话框扩大 + 气泡重新设计（更大间距、更舒服的视觉）
- 响应式 + 动效优化

**Key context:**
- 用户反馈：当前界面"很一般"，蓝色调不好看，对话框太小
- 布局问题：RAG 切换在左侧设置面板，离右侧对话框太远
- 色调问题：当前 `#4361ee` 蓝色调过重，需要浅色柔和方案
- 基于 UI/UX Pro Max 设计系统推荐，选择暖白中性 + 柔和紫作为新配色

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
