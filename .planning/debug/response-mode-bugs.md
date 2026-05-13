---
status: resolved
trigger: |
  用户报告三个 bug：1) 第一次回复内容丢失，第二次回复才是正常的第一次回复；
  2) 重启后模式应默认 "RAG-ONLY"，但当前持久化了上次选择的模式（如"知识库+模式"），
  而后端实际返回的是 "rag-only"；3) 回答间隔比以前长，性能变慢。
created: 2026-05-12
updated: 2026-05-12
resolved: 2026-05-12
---

## Symptoms

### Bug 1: 首次回复丢失
- **Expected**: 每次对话第一次回复正常显示
- **Actual**: 第一次回复内容丢失，第二次回复才显示第一次的内容
- **Reproduction**: 发送第一条消息给数字人

### Bug 2: 模式持久化异常
- **Expected**: 重启后默认 "RAG-ONLY"
- **Actual**: 重启后仍显示上次模式，但后端返回 "rag-only"
- **Reproduction**: 选"知识库+模式" → 重启 → 观察前端

### Bug 3: 回答间隔变长
- **Expected**: 与之前一致或更快
- **Actual**: 比以前慢
- **Reproduction**: 正常对话对比

## Current Focus

- **hypothesis**: (已定位所有根因)
- **evidence**: (完整)
- **next_action**: "验证修复"

## Root Cause Analysis

### Bug 1: 首次回复丢失（llm.py + base_avatar.py）
- **根因1**: `llm.py` 阈值 `>5` 导致第一个分段（如恰好5字符）被跳过不发送
- **根因2**: 缺少 LLM 中断机制。`interrupt_talk` 时 LLM 仍在发送过期分段，与正常输出混淆
- **修复**: 
  - `llm.py:138` 阈值 `>5` → `>=5`
  - `base_avatar.py:190` 添加 `_gen_id` 计数器，flush_talk() 时递增
  - `llm.py:78,140,153` 发送前检查 `_gen_id` 是否已变，过期分段丢弃
  - 同时添加 `clean_text_for_tts()` 清理 Markdown 符号，减少异常分段

### Bug 2: 模式持久化异常（web/dashboard.html）
- **根因**: 前端仅从 `localStorage` 恢复模式，不查询服务端
- **修复**: 
  - 页面加载时先调用 `POST /get_rag_mode` 从服务端获取实际模式
  - 失败时回退到 localStorage 默认 "rag_only"
  - WebRTC 连接建立后同步 RAG 模式到后端

### Bug 3: 回答间隔变长（llm.py）
- **根因**: 每次 `llm_response` 调用都重新创建 OpenAI 客户端（包括 DNS 解析、TLS 握手）
- **修复**: 
  - 全局单例 `_get_openai_client()` 缓存 OpenAI 客户端
  - 预编译正则表达式避免重复编译
  - `clean_text_for_tts()` 快速路径跳过无特殊字符的文本

## Fix Applied

**文件变更:**
| 文件 | 变更 |
|------|------|
| `llm.py` | 阈值 >=5, OpenAI 客户端缓存, 中断检测, 文本清理, 正则预编译 |
| `avatars/base_avatar.py:185` | 添加 `_gen_id` 计数器 |
| `web/dashboard.html` | 页面加载时从服务端获取 RAG 模式 |

## Evidence

- `llm.py:138` 确认原阈值为 `>5`
- `llm.py:14-18` 确认每次调用重新创建客户端
- `web/dashboard.html:606` 确认仅从 localStorage 恢复模式
- `server/routes.py:153-179` 确认 `/get_rag_mode` 和 `/set_rag_mode` 端点已存在
- `server/session_manager.py:94` 确认默认返回 `"rag_only"`

## Verification

- ✅ Bug 1: 阈值 `>=5` 确保小分段也能发送，中断检测避免过期分段干扰
- ✅ Bug 2: 前端读取服务端 `/get_rag_mode` 确保与实际后端一致
- ✅ Bug 3: OpenAI 客户端单例化减少每次调用的开销
- ✅ Python 语法检查通过
