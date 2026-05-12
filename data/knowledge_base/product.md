# LiveTalking 产品说明

## 产品概述

LiveTalking 是一个**实时交互流式数字人系统**，为开发者提供完整的数字人解决方案。系统实现了音视频同步对话，支持多种数字人模型、声音克隆和多种输出方式。

### 核心价值

- 🎭 **高质量数字人渲染** - 支持多种模型，唇形同步自然
- 🗣️ **智能语音交互** - 实时语音识别与合成
- 📚 **知识库增强** - RAG 技术实现专业知识问答
- 🚀 **灵活部署** - 支持本地、服务器、云端部署

---

## 核心功能

### 1. 数字人模型

LiveTalking 支持三种主流数字人模型：

#### Wav2Lip
- **特点**：高质量唇形同步，视频输出清晰
- **适用场景**：高质量视频生成、录制场景
- **性能**：中等计算需求

#### MuseTalk
- **特点**：表情自然流畅，实时性好
- **适用场景**：实时互动、直播场景
- **性能**：中等计算需求

#### Ultralight
- **特点**：轻量级，启动快速
- **适用场景**：低延迟场景、移动端部署
- **性能**：低计算需求

### 2. 语音交互

#### 语音识别 (STT)
- 支持多种语音识别引擎
- 实时语音转文字
- 支持中英文识别

#### 语音合成 (TTS)
- Edge TTS（免费）
- 可扩展其他 TTS 服务
- 支持声音克隆

### 3. 输出方式

| 输出方式 | 延迟 | 特点 | 适用场景 |
|----------|------|------|----------|
| WebRTC | ~200ms | 双向通信、网页访问 | 实时互动、网页端 |
| RTMP | ~500ms | 推流到直播平台 | 直播场景 |
| Virtual Camera | ~300ms | 虚拟摄像头 | 视频会议、OBS |

### 4. RAG 知识库

RAG (Retrieval Augmented Generation) 知识库功能是 LiveTalking 的智能问答增强模块：

#### 功能特点
- 📖 **多格式支持**：TXT、MD、PDF、DOCX
- 🔍 **语义检索**：基于向量相似度检索
- 🎯 **精准问答**：基于知识库内容回答
- 🔄 **动态更新**：支持知识库热更新

#### 工作原理
```
用户提问 → 向量检索 → 获取相关文档 → 注入 LLM Prompt → 生成回答
```

#### 配置方式
```yaml
# data/rag_config.yaml
rag:
  enabled: true
  top_k: 3
  persist_dir: ./data/chromadb
  collection: knowledge_base
```

---

## 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        LiveTalking 系统                      │
├─────────────────────────────────────────────────────────────┤
│  输入层    │  处理层          │  输出层                      │
├────────────┼──────────────────┼──────────────────────────────┤
│  麦克风    │  STT 语音识别    │  WebRTC                      │
│  文本输入  │  LLM 对话生成    │  RTMP                        │
│  音频文件  │  RAG 知识检索    │  Virtual Camera              │
│            │  TTS 语音合成    │                              │
│            │  Avatar 渲染     │                              │
└────────────┴──────────────────┴──────────────────────────────┘
```

### 插件架构

LiveTalking 使用装饰器注册模式实现插件扩展：

```python
# 注册 TTS 插件
@register("tts", "custom_tts")
class CustomTTS(BaseTTS):
    def txt_to_audio(self, text):
        # 实现语音合成
        pass

# 使用插件
tts = registry.create("tts", "custom_tts")
```

**可扩展的插件类型**：
- `stt` - 语音识别
- `llm` - 大语言模型
- `tts` - 语音合成
- `avatar` - 数字人模型
- `output` - 输出传输

---

## 使用场景

### 1. 企业客服
- 7x24 小时智能客服
- 基于企业知识库回答
- 多渠道接入

### 2. 教育培训
- 虚拟教师授课
- 知识问答助手
- 在线培训平台

### 3. 直播带货
- 虚拟主播
- 产品介绍自动化
- 多平台推流

### 4. 会议助手
- 视频会议虚拟形象
- 会议记录和总结
- 智能问答

---

## 部署要求

### 硬件要求

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 4 核 | 8 核+ |
| 内存 | 8 GB | 16 GB+ |
| GPU | GTX 1060 | RTX 3080+ |
| 存储 | 20 GB | 50 GB+ SSD |

### 软件要求

- **操作系统**：Linux / Windows / macOS
- **Python**：3.10+
- **CUDA**：12.4（GPU 加速）
- **PyTorch**：2.5.0+

### 网络要求

- **WebRTC 模式**：TCP 8010 端口 + UDP 全端口开放
- **RTMP 模式**：TCP 8010 端口
- **API 访问**：需要访问 DashScope API（或其他 LLM API）

---

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
export DASHSCOPE_API_KEY=sk-your-api-key
```

### 3. 启动服务
```bash
python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar1
```

### 4. 访问前端
- WebRTC 界面：http://localhost:8010/webrtcapi.html
- Dashboard：http://localhost:8010/dashboard.html

### 5. 启用 RAG（可选）
```bash
python app.py --rag_enabled --rag_top_k 3 --model wav2lip --avatar_id wav2lip256_avatar1
```

---

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/offer` | POST | WebRTC 信令 |
| `/human` | POST | 文本输入（echo/chat 模式） |
| `/humanaudio` | POST | 音频文件上传 |
| `/interrupt_talk` | POST | 打断当前说话 |
| `/is_speaking` | POST | 查询说话状态 |
| `/set_audiotype` | POST | 设置自定义动作状态 |

---

## 技术支持

- **文档**：`docs/rag.md`
- **问题反馈**：GitHub Issues
- **API 文档**：参考 `rag/` 目录下的模块文档

---

*版本：v1.0*
*更新日期：2026-05-12*
