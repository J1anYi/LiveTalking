---
wave: 1
depends_on: []
files_modified:
  - app.py
  - server/rtc_manager.py
  - server/session_manager.py
  - avatars/base_avatar.py
requirements_addressed:
  - EXIT-01
  - EXIT-02
  - EXIT-03
autonomous: true
---

# Plan 07-01: Graceful Exit Implementation

## Objective

修复 Ctrl+C 后进程无法正常退出的问题，确保所有资源被正确清理。

## Problem Analysis

根据用户报告的日志：
```
KeyboardInterrupt
DEBUG:utils.logger:sleep qsize=17
DEBUG:utils.logger:sleep qsize=33
...
```

问题：
1. `loop.run_forever()` 没有注册 SIGINT/SIGTERM 信号处理器
2. `on_shutdown` 只关闭 PeerConnection，没有停止 avatar session 后台线程
3. `base_avatar.py` 的 `render()` 线程及其子线程（inference、process_frames）没有收到退出信号

## Tasks

### Task 1: Add Signal Handlers to app.py

<read_first>
- E:/code_github/LiveTalking3/LiveTalking/app.py
- E:/code_github/LiveTalking3/LiveTalking/server/session_manager.py
</read_first>

<action>
在 `run_server` 函数中注册信号处理器：

1. 在 `run_server` 函数开头添加信号处理器注册：
```python
import signal

def run_server(runner):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 信号处理器
    shutdown_event = asyncio.Event()
    
    def signal_handler():
        logger.info("Received shutdown signal, cleaning up...")
        shutdown_event.set()
    
    # 注册信号处理器
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '0.0.0.0', opt.listenport)
    loop.run_until_complete(site.start())
    
    # 等待关闭信号
    loop.run_until_complete(shutdown_event.wait())
    
    # 执行清理
    logger.info("Shutting down server...")
    loop.run_until_complete(on_shutdown(appasync))
    loop.stop()
```

2. 修改 `main()` 函数中 `run_server` 调用后的清理逻辑。
</action>

<acceptance_criteria>
- `app.py` 包含 `import signal`
- `app.py` 包含 `loop.add_signal_handler(sig, signal_handler)` 
- `app.py` 包含 `shutdown_event.set()` 调用
</acceptance_criteria>

---

### Task 2: Add shutdown method to SessionManager

<read_first>
- E:/code_github/LiveTalking3/LiveTalking/server/session_manager.py
- E:/code_github/LiveTalking3/LiveTalking/avatars/base_avatar.py
</read_first>

<action>
在 `SessionManager` 类中添加 `shutdown_all` 方法：

```python
async def shutdown_all(self):
    """关闭所有会话并清理资源"""
    logger.info(f"Shutting down {len(self.sessions)} sessions...")
    for sessionid, avatar_session in list(self.sessions.items()):
        if avatar_session and hasattr(avatar_session, 'stop'):
            avatar_session.stop()
        self.sessions.pop(sessionid, None)
    logger.info("All sessions shutdown complete")
```

在 `BaseAvatar` 类中添加 `stop` 方法：

```python
def stop(self):
    """停止所有后台线程"""
    if hasattr(self, 'quit_event'):
        self.quit_event.set()
    logger.info(f"Avatar session {self.sessionid} stopped")
```
</action>

<acceptance_criteria>
- `session_manager.py` 包含 `async def shutdown_all(self)` 方法
- `base_avatar.py` 包含 `def stop(self)` 方法
- `stop` 方法设置 `self.quit_event.set()`
</acceptance_criteria>

---

### Task 3: Update RTCManager.shutdown to stop sessions

<read_first>
- E:/code_github/LiveTalking3/LiveTalking/server/rtc_manager.py
- E:/code_github/LiveTalking3/LiveTalking/server/session_manager.py
</read_first>

<action>
修改 `RTCManager.shutdown` 方法：

```python
async def shutdown(self):
    """关闭所有 PeerConnection 和 Sessions"""
    logger.info("Closing all PeerConnections...")
    coros = [pc.close() for pc in self.pcs]
    await asyncio.gather(*coros, return_exceptions=True)
    self.pcs.clear()
    
    # 关闭所有 avatar sessions
    await session_manager.shutdown_all()
    logger.info("RTCManager shutdown complete")
```
</action>

<acceptance_criteria>
- `rtc_manager.py` 的 `shutdown` 方法调用 `session_manager.shutdown_all()`
- `shutdown` 方法包含 `await asyncio.gather(*coros, return_exceptions=True)`
</acceptance_criteria>

---

### Task 4: Fix thread join timeout in base_avatar.py

<read_first>
- E:/code_github/LiveTalking3/LiveTalking/avatars/base_avatar.py
</read_first>

<action>
修改 `render` 方法中的线程等待逻辑，添加超时：

```python
# 在 render 方法末尾
infer_quit_event.set()
infer_thread.join(timeout=5.0)
if infer_thread.is_alive():
    logger.warning("inference thread did not stop in time")

process_quit_event.set()
process_thread.join(timeout=5.0)
if process_thread.is_alive():
    logger.warning("process_frames thread did not stop in time")

logger.info('baseavatar render thread stop')
```
</action>

<acceptance_criteria>
- `base_avatar.py` 的 `render` 方法中 `infer_thread.join(timeout=5.0)` 存在
- `base_avatar.py` 的 `render` 方法中 `process_thread.join(timeout=5.0)` 存在
</acceptance_criteria>

---

## Verification

运行以下测试验证：

1. 启动服务：`python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar1`
2. 按 Ctrl+C
3. 检查：
   - 服务在 5 秒内退出
   - `netstat -ano | findstr 8010` 显示端口已释放
   - 无残留 python 进程

## must_haves

- [ ] Ctrl+C 后服务在 5 秒内退出
- [ ] 退出后端口 8010 立即释放
- [ ] 所有后台线程正确停止
- [ ] 无残留进程

---
*Phase: 07-graceful-exit*
*Created: 2026-05-12*
