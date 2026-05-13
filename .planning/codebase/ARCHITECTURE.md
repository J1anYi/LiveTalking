# Architecture Overview

**Generated:** 2026-05-12
**Type:** Codebase Mapping

## System Pattern: Plugin Registry + Async Pipeline

The system uses a **decorator-based plugin registry** (`registry.py`) for core components, connected by **asynchronous queues** in a pipeline architecture.

```
User Input → API Routes → Session Manager → Avatar Session
    → LLM (streaming) → TTS → Audio Features → Avatar Inference
    → Video Frame → Output Module → User
```

## Core Abstractions

### Plugin Registry (`registry.py`)
- Categories: `stt`, `llm`, `tts`, `avatar`, `output`
- Registration via `@register("category", "name")` decorator
- Instantiation via `registry.create("category", "name", **kwargs)`
- New plugins auto-register on import

### BaseAvatar (`avatars/base_avatar.py`)
- Central orchestrator, manages TTS + Output plugin instances
- Two thread loops:
  - `inference()` — consumes audio features, runs neural inference (25fps)
  - `process_frames()` — consumes result frames, pushes to output transport
- Methods: `put_msg_txt()`, `put_audio_frame()`, `flush_talk()`, `stop()`

### BaseTTS (`tts/base_tts.py`)
- Async TTS via `put_msg_txt()` → internal queue → `txt_to_audio()`
- `process_tts()` runs in dedicated thread, consumes from `self.msgqueue`
- Generates audio frames streamed to inference pipeline

### BaseOutput (`streamout/base_output.py`)
- Abstract: `start()`, `push_video_frame()`, `push_audio_frame()`, `stop()`
- Implementations: WebRTC, RTMP, VirtualCam

### SessionManager (`server/session_manager.py`)
- Singleton, manages per-session avatar instances
- `create_session()` — async factory with thread pool loading
- `shutdown_all()` — cleanup on graceful exit
- Tracks per-session RAG mode (`rag_modes` dict)

## Key Patterns

**Decorator Registration:**
- `@register("avatar", "wav2lip") class LipReal(BaseAvatar): ...`
- `@register("tts", "edgetts") class EdgeTTS(BaseTTS): ...`

**Async Pipeline (queue-based):**
1. LLM streaming output → `tts.put_msg_txt()` → `tts.msgqueue`
2. TTS thread → `txt_to_audio()` → `asr.feat_queue` + `asr.output_queue`
3. Inference thread → audio features → `inference_batch()` → `res_frame_queue`
4. Process thread → `res_frame_queue` → `output.push_video_frame()`

**Configuration Priority (3-tier):**
1. CLI args (`--rag_enabled`, `--rag_top_k`)
2. Environment variables (`DASHSCOPE_API_KEY`, `RAG_*`)
3. YAML config file (`data/rag_config.yaml`)

**Graceful Shutdown:**
- `signal.signal(SIGINT/SIGTERM)` → `asyncio.Event` → `session_manager.shutdown_all()` → `avatar.stop()` → thread join (5s timeout)

## Data Flow (Chat Mode)

```
/human POST → routes.py → run_in_executor(llm_response)
  → _get_openai_client() (cached singleton)
  → RAG retrieval (if enabled) → enhanced prompt
  → OpenAI streaming completion (DashScope Qwen-Plus)
  → Segment detection (punctuation, >=5 chars)
  → clean_text_for_tts() (regex markdown cleanup)
  → avatar_session.put_msg_txt() → tts.msgqueue
  → TTS thread → audio → feat_queue
  → inference thread → video frames → res_frame_queue
  → process thread → output.push_video_frame()
```

## File Size Distribution

| File | Lines | Role |
|------|-------|------|
| `avatars/base_avatar.py` | 489 | Core orchestrator |
| `app.py` | 256 | Entry point, initialization |
| `avatars/wav2lip/genavatar.py` | ~200 | Wav2Lip model logic |
| `llm.py` | 169 | LLM streaming + RAG integration |
| `server/routes.py` | 194 | API route handlers |
| `server/session_manager.py` | 107 | Session lifecycle |
| `rag/__init__.py` | 110 | RAG public API |
| `tts/edge.py` | 76 | Edge TTS implementation |
