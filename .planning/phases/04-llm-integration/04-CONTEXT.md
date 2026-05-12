# Phase 4: LLM Integration - Context

**Gathered:** 2026-05-12
**Status:** Ready for planning

<domain>
## Phase Boundary

将 RAG 检索集成到 `llm.py` 的对话流程中，在 chat 模式下自动检索知识库并注入上下文，同时保持流式输出机制和 echo 模式兼容。

**In scope:**
- 修改 `llm.py` 添加 RAG 检索逻辑
- 实现知识库上下文注入
- 保持流式输出兼容
- 添加配置开关控制知识库启用/禁用
- 维护对话历史用于多轮检索

**Out of scope:**
- 前端界面改动
- 新的 API 端点
- 知识库管理功能

</domain>

<decisions>
## Implementation Decisions

### Integration Approach
- **D-01:** 修改现有 `llm_response()` 函数，通过配置开关控制 RAG 检索
  - **Why:** 简单直接，保持单一入口，避免代码重复
  - **How to apply:** 在函数开头检查配置，启用时执行检索并注入上下文

### Prompt Construction
- **D-02:** 使用 `rag.build_rag_prompt()` 函数构建带知识库的 prompt
  - **Why:** rag/__init__.py 已提供此函数，格式统一，保持一致性
  - **How to apply:** 检索结果传入 build_rag_prompt(query, chunks) 获取增强 prompt

### Error Handling
- **D-03:** 静默降级 — 检索失败或结果为空时记录日志，继续无知识库对话
  - **Why:** 用户体验平滑，不中断对话流程
  - **How to apply:** try-except 包裹检索逻辑，失败时使用原始 message

### Configuration
- **D-04:** 通过 `avatar_session.opt` 传递 RAG 配置
  - **Why:** 利用现有配置传递机制，与现有架构一致
  - **How to apply:** config.py 添加 --rag_enabled, --rag_top_k 等参数

### Multi-turn Retrieval
- **D-05:** 维护对话历史，用完整上下文进行检索
  - **Why:** 多轮对话场景下，历史上下文能提供更准确的检索
  - **How to apply:** 在 llm_response 中维护对话历史列表，拼接历史消息用于检索

### RAG Initialization
- **D-06:** 应用启动时初始化 RAG 检索器，全局复用实例
  - **Why:** 避免每次调用创建新实例，提高检索性能
  - **How to apply:** 在 app.py 或 avatar 初始化时创建 RAGRetriever 实例

### Claude's Discretion
- 对话历史存储位置（avatar_session 属性或全局变量）
- 历史消息最大数量限制
- 检索超时配置具体值

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Architecture
- `llm.py` — 现有 LLM 对话逻辑，需修改
- `config.py` — CLI 参数配置，需扩展
- `rag/__init__.py` — RAG 公共 API (build_rag_prompt, quick_retrieve)
- `rag/retriever.py` — RAGRetriever 类

### Project Requirements
- `.planning/REQUIREMENTS.md` — FR-4.1 ~ FR-4.4 LLM 集成需求

### Prior Phase Context
- `.planning/phases/02-core-rag/02-SUMMARY.md` — Phase 2 实现总结
- `.planning/phases/03-data-source-connectors/03-SUMMARY.md` — Phase 3 实现总结

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `rag.build_rag_prompt(query, chunks)` — 构建带知识库上下文的 prompt
- `rag.quick_retrieve(query, top_k)` — 快速检索函数
- `rag.RAGRetriever` — 完整检索器类
- `avatar_session.opt` — 现有配置传递机制

### Established Patterns
- `llm_response(message, avatar_session, datainfo)` — 当前函数签名
- 流式输出：`client.chat.completions.create(stream=True)`
- 消息分块发送：`avatar_session.put_msg_txt(result, datainfo)`

### Integration Points
- `llm.py:21-28` — OpenAI client 创建和 messages 构建
- `llm.py:23` — 系统提示定义位置
- `config.py` — CLI 参数定义
- `app.py` — 应用入口，可初始化 RAG 检索器

</code_context>

<specifics>
## Specific Ideas

- 对话历史格式：`[{"role": "user/assistant", "content": "..."}]`
- 检索调用时机：在 OpenAI API 调用之前
- 配置参数名：`--rag_enabled`, `--rag_top_k`, `--rag_persist_dir`

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-llm-integration*
*Context gathered: 2026-05-12*
