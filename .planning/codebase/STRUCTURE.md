# Structure

**Generated:** 2026-05-12
**Type:** Codebase Mapping

## Top-Level Layout

```
LiveTalking/
├── app.py                 # Entry point, server init, model loading
├── config.py              # CLI argument parsing, RAG config merge
├── llm.py                 # LLM streaming response + RAG prompt
├── registry.py            # Plugin registration system
│
├── avatars/               # Digital human model implementations
│   ├── base_avatar.py     # Base orchestrator (inference, process, TTS mgmt)
│   ├── wav2lip_avatar.py  # Wav2Lip avatar plugin
│   ├── musetalk_avatar.py # MuseTalk avatar plugin
│   ├── ultralight_avatar.py # UltraLight avatar plugin
│   ├── wav2lip/           # Wav2Lip model modules (inference, face detection, audio)
│   ├── musetalk/          # MuseTalk model modules (unet, vae, whisper, face parsing)
│   └── ultralight/        # UltraLight model modules
│
├── tts/                   # Text-to-speech engines
│   ├── base_tts.py        # Abstract base: queue-based async TTS
│   ├── edge.py            # Microsoft Edge TTS (default)
│   ├── cosyvoice.py       # CosyVoice TTS
│   ├── fish.py            # FishSpeech TTS
│   ├── sovits.py          # GPT-SoVITS TTS
│   ├── xtts.py            # XTTSv2
│   ├── azure.py           # Azure Speech
│   ├── tencent.py         # Tencent TTS
│   ├── doubao.py          # DouBao TTS
│   ├── indextts2.py       # IndexTTS2
│   └── qwentts.py         # Qwen TTS
│
├── streamout/             # Output transport
│   ├── base_output.py     # Abstract base
│   ├── webrtc.py          # WebRTC output (default)
│   ├── rtmp.py            # RTMP push output
│   └── virtualcam.py      # Virtual camera output
│
├── server/                # HTTP server
│   ├── routes.py          # API route definitions
│   ├── rtc_manager.py     # WebRTC connection lifecycle
│   ├── session_manager.py # Session lifecycle (singleton)
│   ├── webrtc.py          # WebRTC MediaStreamTrack (HumanPlayer)
│   └── __init__.py
│
├── rag/                   # RAG Knowledge Base
│   ├── __init__.py        # Public API: build_rag_prompt, quick_retrieve
│   ├── embeddings.py      # DashScope Embedding client
│   ├── vector_store.py    # ChromaDB vector storage
│   ├── retriever.py       # Document retrieval
│   ├── config_loader.py   # Config loading + merge (3-tier)
│   ├── document_processor.py # Document chunking
│   └── loaders/           # Data source loaders
│       ├── file_loader.py     # PDF/TXT/MD/DOCX loader
│       ├── database_connector.py # MySQL/PG/SQLite connector
│       └── api_loader.py      # REST API fetcher
│
├── utils/                 # Utilities
│   ├── logger.py          # Logging setup
│   ├── device.py          # CUDA device management
│   ├── image.py           # Image I/O utilities
│   ├── audio.py           # Audio utilities
│   ├── audioutil.py       # Audio processing
│   └── async_utils.py     # Async helpers
│
├── tests/                 # Test suite (pytest)
│   ├── test_config_loader.py
│   ├── test_database_connector.py
│   ├── test_document_processor.py
│   ├── test_e2e_rag.py
│   ├── test_embeddings.py
│   ├── test_file_loader.py
│   ├── test_integration.py
│   ├── test_retriever.py
│   └── test_vector_store.py
│
├── data/                  # Runtime data
│   ├── avatars/           # Avatar reference data (images, videos)
│   └── chromadb/          # ChromaDB persistence directory
│
├── models/                # Pre-trained model files
├── web/                   # Frontend static files
│   ├── dashboard.html     # Main dashboard
│   ├── webrtcapi.html     # WebRTC test page
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript
│
├── docs/                  # Documentation
├── assets/                # Assets
└── .planning/             # GSD project management
```

## Naming Conventions

| Pattern | Example | Rule |
|---------|---------|------|
| Python files | `snake_case.py` | PEP 8 |
| Classes | `PascalCase` | `BaseAvatar`, `EdgeTTS`, `HumanPlayer` |
| Methods/Functions | `snake_case` | `put_msg_txt()`, `flush_talk()`, `build_rag_prompt()` |
| Constants | `UPPER_SNAKE` | `_RE_EMOJI`, `DASHSCOPE_API_KEY` |
| Private methods | `__double_leading` | `__main()`, `__create_bytes_stream()` |
| Plugins | `@register("cat", "name")` | `@register("tts", "edgetts")` |

## Key Entry Points

| File | Purpose |
|------|---------|
| `app.py:67-256` | `run_server()` — main startup, args, RAG init, HTTP server |
| `server/routes.py:184-194` | `setup_routes()` — all API endpoints |
| `llm.py:71` | `llm_response()` — LLM chat streaming handler |
| `avatars/base_avatar.py:125` | `put_msg_txt()` — text → TTS → audio pipeline entry |
| `avatars/base_avatar.py:309` | `inference()` — main inference loop |
| `avatars/base_avatar.py:366` | `process_frames()` — output processing loop |
| `server/session_manager.py:47` | `create_session()` — session factory |
