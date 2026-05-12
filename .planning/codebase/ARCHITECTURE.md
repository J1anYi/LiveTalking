# System Architecture

**Analysis Date:** 2026/05/11

## Overview

LiveTalking is a real-time interactive streaming digital human system that achieves audio-video synchronized dialogue. The system follows a **layered plugin architecture** with a clear separation between:
- API/Transport layer (WebRTC, RTMP, VirtualCam)
- Logic layer (LLM, TTS, ASR)
- Rendering layer (Avatar models: MuseTalk, Wav2Lip, UltraLight)
- Output layer (streaming backends)

The core innovation is the **asynchronous rendering pipeline** that synchronizes audio features with video frame generation in real-time.

## Data Flow

```
User Input (Text/Audio)
         │
         ▼
┌─────────────────────┐
│   API Layer         │
│   routes.py         │  ← HTTP/WebSocket endpoints
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Session Manager   │  ← Manages avatar session lifecycle
│   session_manager.py│
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   LLM Engine        │  ← Qwen/DashScope (optional)
│   llm.py            │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   TTS Engine        │  ← EdgeTTS/GPT-SoVITS/CosyVoice/etc.
│   tts/*.py          │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   ASR/Audio Feature │  ← Whisper/Hubert for feature extraction
│   audio_features/   │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Avatar Rendering  │  ← MuseTalk/Wav2Lip/UltraLight
│   base_avatar.py    │
│   ┌───────────────┐ │
│   │ inference()   │ │  ← Model inference thread
│   │ process_frames│ │  ← Frame composition thread
│   │ render()      │ │  ← Main orchestration thread
│   └───────────────┘ │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Output Layer      │  ← WebRTC/RTMP/VirtualCam
│   streamout/*.py    │
└─────────────────────┘
         │
         ▼
    End User (Browser/Media Server/Virtual Camera)
```

## Layer Architecture

### 1. API Layer

**Endpoints** (`server/routes.py`):
- `POST /offer` - WebRTC SDP offer/answer exchange
- `POST /human` - Text input (echo/chat mode)
- `POST /humanaudio` - Audio file upload
- `POST /set_audiotype` - Custom action/state switching
- `POST /record` - Recording control
- `POST /interrupt_talk` - Interrupt current speech
- `POST /is_speaking` - Query speaking status

**Session Handling**:
- Sessions are created via `SessionManager.create_session()`
- Each session gets a unique UUID
- Sessions persist beyond WebRTC connection lifecycle

### 2. Logic Layer

**LLM Engine** (`llm.py`):
- Uses DashScope/Qwen for chat completion
- Streaming response with sentence segmentation
- Integrates with TTS for voice output

**TTS Engine** (`tts/*.py`):
- Plugin-based architecture via `@register("tts", name)` decorator
- Available plugins: `edgetts`, `gpt-sovits`, `xtts`, `cosyvoice`, `fishtts`, `tencent`, `doubao`, `indextts2`, `azuretts`, `qwentts`
- Base class: `tts/base_tts.py` - `BaseTTS`
- Key method: `txt_to_audio(msg)` - converts text to audio chunks

**Audio Feature Extraction** (`avatars/audio_features/`):
- `whisper.py` - WhisperASR for audio-to-feature
- `hubert.py` - Hubert feature extraction
- `mel.py` - Mel spectrogram features
- Base class: `base_asr.py` - `BaseASR`
- Outputs audio features for avatar model inference

### 3. Rendering Layer

**Base Avatar** (`avatars/base_avatar.py`):
The core rendering pipeline consists of three concurrent threads:

```
render() [Main Thread]
    │
    ├── tts.render() ──────────────────► TTS Thread
    │                                        │
    │                                        ▼
    │                               Audio chunks → ASR queue
    │
    ├── inference() [Inference Thread] ◄── ASR feat_queue
    │       │
    │       └── inference_batch() ──────► Model inference
    │              │
    │              └── res_frame_queue ──► Predicted frames
    │
    └── process_frames() [Process Thread] ◄── res_frame_queue
            │
            ├── paste_back_frame() ──────► Frame composition
            │
            └── output.push_video_frame() ► Output layer
```

**Model Inference**:
- MuseTalk: VAE + UNet + Audio embedding (Whisper)
- Wav2Lip: Lip-sync model with face detection
- UltraLight: Lightweight real-time model

**Post-processing**:
- `paste_back_frame()` - Pastes generated face region back to original frame
- Transition effects between speaking/silent states
- Custom action cycling support

### 4. Streaming Layer

**WebRTC** (`streamout/webrtc.py`, `server/rtc_manager.py`, `server/webrtc.py`):
- Uses `aiortc` for WebRTC implementation
- `RTCManager` handles PeerConnection lifecycle
- `HumanPlayer` manages media tracks (audio/video)
- `PlayerStreamTrack` implements `MediaStreamTrack` for streaming
- Supports H.264 and VP8 codecs

**RTMP** (`streamout/rtmp.py`):
- Uses `python_rtmpstream` library
- `RTMPOutput` pushes frames to RTMP server
- Handles BGR→RGB conversion for streaming

**Virtual Camera** (`streamout/virtualcam.py`):
- Uses `pyvirtualcam` for virtual camera output
- Uses `pyaudio` for local audio playback
- Suitable for local testing and OBS integration

### 5. Plugin System

**Registry Mechanism** (`registry.py`):
```python
# Registration via decorator
@register("tts", "edgetts")
class EdgeTTS(BaseTTS): ...

# Creation via factory
tts = registry.create("tts", "edgetts", opt=opt)
```

**Plugin Categories**:
- `stt` - Speech-to-text (future)
- `llm` - Large language models
- `tts` - Text-to-speech
- `avatar` - Avatar rendering models
- `streamout` - Output streaming backends

**Available Plugins**:
| Category | Plugins |
|----------|---------|
| tts | edgetts, gpt-sovits, xtts, cosyvoice, fishtts, tencent, doubao, indextts2, azuretts, qwentts |
| avatar | musetalk, wav2lip, ultralight |
| streamout | webrtc, rtcpush, rtmp, virtualcam |

## Key Abstractions

### BaseAvatar (`avatars/base_avatar.py`)
- **Purpose**: Core rendering pipeline for all avatar types
- **Key Methods**:
  - `render(quit_event)` - Main orchestration loop
  - `inference(quit_event)` - Batch model inference
  - `process_frames(quit_event)` - Frame composition and output
  - `put_msg_txt(msg)` - Queue text for TTS
  - `put_audio_frame(chunk)` - Queue audio for ASR
- **Queues**:
  - `res_frame_queue` - Inference results → frame processor
  - `asr.feat_queue` - Audio features → inference
  - `asr.output_queue` - Audio frames → output

### BaseTTS (`tts/base_tts.py`)
- **Purpose**: Abstract base for TTS implementations
- **Key Methods**:
  - `put_msg_txt(msg, datainfo)` - Queue text
  - `txt_to_audio(msg)` - Convert text to audio
  - `process_tts(quit_event)` - Processing thread

### BaseASR (`avatars/audio_features/base_asr.py`)
- **Purpose**: Audio feature extraction base class
- **Key Methods**:
  - `put_audio_frame(chunk)` - Queue audio chunk
  - `get_audio_frame()` - Get audio with silence detection
  - `run_step()` - Per-step processing
  - `_feature2chunks()` - Slice features for batch inference

### BaseOutput (`streamout/base_output.py`)
- **Purpose**: Abstract output transport interface
- **Key Methods**:
  - `start()` - Initialize output channel
  - `push_video_frame(frame)` - Push video frame
  - `push_audio_frame(frame)` - Push audio frame
  - `stop()` - Cleanup

### SessionManager (`server/session_manager.py`)
- **Purpose**: Singleton session lifecycle manager
- **Key Methods**:
  - `create_session(params)` - Async session creation
  - `get_session(sessionid)` - Retrieve session
  - `remove_session(sessionid)` - Cleanup session
- **Pattern**: Singleton via `__new__`

## Entry Points

**Main Entry** (`app.py`):
- Location: `app.py:main()`
- Triggers: `python app.py` or direct execution
- Responsibilities:
  - Parse CLI arguments via `config.parse_args()`
  - Load avatar model (MuseTalk/Wav2Lip/UltraLight)
  - Initialize `RTCManager`
  - Initialize `SessionManager`
  - Setup aiohttp routes
  - Start HTTP server

**Route Entry** (`server/routes.py:setup_routes()`):
- Registers all API endpoints
- Static file serving from `web/` directory

## Error Handling

**Strategy**: Exception catching with JSON error responses

**Patterns**:
- Route handlers use try/except with `json_error()` response
- Logger captures exceptions with stack traces
- WebRTC connection state changes trigger cleanup
- Graceful shutdown via `on_shutdown()` handler

**Example** (`server/routes.py`):
```python
async def human(request):
    try:
        # ... processing
        return json_ok()
    except Exception as e:
        logger.exception('human route exception:')
        return json_error(str(e))
```

## Cross-Cutting Concerns

**Logging**:
- Centralized via `utils/logger.py`
- `logger` instance used throughout codebase
- Info level for state changes, debug for performance

**Validation**:
- Input validation at route level
- Session existence checks before operations
- Plugin availability validation in registry

**Authentication**:
- Not implemented at framework level
- API keys for external services (LLM, TTS) via environment variables

**Configuration**:
- CLI arguments parsed via `config.py`
- `opt` object passed through all layers
- Environment variables for API keys (e.g., `DASHSCOPE_API_KEY`)

**Concurrency**:
- Threading for TTS, inference, and frame processing
- Async/await for WebRTC and HTTP handlers
- Multiprocessing for avatar session isolation (`mp.set_start_method('spawn')`)

---

*Architecture analysis: 2026/05/11*
