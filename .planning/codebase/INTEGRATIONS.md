# External Integrations

## TTS Services

| Service | Module | Config Key | Description |
|---------|--------|------------|-------------|
| Edge TTS | `tts/edge.py` | `edgetts` | Microsoft Edge free TTS, supports multiple languages and voices |
| GPT-SoVITS | `tts/sovits.py` | `gpt-sovits` | Open-source voice cloning TTS, requires local server |
| CosyVoice | `tts/cosyvoice.py` | `cosyvoice` | Alibaba's CosyVoice TTS, zero-shot voice cloning |
| Fish TTS | `tts/fish.py` | `fishtts` | Fish Speech TTS, requires local server |
| XTTS | `tts/xtts.py` | `xtts` | Coqui XTTS, voice cloning via REST API |
| Tencent TTS | `tts/tencent.py` | `tencent` | Tencent Cloud TTS, requires `TENCENT_APPID`, `TENCENT_SECRET_ID`, `TENCENT_SECRET_KEY` |
| Doubao TTS | `tts/doubao.py` | `doubao` | ByteDance volcano TTS, requires `DOUBAO_APPID`, `DOUBAO_TOKEN` |
| Azure TTS | `tts/azure.py` | `azuretts` | Azure Cognitive Services TTS, requires `AZURE_SPEECH_KEY`, `AZURE_TTS_REGION` |
| Qwen TTS | `tts/qwentts.py` | `qwentts` | Alibaba Qwen realtime TTS via DashScope, requires `DASHSCOPE_API_KEY` |
| IndexTTS2 | `tts/indextts2.py` | `indextts2` | IndexTTS2 via Gradio interface |

### TTS Configuration Parameters
- `--tts`: TTS service type (default: `edgetts`)
- `--REF_FILE`: Voice model ID or reference audio file path
- `--REF_TEXT`: Reference text for voice cloning (optional)
- `--TTS_SERVER`: TTS server URL for self-hosted services (default: `http://127.0.0.1:9880`)

## LLM Services

| Service | API Endpoint | Config Key | Description |
|---------|--------------|------------|-------------|
| Qwen (DashScope) | `https://dashscope.aliyuncs.com/compatible-mode/v1` | OpenAI compatible | Alibaba's Qwen model for chat responses |

### LLM Configuration
The LLM integration uses OpenAI-compatible API format. Default configuration in `llm.py`:
- Model: `qwen-plus`
- API Key: Configured in code (should use environment variable)
- Base URL: DashScope compatible-mode endpoint

## Streaming Outputs

| Protocol | Module | Use Case |
|----------|--------|----------|
| WebRTC | `streamout/webrtc.py` | Browser real-time streaming, low latency (~100ms) |
| RTMP | `streamout/rtmp.py` | Push to streaming platforms (YouTube, Bilibili, etc.) |
| RTCPush | Built into `app.py` | Push via WHIP protocol to media server (SRS) |
| Virtual Camera | `streamout/virtualcam.py` | Output as virtual webcam for video conferencing |

### Output Configuration Parameters
- `--transport`: Output mode (`webrtc`/`rtmp`/`rtcpush`/`virtualcam`)
- `--push_url`: Push URL for RTMP/RTCPush (default: `http://localhost:1985/rtc/v1/whip/?app=live&stream=livestream`)
- `--listenport`: Web server port (default: 8010)
- `--max_session`: Maximum concurrent sessions (default: 1)

## Avatar Models

| Model | Description | Source |
|-------|-------------|--------|
| Wav2Lip | Lip-sync from audio, fast inference | Download from cloud storage |
| MuseTalk | Audio-driven talking head, higher quality | Download from cloud storage |
| Ultralight | Lightweight real-time model | Download from cloud storage |

## Model Sources

| Model | Download Location | Target Path |
|-------|-------------------|-------------|
| Wav2Lip 256 | [Quark Drive](https://pan.quark.cn/s/83a750323ef0) / [Google Drive](https://drive.google.com/drive/folders/1FOC_MD6wdogyyX_7V1d4NDIO7P9NlSAJ) | `models/wav2lip.pth` |
| Wav2Lip Avatar | Same as above | `data/avatars/wav2lip256_avatar1/` |
| MuseTalk Models | Same as above | `models/` |
| Hubert Model | HuggingFace | Auto-downloaded via transformers |

## External Service Dependencies

### Required Environment Variables
| Variable | Service | Description |
|----------|---------|-------------|
| `DASHSCOPE_API_KEY` | Qwen TTS/LLM | Alibaba DashScope API key |
| `AZURE_SPEECH_KEY` | Azure TTS | Azure Cognitive Services key |
| `AZURE_TTS_REGION` | Azure TTS | Azure region (e.g., eastasia) |
| `TENCENT_APPID` | Tencent TTS | Tencent Cloud App ID |
| `TENCENT_SECRET_ID` | Tencent TTS | Tencent Cloud Secret ID |
| `TENCENT_SECRET_KEY` | Tencent TTS | Tencent Cloud Secret Key |
| `DOUBAO_APPID` | Doubao TTS | ByteDance App ID |
| `DOUBAO_TOKEN` | Doubao TTS | ByteDance access token |
| `HF_ENDPOINT` | HuggingFace | Mirror URL (e.g., `https://hf-mirror.com`) |

### Self-Hosted Services
| Service | Default Port | Description |
|---------|--------------|-------------|
| GPT-SoVITS | 9880 | Voice cloning TTS server |
| CosyVoice | 5000 | Zero-shot TTS server |
| Fish TTS | - | Fish Speech server |
| XTTS | 9000 | Coqui XTTS server |
| SRS Media Server | 1985 | For RTCPush/RTMP streaming |

## WebRTC Infrastructure

- STUN Server: `stun:stun.miwifi.com:3478` (default)
- ICE Server configuration via `RTCIceServer`
- Supports H.264 and VP8 video codecs
- Audio: PCM 16kHz mono

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/offer` | POST | WebRTC SDP offer/answer exchange |
| `/human` | POST | Text input for echo/chat mode |
| `/humanaudio` | POST | Upload audio file for playback |
| `/set_audiotype` | POST | Set custom avatar state |
| `/record` | POST | Start/stop recording |
| `/interrupt_talk` | POST | Interrupt current speech |
| `/is_speaking` | POST | Check speaking status |
