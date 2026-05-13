# FEATURES: Chat UI + History for LiveTalking Digital Human

## 项目上下文

- LiveTalking = 数字人系统，主交互是**语音对话**（用户说话 → ASR → LLM → TTS → 音画同步输出）
- 当前 `dashboard.html` 的"对话模式"只有输入框 + 一个平铺文本的 `asr-container`
- LLM 响应只流向 TTS/音频管道，**不返回前端**——前端看不见助手回复的文字
- `_llm_history` 存在 `avatar_session` 内存中，且**只存用户消息，不存助手消息**（见 `llm.py:165`）
- 当前状态：有 API（`/human`），无历史 API，无持久化，无消息气泡，无 Markdown

---

## 一、Table Stakes（必须要有）

这些是 LLM 对话 UI 的基准线，缺失会让产品显得业余。

### 1.1 消息气泡 UI

- 问答双方消息使用视觉区分的气泡（左/右对齐、不同底色、不同头像/标识）
- 系统消息（连接状态、RAG 模式切换、错误提示）有独立样式
- 当前 `dashboard.html` 的 `.asr-text` 已经按 `user-message` / `system-message` 区分，但只是左对齐同色块，需要升级为真·气泡布局

### 1.2 流式输出显示（打字机效果）

- LLM 响应逐 chunk 到达时，前端逐步追加文本，用户在字幕出现前就看到文字
- 当前 `llm.py` 流式输出只喂给 TTS，文字流从未到达前端
- **需要改造**：`llm_response()` 拆出独立流，通过新的 SSE 端点或 WebSocket 推送到前端
- 这是 chat UI 最基础的体验要求——否则用户直到音频结束都看不到 LLM 在说什么

### 1.3 自动滚动到最新消息

- 新消息出现时，聊天区域自动滚动到底部
- 如果用户主动向上滚动浏览历史，暂停自动滚动；向下滚到底部后恢复
- 当前已有 `scrollTop()` 但只有很简单的调用

### 1.4 时间戳

- 每条消息附带时间戳（HH:MM 格式，同一天；月/日/时/分 格式，跨天）
- 时间戳应轻量、不抢眼（灰色小字，气泡角落或消息之间）

### 1.5 API 端点暴露

- 当前 `_llm_history` 只存在于 avatar_session 内存中且缺少助手消息
- 至少需要一个新端点 `GET /history?sessionid=X` 返回完整消息列表
- 前端需要能在页面刷新后加载历史消息——否则刷新就丢，反直觉

### 1.6 消息状态指示

- 发送中（loading indicator / 脉冲动画）
- 已发送 / 已完成
- 发送失败（错误提示 + 重试入口）
- 对当前项目特别重要：LLM + TTS 整个管道可能有数秒延迟，用户需要知道"系统正在处理"

### 1.7 打断/中断指示

- 如果用户发送了新消息（打断数字人），前一条未完成的消息应标记为"已中断"
- 当前 `/human` 支持 `interrupt: true` 参数，但前端 UI 没有相应反馈

---

## 二、Differentiators（差异化亮点）

在表 stakes 之上，适合数字人场景的特色功能。

### 2.1 结构化消息（Markdown 渲染）——高优先级

- LLM 响应中有 `**粗体**`、列表、代码块、标题等 Markdown
- 前端使用 marked.js / highlight.js 渲染
- 但 TTS 仍然用 `clean_text_for_tts()` 清洗后再朗读（已有此函数）
- 文字显示富文本、语音读纯文本——视听分离
- 调研建议：marked.js (12KB gzip) 轻量无依赖，适合本项目

### 2.2 文本/语音双轨消息附加

- 发消息时区分来源：键盘输入 vs 语音输入（ASR）
- 语音输入的消息可以附带一个小麦克风图标
- 这是数字人场景特有的——传统 chat UI 只有键盘输入

### 2.3 对话侧边栏 / 会话列表

- 左侧或右侧显示历史会话列表（按时间排序）
- 每条会话显示：摘要（首条用户消息截断）、时间、消息数
- 点击切换会话 → 加载对应 `_llm_history`
- 类似 ChatGPT 侧边栏但是更轻量

### 2.4 会话操作

- 重命名会话（自动用首条消息做标题，用户可修改）
- 删除会话
- 导出会话（JSON / Markdown / TXT）

### 2.5 无限滚动 / 懒加载历史

- 当单次会话消息超过 N 条（如 100），分页加载
- 滚动到顶部触发加载更早的消息
- 当前系统运行中会话不会累积到这么多（`_llm_history` 无上限但无限制增长会有内存问题）

### 2.6 服务端 SSE 推流（作为 WebSocket 的轻量替代）

- `GET /sse/chat?sessionid=X` — SSE 端点推送 LLM 流式文字
- 比 WebSocket 更简单（HTTP 长连，自动重连）
- 前端用 `EventSource` 接收，逐 chunk 追加到气泡

### 2.7 音频波形可视化

- 消息发送/接收时在气泡旁显示小型音频电平条
- 数字人正在"说话"时的那条消息可以高亮边框或显示说话动画
- 利用已有的 `audio_context`（`webrtcchat.html` 中已有 `getUserMedia`）

### 2.8 消息支持多模态

- 用户可发送图片/链接给 LLM（如果 LLM 支持多模态视觉理解）
- 数字人回复可包含"已显示图片"的提示

---

## 三、Anti-Features（刻意避免）

以下是常见的"想做的东西"，但基于数字人场景和项目规模，应当明确说"不做"。

| Anti-Feature | 原因 |
|---|---|
| **富文本编辑器（Tiptap/Quill）** | 用户输入一律纯文本或语音，不需要工具栏、格式刷、图片粘贴。过度工程。 |
| **WebSocket 全双工通信** | 本项目只需要服务端→客户端单方向推送文字流。SSE (`EventSource`) 更轻量、自动重连、低心智负担。 |
| **复杂的状态管理（Redux/Zustand）** | 消息列表 + 会话列表，用纯 JS 数组 + DOM 操作即可。引入状态管理库是本项目场景的过度设计。 |
| **用户认证/登录系统** | 单用户本地部署的数字人。JWT/OAuth/多租户 完全不需要。 |
| **消息搜索/全文检索** | 会话列表本身已经够用。搜索功能工程量不小且短期内没有用户需求。 |
| **实时协作/多用户同屏** | 数字人是 1:1 交互，不是多人聊天。不需要 Online Presence / Typing Indicator。 |
| **客户端 SQL/WASM** | 既然已确定服务端 SQLite，前端只需要 fetch API 即可。不需要将存储推送到浏览器端。 |
| **PWA / Service Worker** | 服务端是 Python 流媒体服，不是 SPA。PWA 对此场景无意义。 |
| **对话分支 / 版本管理（类似 Claude）** | ChatGPT 的分支对话对大多数用户而言是混淆源，本项目又不是 IDE 式的试错场景。跳过。 |
| **语音回复转文字后再次 TTS 播放** | 不要将用户语音识别结果再次 TTS 成数字人回放。数字人不需要学舌。 |

---

## 四、复杂度估算

| # | Feature | 前后端改动 | 估时（人天） | 风险 |
|---|---------|-----------|------------|------|
| 1.1 | 消息气泡 UI | 纯前端（dashboard.html CSS + HTML） | 0.5 | 低 |
| 1.2 | 流式输出（SSE 推文字） | 后端新增 SSE 端点 + `llm.py` 改造 + 前端 EventSource | 2 | 中——需要重新设计 LLM 响应的数据流 |
| 1.3 | 自动滚动 | 纯前端（JS scroll + IntersectionObserver） | 0.3 | 低 |
| 1.4 | 时间戳 | 前端格式化 + 后端保存 timestamp | 0.3 | 低 |
| 1.5 | History API | 后端新端点 + `_llm_history` 改造（存助手消息） | 1 | 低 |
| 1.6 | 消息状态 | 前端 + SSE 消息 schema 添加 status 字段 | 0.5 | 低 |
| 1.7 | 打断指示 | 前端 SSE 事件 + 消息标记 | 0.3 | 低 |
| 2.1 | Markdown 渲染 | 引入 marked.js + 样式 | 0.3 | 低 |
| 2.2 | 输入来源标记 | 前端加图标 | 0.2 | 低 |
| 2.3 | 会话侧边栏 | 后端会话 CRUD + 前端列表 | 1.5 | 中 |
| 2.4 | 会话操作 | 后端 + 前端 | 1 | 低 |
| 2.5 | 无限滚动 | 后端分页参数 + 前端 IntersectionObserver | 0.5 | 低 |
| 2.6 | SSE 端点 | 后端实现 | 0.5（和1.2重叠） | 低 |
| 2.7 | 音频波形 | 纯前端 AudioContext API | 0.5 | 低 |
| 2.8 | 多模态消息 | 后端文件上传 + 前端预览 | 2 | 中——依赖 LLM 多模态能力 |

### 关键路径

```
1.2 SSE 流式输出 ─── 必须优先实现，是其他所有 UX 的基础
 └─ 1.1 消息气泡 ─── 依赖 1.2 获得消息数据
    └─ 1.3 自动滚动 ─── 依赖 1.1 的 DOM 结构
    └─ 1.4 时间戳 ─── 依赖 1.5 的历史记录
    └─ 1.6 消息状态 ─── 依赖 1.2 的 SSE 消息 schema
    └─ 2.1 Markdown ─── 依赖 1.1 的气泡渲染
1.5 History API ─── 独立，可并行开发
2.3 会话侧边栏 ─── 依赖 1.5
```

### 推荐分阶段交付

| 阶段 | 包含 | 估时 |
|------|------|------|
| **Phase A（核心体验）** | 1.1 + 1.2 + 1.3 + 1.6 + 2.6 | 3 天 |
| **Phase B（历史）** | 1.4 + 1.5 + 1.7 | 1.5 天 |
| **Phase C（增强）** | 2.1 + 2.2 + 2.7 | 1 天 |
| **Phase D（会话管理）** | 2.3 + 2.4 + 2.5 | 2.5 天 |

**核心交付（A）总计约 3 人天**，即可得到一个具备完整对话体验的 Chat UI。

---

## 五、数据流设计（建议）

### 当前（问题）

```
用户 → /human → llm_response() → clean_text_for_tts() → put_msg_txt() → TTS → audio
                                                                           └→ 前端：看不到文字
```

### 改造后

```
用户 → /human → llm_response()
                 ├→ SSE 端点逐 chunk 推文字 → 前端 EventSource → 气泡逐字追加
                 ├→ clean_text_for_tts() → put_msg_txt() → TTS → audio
                 └→ 完成时写入 SQLite + _llm_history

SSE 消息 Schema:
  { "type": "chunk",  "text": "你好",   "sessionid": "xxx" }    // 流式中间段
  { "type": "done",   "sessionid": "xxx", "msg_id": "yyy" }     // 完成
  { "type": "interrupted", "sessionid": "xxx" }                 // 被打断
```

---

## 六、关键技术决策

| 决策 | 选项 | 推荐 |
|------|------|------|
| 流式推送 | SSE vs WebSocket | **SSE** — 单方向，自动重连，EventSource API 一行搞定 |
| 前端 Markdown 渲染 | marked vs react-markdown vs 手写 | **marked.js** (12KB gzip), 无框架依赖 |
| 消息 ID | UUID vs 自增 vs time-based | **ULID** — 按时间排序、不冲突、适合作为 scroll key |
| UI 构建 | 纯 DOM vs 框架（Vue/React/Svelte） | **纯 DOM** — 单个页面，状态简单，引入框架增加构建工具复杂度 |
| 历史存储 | SQLite vs JSON 文件 vs Redis | **SQLite**（已定）— 已有 Python 生态支持，零运维 |
