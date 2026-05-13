# Milestones: LiveTalking RAG Knowledge Base

---

## v1.0 — RAG Knowledge Base Integration

**Shipped:** 2026-05-12
**Phases:** 6 | **Plans:** 26

**Delivered:** 为 LiveTalking 数字人添加 RAG 知识库功能，实现基于知识库的智能对话。

**Key accomplishments:**
- ✅ 核心模块: VectorStore, DashScopeEmbedding, DocumentProcessor, RAGRetriever
- ✅ 数据源连接器: FileLoader, SQLiteConnector, APILoader (支持 TXT/MD/PDF/DOCX/SQLite/REST API)
- ✅ LLM 集成: Chat 模式自动注入知识库上下文，保持流式输出
- ✅ 配置系统: CLI 参数 + 环境变量 + YAML 文件，优先级合并
- ✅ 测试: 39 个新测试用例通过
- ✅ 文档: 完整用户文档 + 示例知识库

**Archive:** `.planning/milestones/v1.0-ROADMAP.md`

---

## v1.1 — Bug Fixes & UX Enhancement

**Shipped:** 2026-05-12
**Phases:** 2 | **Plans:** 2

**Delivered:** 修复优雅退出问题和 RAG 模式切换功能。

**Key accomplishments:**
- ✅ 优雅退出: 信号处理 + 会话清理 + 线程超时
- ✅ RAG 模式切换: RAG-only / RAG+Model 双模式
- ✅ 首条回复丢失修复 (阈值 >=5 + 中断检测)
- ✅ 模式持久化修复 (重启后从服务端获取)
- ✅ Edge-TTS 升级 7.2.3 → 7.2.8 (微软接口修复)

---

## v1.2 — Chat UI & History

**Planned:** 2026-05-12
**Phases:** 4 (9-12)

**Delivered:** 重构聊天界面 + 添加对话历史持久化存储。

**Target features:**
- ✅ SSE 流式文字推送 + 消息气泡 UI
- ✅ SQLite 持久化历史记录 + History API
- ✅ 会话管理侧边栏
- ✅ Alpine.js 前端框架重构

---
