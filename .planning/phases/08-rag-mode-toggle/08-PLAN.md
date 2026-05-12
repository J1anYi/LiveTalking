---
wave: 1
depends_on: []
files_modified:
  - llm.py
  - server/routes.py
  - web/dashboard.html
  - server/session_manager.py
requirements_addressed:
  - RAG-01
  - RAG-02
  - RAG-03
  - RAG-04
  - RAG-05
autonomous: true
---

# Plan 08-01: RAG Mode Toggle Implementation

## Objective

添加 RAG 模式切换功能，支持"仅 RAG"和"RAG+模型知识"两种模式。

## Current State Analysis

**llm.py (第 31-47 行):**
- 当前只有一种模式：RAG-only
- 使用 `build_rag_prompt` 构建增强 prompt
- prompt 格式：`You are a knowledge assistant. KB content: ... Query: ...`

**dashboard.html:**
- 没有 RAG 模式切换按钮
- 需要在设置面板添加切换控件

**server/routes.py:**
- 没有 `/set_rag_mode` 端点
- 需要添加新的 API 路由

## Tasks

### Task 1: Add RAG mode state to SessionManager

<read_first>
- E:/code_github/LiveTalking3/LiveTalking/server/session_manager.py
</read_first>

<action>
在 `SessionManager` 类中添加 RAG 模式状态管理：

1. 在 `__init__` 方法中添加：
```python
self.rag_modes: Dict[str, str] = {}  # sessionid -> "rag_only" | "rag_plus_model"
```

2. 添加新方法：
```python
def set_rag_mode(self, sessionid: str, mode: str):
    """设置 RAG 模式
    
    Args:
        sessionid: 会话 ID
        mode: "rag_only" 或 "rag_plus_model"
    """
    if mode not in ("rag_only", "rag_plus_model"):
        raise ValueError(f"Invalid RAG mode: {mode}")
    self.rag_modes[sessionid] = mode
    logger.info(f"RAG mode set to '{mode}' for session {sessionid}")

def get_rag_mode(self, sessionid: str) -> str:
    """获取 RAG 模式，默认为 'rag_only'"""
    return self.rag_modes.get(sessionid, "rag_only")
```
</action>

<acceptance_criteria>
- `session_manager.py` 包含 `self.rag_modes: Dict[str, str] = {}`
- `session_manager.py` 包含 `def set_rag_mode(self, sessionid: str, mode: str)` 方法
- `session_manager.py` 包含 `def get_rag_mode(self, sessionid: str) -> str` 方法
</acceptance_criteria>

---

### Task 2: Add /set_rag_mode API endpoint

<read_first>
- E:/code_github/LiveTalking3/LiveTalking/server/routes.py
- E:/code_github/LiveTalking3/LiveTalking/server/session_manager.py
</read_first>

<action>
在 `server/routes.py` 中添加新的 API 端点：

1. 添加路由处理函数：
```python
async def set_rag_mode(request):
    """设置 RAG 模式"""
    try:
        params = await request.json()
        sessionid = params.get('sessionid', '')
        mode = params.get('mode', 'rag_only')
        
        if mode not in ('rag_only', 'rag_plus_model'):
            return json_error(f"Invalid mode: {mode}. Must be 'rag_only' or 'rag_plus_model'")
        
        session_manager.set_rag_mode(sessionid, mode)
        return json_ok(data={"mode": mode})
    except Exception as e:
        logger.exception('set_rag_mode exception:')
        return json_error(str(e))


async def get_rag_mode(request):
    """获取当前 RAG 模式"""
    try:
        params = await request.json()
        sessionid = params.get('sessionid', '')
        mode = session_manager.get_rag_mode(sessionid)
        return json_ok(data={"mode": mode})
    except Exception as e:
        logger.exception('get_rag_mode exception:')
        return json_error(str(e))
```

2. 在 `setup_routes` 函数中注册路由：
```python
app.router.add_post("/set_rag_mode", set_rag_mode)
app.router.add_post("/get_rag_mode", get_rag_mode)
```
</action>

<acceptance_criteria>
- `routes.py` 包含 `async def set_rag_mode(request)` 函数
- `routes.py` 包含 `async def get_rag_mode(request)` 函数
- `setup_routes` 函数包含 `app.router.add_post("/set_rag_mode", set_rag_mode)`
- `setup_routes` 函数包含 `app.router.add_post("/get_rag_mode", get_rag_mode)`
</acceptance_criteria>

---

### Task 3: Update llm.py to support RAG+Model mode

<read_first>
- E:/code_github/LiveTalking3/LiveTalking/llm.py
- E:/code_github/LiveTalking3/LiveTalking/rag/__init__.py
</read_first>

<action>
修改 `llm.py` 以支持两种 RAG 模式：

1. 导入 session_manager：
```python
from server.session_manager import session_manager
```

2. 修改 RAG 检索逻辑（第 29-47 行），添加模式判断：
```python
# RAG retrieval for chat mode (enhanced prompt)
enhanced_message = message
rag_mode = session_manager.get_rag_mode(avatar_session.sessionid)

if rag_retriever and getattr(opt, 'rag_enabled', False):
    try:
        # Build retrieval query with conversation context
        retrieval_query = message
        if avatar_session._llm_history:
            # Include last 2 turns for context
            context_msgs = avatar_session._llm_history[-4:]
            retrieval_query = " ".join([m["content"] for m in context_msgs]) + " " + message

        # Retrieve relevant documents
        retrieved = rag_retriever.retrieve(retrieval_query)

        if retrieved:
            if rag_mode == "rag_only":
                # 原有模式：只使用 RAG 内容
                enhanced_message = build_rag_prompt(message, retrieved)
            else:
                # RAG+Model 模式：将 RAG 内容作为参考信息
                context_parts = []
                for chunk in retrieved[:3]:  # 最多使用 3 个文档
                    text = chunk.get("text", "")
                    context_parts.append(f"- {text}")
                context = "\n".join(context_parts)
                enhanced_message = f"参考信息:\n{context}\n\n用户问题: {message}\n\n请结合参考信息和你的知识回答问题:"
            logger.info(f"RAG retrieved {len(retrieved)} documents, mode={rag_mode}")
    except Exception as e:
        logger.warning(f"RAG retrieval failed, using original message: {e}")
```
</action>

<acceptance_criteria>
- `llm.py` 包含 `from server.session_manager import session_manager`
- `llm.py` 包含 `rag_mode = session_manager.get_rag_mode(avatar_session.sessionid)`
- `llm.py` 包含 `if rag_mode == "rag_only":` 条件判断
- `llm.py` 包含 `else:` 分支处理 "rag_plus_model" 模式
</acceptance_criteria>

---

### Task 4: Add RAG mode toggle to dashboard.html

<read_first>
- E:/code_github/LiveTalking3/LiveTalking/web/dashboard.html
</read_first>

<action>
在 `dashboard.html` 中添加 RAG 模式切换按钮：

1. 在设置面板（`.settings-panel`）中添加 RAG 模式切换控件（约第 338-347 行之后）：
```html
<div class="settings-panel mt-3">
    <div class="row">
        <div class="col-md-12">
            <div class="form-check form-switch mb-3">
                <input class="form-check-input" type="checkbox" id="use-stun">
                <label class="form-check-label" for="use-stun">使用STUN服务器</label>
            </div>
            <!-- RAG 模式切换 -->
            <div class="mb-3">
                <label class="form-label">RAG 知识库模式</label>
                <div class="btn-group w-100" role="group">
                    <input type="radio" class="btn-check" name="rag-mode" id="rag-only" value="rag_only" checked>
                    <label class="btn btn-outline-primary" for="rag-only">仅知识库</label>
                    <input type="radio" class="btn-check" name="rag-mode" id="rag-plus-model" value="rag_plus_model">
                    <label class="btn btn-outline-primary" for="rag-plus-model">知识库+模型</label>
                </div>
                <small class="text-muted">仅知识库：只回答知识库内容 | 知识库+模型：结合知识库和模型自身知识</small>
            </div>
        </div>
    </div>
</div>
```

2. 在 JavaScript 中添加模式切换处理（约第 600 行之后）：
```javascript
// RAG 模式切换
$('input[name="rag-mode"]').change(function() {
    const mode = $(this).val();
    const sessionid = document.getElementById('sessionid').value;
    
    fetch('/set_rag_mode', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({sessionid: sessionid, mode: mode})
    }).then(response => response.json())
    .then(data => {
        if (data.code === 0) {
            console.log('RAG mode set to:', mode);
            // 保存到 localStorage
            localStorage.setItem('rag_mode', mode);
        }
    });
});

// 页面加载时恢复 RAG 模式
const savedRagMode = localStorage.getItem('rag_mode');
if (savedRagMode) {
    $(`input[name="rag-mode"][value="${savedRagMode}"]`).prop('checked', true);
}
```
</action>

<acceptance_criteria>
- `dashboard.html` 包含 `name="rag-mode"` 的 radio button 组
- `dashboard.html` 包含 `id="rag-only"` 和 `id="rag-plus-model"` 的选项
- `dashboard.html` 包含 `$('input[name="rag-mode"]').change` 事件处理
- `dashboard.html` 包含 `localStorage.setItem('rag_mode', mode)` 持久化逻辑
- `dashboard.html` 包含 `localStorage.getItem('rag_mode')` 恢复逻辑
</acceptance_criteria>

---

## Verification

测试步骤：
1. 启动服务并打开 dashboard.html
2. 连接数字人
3. 切换 RAG 模式到"知识库+模型"
4. 发送问题，验证回答包含模型自身知识
5. 切换回"仅知识库"模式
6. 发送相同问题，验证回答只来自知识库
7. 刷新页面，验证模式保持

## must_haves

- [ ] Dashboard 显示 RAG 模式切换按钮
- [ ] 切换后 LLM 回答使用正确的模式
- [ ] 模式状态刷新页面后保持
- [ ] API 端点 `/set_rag_mode` 和 `/get_rag_mode` 正常工作

---
*Phase: 08-rag-mode-toggle*
*Created: 2026-05-12*
