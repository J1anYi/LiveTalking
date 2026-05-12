---
phase: 07
plan: 01
subsystem: graceful-exit
tags: [shutdown, signal-handling, thread-cleanup]
requires: []
provides: [graceful-exit]
affects: [app.py, server/rtc_manager.py, server/session_manager.py, avatars/base_avatar.py]
tech-stack:
  added: []
  patterns: [signal-handlers, async-cleanup, thread-timeout]
key-files:
  created: []
  modified:
    - app.py
    - server/rtc_manager.py
    - server/session_manager.py
    - avatars/base_avatar.py
decisions:
  - Use asyncio.Event for shutdown signaling
  - Handle Windows NotImplementedError with fallback to signal.signal()
  - Add 5-second timeout for thread joins to prevent hanging
metrics:
  duration: "10 minutes"
  completed_date: "2026-05-12"
  task_count: 4
  file_count: 4
---

# Phase 7 Plan 01: Graceful Exit Implementation Summary

## One-liner

修复 Ctrl+C 后进程无法正常退出的问题，通过信号处理器、会话清理和线程超时机制实现优雅退出。

## Changes Made

### Task 1: Signal Handlers (app.py)

- 导入 `signal` 模块
- 在 `run_server()` 中注册 SIGINT/SIGTERM 信号处理器
- 使用 `asyncio.Event` 作为关闭信号
- 处理 Windows 平台的 `NotImplementedError`（使用 `signal.signal()` 替代）
- 在关闭时执行 `on_shutdown()` 清理并调用 `loop.stop()`

### Task 2: Shutdown Methods (session_manager.py, base_avatar.py)

- 在 `SessionManager` 中添加 `shutdown_all()` 异步方法，遍历所有会话并调用 `stop()`
- 在 `BaseAvatar` 中添加 `stop()` 方法，设置 `quit_event` 来停止后台线程

### Task 3: RTCManager Shutdown (rtc_manager.py)

- 修改 `shutdown()` 方法调用 `session_manager.shutdown_all()`
- 使用 `return_exceptions=True` 防止清理过程中的异常阻塞
- 添加日志记录清理进度

### Task 4: Thread Join Timeout (base_avatar.py)

- 为 `infer_thread.join()` 添加 5 秒超时
- 为 `process_thread.join()` 添加 5 秒超时
- 线程未及时停止时输出警告日志

## Deviations from Plan

None - plan executed exactly as written.

## Verification

手动验证步骤：
1. 启动服务：`python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar1`
2. 按 Ctrl+C
3. 验证：
   - 服务在 5 秒内退出
   - 端口 8010 立即释放
   - 无残留 python 进程

## Commits

| Commit | Message |
|--------|---------|
| 73f0a80 | feat(07-01): add signal handlers for graceful shutdown |
| cd80d8b | feat(07-01): add shutdown_all and stop methods for session cleanup |
| 2def51e | feat(07-01): update RTCManager.shutdown to clean up sessions |

---

*Phase: 07-graceful-exit*
*Completed: 2026-05-12*
