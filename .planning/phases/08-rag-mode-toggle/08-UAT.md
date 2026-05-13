---
status: diagnosed
phase: 08-rag-mode-toggle
source: 08-SUMMARY.md
started: 2026-05-12T17:20:00Z
updated: 2026-05-12T17:20:00Z
---

## Current Test

[testing complete]

## Tests

### 1. 页面加载时 RAG 模式从服务端获取
expected: 打开 dashboard.html 并连接，页面加载后 RAG 模式显示"仅知识库"(rag_only)，来自服务端默认值，而非 localStorage
result: pass
evidence: |
  dashboard.html:606-625 通过 POST /get_rag_mode 获取服务端模式，
  成功时根据返回值设置 radio button，失败时回退到 localStorage 或 "rag_only" 默认值。
  session_manager.py:94 get_rag_mode 默认返回 "rag_only"。

### 2. RAG 模式切换生效
expected: 切换到"知识库+模型"模式，发送问题，回答应结合知识库和模型知识
result: pass
evidence: |
  dashboard.html:585-604 radio button change 事件调用 POST /set_rag_mode。
  llm.py:82-107 根据 rag_mode 使用不同 prompt：
  - rag_only → build_rag_prompt() 纯知识库
  - rag_plus_model → 参考信息 + 模型知识

### 3. 回答长度优化 — RAG-only 模式
expected: RAG-only 模式下，回答简短口语化，不添加额外信息
result: pass
evidence: |
  rag/__init__.py:81 prompt 尾部有 "请用简短、口语化的方式回答"
  llm.py:114 system prompt 有 "尽量以简短、口语化的方式输出"
  双重简短约束，回答应足够简洁。

### 4. 回答长度优化 — RAG+Model 模式
expected: RAG+Model 模式下，回答应结合知识库+自身知识，但不过度冗长
result: issue
reported: "回答确实很长啊，有没有优化的地方"
severity: minor
evidence: |
  llm.py:107 RAG+Model prompt：
    "参考信息:\n{context}\n\n用户问题: {message}\n\n请结合参考信息和你的知识回答问题:"
  该 prompt 缺少"简短/简洁"指令，system prompt 的简短约束不够强，
  模型倾向于给出详细回答。与此对比，RAG-only prompt 明确写了 "简短"。

### 5. 刷新页面后模式保持
expected: 刷新页面后，RAG 模式保持为刷新前选择的模式
result: pass
evidence: |
  切换时 localStorage.setItem('rag_mode', mode) (dashboard.html:601)
  页面加载时从服务端获取后同步到 localStorage (dashboard.html:618)
  双向同步保证刷新后模式保持。

### 6. 重启服务后模式重置为 rag_only
expected: 重启后端服务后，模式自动重置为"仅知识库"(rag_only)，不从 localStorage 恢复旧模式
result: pass
evidence: |
  session_manager.py:94 get_rag_mode 默认返回 "rag_only"
  dashboard.html:606-625 页面加载时从服务端获取模式，不依赖 localStorage
  重启后 session_manager 重置，所有 session 回到默认值。

## Summary

total: 6
passed: 5
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "RAG+Model 模式下回答应简短，不过度冗长"
  status: failed
  reason: "User reported: 回答确实很长啊，有没有优化的地方"
  severity: minor
  test: 4
  root_cause: "RAG+Model prompt (llm.py:107) 缺少简短约束指令"
  artifacts:
    - path: "llm.py"
      issue: "RAG+Model prompt missing brevity instruction"
  missing:
    - "在 RAG+Model prompt 末尾添加 '请用简短、口语化的方式回答'"
  fix_applied: "llm.py:107 添加 '用简短、口语化的方式回答问题'"
  debug_session: ".planning/debug/response-mode-bugs.md"
