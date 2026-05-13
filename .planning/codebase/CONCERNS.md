# Concerns

**Generated:** 2026-05-12
**Type:** Codebase Mapping

## Technical Debt

### 1. Edge-TTS Reliability (`tts/edge.py`)
- **Risk:** HIGH — Microsoft Edge TTS WebSocket API changes without notice
- **Evidence:** The hardcoded subscription key (`6A5AA1D4...`) is already blocked in older versions
- **Fix applied:** Upgraded edge-tts 7.2.3 → 7.2.8 (temporary, may break again)
- **Recommendation:** Add fallback TTS engine or monitor edge-tts releases

### 2. No LLM Streaming Tests (`llm.py`)
- **Risk:** MEDIUM — Streaming logic (segment detection, interrupt handling, text cleaning) has no automated tests
- **Evidence:** 0 test files reference `llm.py`
- **Impact:** Regression risk on prompt/logic changes

### 3. Thread Safety (`tts/edge.py:19`)
- **Risk:** LOW-MEDIUM — `asyncio.new_event_loop().run_until_complete()` called for every TTS segment
- **Evidence:** Each `txt_to_audio()` call creates a new event loop
- **Impact:** May leak event loops on repeated calls; no re-use

### 4. Mixed Chinese/English Logging
- **Risk:** LOW — Log messages mix Chinese and English inconsistently
- **Evidence:** `logger.info('start inference')` vs `logger.info(f"LLM segment: ...")`
- **Impact:** Cosmetic, but harder to grep for automation

### 5. Old Flask Import (`app.py:19`)
- **Risk:** LOW — `from flask import Flask` imported but not used (migrated to aiohttp)
- **Evidence:** `app = Flask(__name__)` initialized but never used for serving
- **Impact:** Dead code, confusing

## Performance Concerns

### 1. LLM TTFT (Time To First Token)
- **Description:** First token from Qwen-Plus takes 1-8 seconds
- **Root cause:** DashScope API latency (not client-side)
- **Mitigation:** Cached `_get_openai_client()` singleton saves ~274ms init time
- **Status:** Cannot fully resolve — depends on upstream API performance

### 2. TTS Serialization
- **Description:** Each TTS segment creates a new async event loop and WebSocket connection
- **Status:** Known but acceptable for current use case
- **Impact:** ~5s per TTS call overhead

### 3. Video Inference Latency
- **Description:** Wav2Lip inference at ~25fps on consumer GPU
- **Status:** Acceptable for real-time, bottleneck is model complexity

## Security Concerns

### 1. API Key Exposure Risk
- **Description:** `DASHSCOPE_API_KEY` read from env var at runtime
- **Risk:** LOW — standard practice, no hardcoded keys in code
- **Recommendation:** Ensure `.env` files are in `.gitignore`

### 2. STUN Server Config
- **Description:** Hardcoded `stun:stun.freeswitch.org:3478`
- **Risk:** LOW — public STUN server, no auth required
- **Recommendation:** Make configurable

## Fragile Areas

### 1. Segment Detection Logic (`llm.py:139-153`)
- **Why fragile:** Character-by-character punctuation detection, 5-char threshold, interrupt detection
- **Risk:** MODERATE — if model adds special characters or changes output format
- **Test gap:** No unit tests for streaming parser

### 2. RAG Mode Sync (`web/dashboard.html:606-625`)
- **Why fragile:** Async fetch + localStorage fallback; race condition possible on slow connections
- **Risk:** LOW — handled by fallback to localStorage default

### 3. ChromaDB Directory (`data/chromadb/`)
- **Why fragile:** ChromaDB persistence directory is hardcoded relative path
- **Risk:** LOW — breaks if CWD is not project root

## Known Issues (Recent Fixes)

| Issue | Status | Commit |
|-------|--------|--------|
| First response missing | ✅ Fixed | Threshold >5→>=5, interrupt detection |
| Mode persists on restart | ✅ Fixed | Frontend reads from server on load |
| stream_options 3-4x latency | ✅ Fixed | Removed `include_usage` param |
| Edge-TTS disconnect | ✅ Fixed | Upgraded 7.2.3→7.2.8 |
| RAG+Model prompt too verbose | ✅ Fixed | Added "简短" constraint |
