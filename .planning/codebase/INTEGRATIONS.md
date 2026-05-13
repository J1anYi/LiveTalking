# Integrations

**Generated:** 2026-05-12
**Type:** Codebase Mapping

## External APIs & Services

| Service | Direction | Auth | Purpose |
|---------|-----------|------|---------|
| DashScope LLM (Qwen) | Outbound | `DASHSCOPE_API_KEY` | Chat completions for digital human |
| DashScope Embedding | Outbound | `DASHSCOPE_API_KEY` | Text embedding for RAG |
| Microsoft Edge TTS | Outbound | Public key (hardcoded in edge-tts) | Text-to-speech synthesis |
| STUN Server | Outbound | None | WebRTC NAT traversal (`stun:stun.freeswitch.org:3478`) |

## Internal APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/offer` | POST | WebRTC SDP offer handling, session creation |
| `/human` | POST | Text input (echo/chat mode), triggers LLM |
| `/humanaudio` | POST | Audio file upload |
| `/interrupt_talk` | POST | Interrupt current speaking |
| `/is_speaking` | POST | Query speaking status |
| `/set_audiotype` | POST | Custom action state |
| `/set_rag_mode` | POST | Set RAG mode (rag_only / rag_plus_model) |
| `/get_rag_mode` | POST | Get current RAG mode |
| `/record` | POST | Recording control (start/stop) |
| Static files | GET | Web frontend at `/` (from `web/` dir) |

## Vector Database

- **Type:** ChromaDB (embedded, no separate server)
- **Persistence:** `./data/chromadb/` directory
- **Collection:** `knowledge_base` (configurable)
- **Top-K:** 3 (configurable)

## Output Transports

| Transport | Mechanism | Config |
|-----------|-----------|--------|
| WebRTC | aiortc + WHIP | Default, port 8010 |
| RTMP Push | FFmpeg push to RTMP server | `--push_url` |
| Virtual Camera | OBS VirtualCam via pyvirtualcam | `--transport virtualcam` |
