# Technology Stack

**Generated:** 2026-05-12
**Type:** Codebase Mapping

## Languages & Runtimes

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.13+ |
| Async Runtime | aiohttp + asyncio | aiohttp 3.13.3 |
| WebRTC | aiortc | 1.14.0 |
| Legacy WSGI | Flask (standby) | — |

## Key Dependencies

| Category | Library | Version | Purpose |
|----------|---------|---------|---------|
| ML | torch | 2.6.0+cu124 | GPU inference for avatar models |
| ML | torchvision | 0.21.0+cu124 | Image processing |
| ML | transformers | 4.46.2 | Face parsing, whisper |
| ML | onnxruntime-gpu | — | Alternative inference runtime |
| Vision | opencv-python | 4.12.0 | Image/video processing |
| Audio | soundfile | 0.13.1 | Audio file I/O |
| Audio | resampy | 0.4.3 | Audio resampling |
| Audio | librosa | — | Audio analysis |
| TTS | edge-tts | 7.2.8 | Microsoft Edge TTS |
| LLM | openai | 2.16.0 | OpenAI-compatible LLM client |
| RAG | chromadb | >=0.5.0 | Vector database |
| Web | aiohttp-cors | 0.8.1 | CORS middleware |
| Media | av | 16.0.1 | FFmpeg bindings for WebRTC |
| Config | PyYAML | >=6.0.1 | YAML config for RAG |

## LLM Configuration

- **Provider:** DashScope (Alibaba Cloud) via OpenAI-compatible API
- **Endpoint:** `https://dashscope.aliyuncs.com/compatible-mode/v1`
- **Default Model:** `qwen-plus` (overridable via `LLM_MODEL` env var)
- **Auth:** `DASHSCOPE_API_KEY` environment variable
- **Streaming:** Enabled (`stream=True`), segment-based with punctuation detection

## Embedding Configuration

- **Provider:** DashScope (same as LLM)
- **Model:** `text-embedding-v3`, 1024 dimensions
- **Endpoint:** `https://dashscope.aliyuncs.com/compatible-mode/v1`
- **Auth:** Same `DASHSCOPE_API_KEY` env var

## Video Processing Pipeline

| Step | Technology | Details |
|------|-----------|---------|
| Frame capture | OpenCV | Avatar reference frames from `data/avatars/` |
| Face detection | S3FD | Multi-scale face detection |
| Feature extraction | wav2lip/musetalk/ultralight | Model-specific audio->video mapping |
| Video encoding | av (FFmpeg) | Libx264, 25fps, custom bitrate |
| WebRTC output | aiortc MediaStreamTrack | H264 preferred, VP8 fallback |
