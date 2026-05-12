# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**语言要求：所有回答和交互必须使用中文。**

## 项目概述

LiveTalking 是一个实时交互流式数字人系统，实现音视频同步对话。支持多种数字人模型（wav2lip、musetalk、ultralight）、声音克隆、多种输出方式（WebRTC、RTMP、虚拟摄像头）。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务（WebRTC 模式）
python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar1

# 运行服务（RTMP 模式）
python app.py --transport rtmp --model wav2lip --avatar_id wav2lip256_avatar1

# 指定 TTS 服务
python app.py --tts edgetts --model wav2lip --avatar_id wav2lip256_avatar1

# 访问前端
# WebRTC: http://<serverip>:8010/webrtcapi.html
# Dashboard: http://<serverip>:8010/dashboard.html
```

## 环境要求

- Python 3.10+
- PyTorch 2.5.0 + CUDA 12.4
- 需要设置 `DASHSCOPE_API_KEY` 环境变量（用于 LLM）

## 架构

### 插件注册系统

核心架构基于装饰器注册模式 (`registry.py`)：

```python
# 注册插件
@register("tts", "edgetts")
class EdgeTTS(BaseTTS): ...

# 创建实例
tts = registry.create("tts", "edgetts", opt=opt)
```

**注册类别**：
- `stt`: 语音识别
- `llm`: 大语言模型
- `tts`: 语音合成
- `avatar`: 数字人模型
- `output`: 输出传输

### 核心模块

| 模块 | 职责 |
|------|------|
| `app.py` | 入口，初始化 avatar、RTC Manager，启动 HTTP 服务 |
| `config.py` | CLI 参数解析 |
| `llm.py` | LLM 流式响应（DashScope/Qwen） |
| `registry.py` | 插件注册与工厂 |
| `server/routes.py` | HTTP API 路由（/human, /humanaudio 等） |
| `server/session_manager.py` | 会话管理 |
| `server/rtc_manager.py` | WebRTC 连接管理 |

### 数据流

```
用户输入 → API Routes → Session Manager → Avatar Session
    → LLM (chat 模式) → TTS → 音频特征提取 → Avatar 推理
    → 视频帧合成 → Output 模块 (WebRTC/RTMP/VirtualCam) → 用户
```

### Avatar 基类

`avatars/base_avatar.py` 是所有数字人模型的基类：

- 管理 TTS 和 Output 插件实例
- 处理音频帧队列（16kHz, 20ms/chunk）
- 提供渲染循环：`inference()` → `process_frames()` → `output.push_*()`

### TTS 基类

`tts/base_tts.py`：所有 TTS 插件的基类，实现 `txt_to_audio()` 方法。

### Output 基类

`streamout/base_output.py`：所有输出模式的抽象基类，实现 `start()`, `push_video_frame()`, `push_audio_frame()`, `stop()` 方法。

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/offer` | POST | WebRTC 信令 |
| `/human` | POST | 文本输入（echo/chat 模式） |
| `/humanaudio` | POST | 音频文件上传 |
| `/interrupt_talk` | POST | 打断当前说话 |
| `/is_speaking` | POST | 查询说话状态 |
| `/set_audiotype` | POST | 设置自定义动作状态 |

## 添加新插件

1. **TTS 插件**：继承 `tts/base_tts.py`，使用 `@register("tts", "name")` 注册
2. **Avatar 模型**：继承 `avatars/base_avatar.py`，实现 `inference_batch()` 和 `paste_back_frame()`
3. **Output 模式**：继承 `streamout/base_output.py`，实现所有抽象方法

## RAG 模块

项目正在集成 RAG 知识库功能：

- 模块位置：`rag/`
- 设计文档：`rag/ARCHITECTURE.md`, `rag/API_DESIGN.md`
- 使用 ChromaDB 向量存储 + DashScope Embedding API
- 集成点：`llm.py` 中的 prompt 构建

## 注意事项

- 视频帧率固定为 25 fps
- 音频采样率固定为 16kHz
- 服务端需开放 TCP 8010 端口和 UDP 全端口（WebRTC 模式）
- 模型文件存放于 `models/`，avatar 数据存放于 `data/avatars/`
