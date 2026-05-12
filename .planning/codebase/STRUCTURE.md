# Project Structure

**Analysis Date:** 2026/05/11

## Directory Layout

```
LiveTalking/
├── app.py                    # Main entry point, server initialization
├── config.py                 # CLI argument parsing
├── llm.py                    # LLM integration (Qwen/DashScope)
├── registry.py               # Plugin registry system
│
├── avatars/                  # Avatar rendering modules
│   ├── __init__.py
│   ├── base_avatar.py        # Core rendering pipeline
│   ├── musetalk_avatar.py    # MuseTalk implementation
│   ├── wav2lip_avatar.py     # Wav2Lip implementation
│   ├── ultralight_avatar.py  # UltraLight implementation
│   │
│   ├── audio_features/       # Audio feature extraction
│   │   ├── base_asr.py       # ASR base class
│   │   ├── whisper.py        # Whisper ASR
│   │   ├── hubert.py         # Hubert features
│   │   └── mel.py            # Mel spectrogram
│   │
│   ├── musetalk/             # MuseTalk model files
│   │   ├── models/           # VAE, UNet, SyncNet
│   │   ├── utils/            # Utilities, face detection
│   │   ├── whisper/          # Whisper model
│   │   └── genavatar.py      # Avatar generation
│   │
│   ├── wav2lip/              # Wav2Lip model files
│   │   ├── models/           # Wav2Lip model
│   │   ├── face_detection/   # Face detection
│   │   └── genavatar.py      # Avatar generation
│   │
│   └── ultralight/           # UltraLight model files
│       ├── unet.py           # UNet model
│       └── genavatar.py      # Avatar generation
│
├── tts/                      # Text-to-speech modules
│   ├── __init__.py
│   ├── base_tts.py           # TTS base class
│   ├── edge.py               # EdgeTTS (Microsoft)
│   ├── sovits.py             # GPT-SoVITS
│   ├── xtts.py               # XTTS
│   ├── cosyvoice.py          # CosyVoice
│   ├── fish.py               # FishTTS
│   ├── tencent.py            # Tencent TTS
│   ├── doubao.py             # Doubao TTS
│   ├── indextts2.py          # IndexTTS2
│   ├── azure.py              # Azure TTS
│   └── qwentts.py            # Qwen TTS
│
├── server/                   # Server infrastructure
│   ├── __init__.py
│   ├── routes.py             # API route handlers
│   ├── rtc_manager.py        # WebRTC connection manager
│   ├── session_manager.py    # Session lifecycle manager
│   └── webrtc.py             # WebRTC media tracks
│
├── streamout/                # Output streaming modules
│   ├── __init__.py
│   ├── base_output.py        # Output base class
│   ├── webrtc.py             # WebRTC output
│   ├── rtmp.py               # RTMP streaming
│   └── virtualcam.py         # Virtual camera output
│
├── utils/                    # Utility modules
│   ├── logger.py             # Logging configuration
│   ├── image.py              # Image processing utilities
│   └── device.py             # Device selection (CUDA/MPS/CPU)
│
├── web/                      # Static web files
│   ├── webrtcapi.html        # WebRTC client page
│   ├── rtmpapi.html          # RTMP client page
│   ├── rtcpushapi.html       # RTCPush client page
│   └── dashboard.html        # Integrated frontend
│
├── data/                     # Data directory
│   └── avatars/              # Avatar data files
│       └── {avatar_id}/      # Per-avatar files
│           ├── full_imgs/    # Full frame images
│           ├── coords.pkl    # Face coordinates
│           ├── latents.pt    # VAE latents
│           ├── mask/         # Face masks
│           └── avator_info.json
│
└── models/                   # Model weights (gitignored)
    ├── wav2lip.pth
    ├── whisper/
    └── ...
```

## Directory Purposes

### `avatars/`
- **Purpose**: Avatar rendering models and core pipeline
- **Contains**: Model implementations, audio feature extraction, base classes
- **Key files**:
  - `base_avatar.py` - Core rendering pipeline (478 lines)
  - `musetalk_avatar.py` - MuseTalk implementation (167 lines)

### `tts/`
- **Purpose**: Text-to-speech plugin implementations
- **Contains**: TTS backends for various providers
- **Key files**:
  - `base_tts.py` - Abstract base class
  - `edge.py` - Default TTS (EdgeTTS)

### `server/`
- **Purpose**: HTTP/WebRTC server infrastructure
- **Contains**: Route handlers, connection management, session management
- **Key files**:
  - `routes.py` - All API endpoints
  - `rtc_manager.py` - WebRTC connection lifecycle
  - `session_manager.py` - Avatar session management

### `streamout/`
- **Purpose**: Output transport implementations
- **Contains**: Streaming backends for different output modes
- **Key files**:
  - `base_output.py` - Abstract output interface
  - `webrtc.py` - WebRTC streaming
  - `rtmp.py` - RTMP push streaming

### `utils/`
- **Purpose**: Shared utility functions
- **Contains**: Logging, image processing, device selection
- **Key files**:
  - `logger.py` - Centralized logging

### `web/`
- **Purpose**: Static frontend files
- **Contains**: HTML pages for different transport modes
- **Generated**: No
- **Committed**: Yes

### `data/`
- **Purpose**: Runtime data storage
- **Contains**: Avatar assets, recordings
- **Generated**: Partially (recordings)
- **Committed**: Partially (avatar data)

### `models/`
- **Purpose**: Model weights and checkpoints
- **Contains**: Pre-trained model files
- **Generated**: No (downloaded separately)
- **Committed**: No (gitignored)

## Key File Locations

### Entry Points
| File | Purpose |
|------|---------|
| `app.py` | Main server entry point |
| `app.py:main()` | Initialization and server startup |
| `config.py:parse_args()` | CLI argument parsing |

### Configuration
| File | Purpose |
|------|---------|
| `config.py` | CLI arguments and defaults |
| Environment vars | `DASHSCOPE_API_KEY`, TTS server URLs |

### Core Logic
| File | Purpose |
|------|---------|
| `avatars/base_avatar.py` | Rendering pipeline |
| `server/session_manager.py` | Session lifecycle |
| `server/rtc_manager.py` | WebRTC management |
| `registry.py` | Plugin registry |

### Avatar Models
| File | Purpose |
|------|---------|
| `avatars/musetalk_avatar.py` | MuseTalk implementation |
| `avatars/wav2lip_avatar.py` | Wav2Lip implementation |
| `avatars/ultralight_avatar.py` | UltraLight implementation |

### TTS Plugins
| File | Purpose |
|------|---------|
| `tts/base_tts.py` | TTS base class |
| `tts/edge.py` | EdgeTTS (default) |
| `tts/sovits.py` | GPT-SoVITS |

### Output Modules
| File | Purpose |
|------|---------|
| `streamout/base_output.py` | Output interface |
| `streamout/webrtc.py` | WebRTC output |
| `streamout/rtmp.py` | RTMP output |
| `streamout/virtualcam.py` | Virtual camera |

### Testing
| File | Purpose |
|------|---------|
| No test files found | Testing not implemented |

## Naming Conventions

### Files
- **Python modules**: `snake_case.py` (e.g., `base_avatar.py`, `rtc_manager.py`)
- **Class files**: Match class name in snake_case (e.g., `musetalk_avatar.py` → `MuseReal`)
- **Base classes**: `base_*.py` prefix (e.g., `base_tts.py`, `base_asr.py`, `base_output.py`)

### Directories
- **Feature modules**: `snake_case/` (e.g., `avatars/`, `streamout/`)
- **Model-specific**: Match model name (e.g., `musetalk/`, `wav2lip/`, `ultralight/`)

### Classes
- **Base classes**: `Base{Feature}` (e.g., `BaseAvatar`, `BaseTTS`, `BaseASR`, `BaseOutput`)
- **Implementations**: Descriptive names (e.g., `MuseReal`, `WhisperASR`, `EdgeTTS`, `RTMPOutput`)

### Functions
- **Snake case**: `put_msg_txt()`, `inference_batch()`, `paste_back_frame()`
- **Private methods**: Single underscore prefix `_init_streamer()`, `_get_sliced_feature()`

## Where to Add New Code

### New Avatar Model
1. Create `avatars/{model_name}_avatar.py`
2. Implement class inheriting from `BaseAvatar`
3. Add `@register("avatar", "{model_name}")` decorator
4. Implement required methods:
   - `inference_batch(index, audiofeat_batch)`
   - `paste_back_frame(pred_frame, idx)`
5. Add module mapping in `app.py:_avatar_modules`
6. Create `avatars/{model_name}/` directory for model code

### New TTS Plugin
1. Create `tts/{name}.py`
2. Implement class inheriting from `BaseTTS`
3. Add `@register("tts", "{name}")` decorator
4. Implement `txt_to_audio(msg)` method
5. Add module mapping in `base_avatar.py:_tts_modules`

### New Output Transport
1. Create `streamout/{name}.py`
2. Implement class inheriting from `BaseOutput`
3. Add `@register("streamout", "{name}")` decorator
4. Implement required methods:
   - `start()`
   - `push_video_frame(frame)`
   - `push_audio_frame(frame)`
   - `stop()`
5. Add to `base_avatar.py:_output_modules`

### New API Endpoint
1. Add handler function in `server/routes.py`
2. Register route in `setup_routes()` function
3. Use `json_ok()` / `json_error()` for responses
4. Get session via `get_session(request, sessionid)`

### New Utility Function
1. Add to appropriate file in `utils/`
2. Create new file if distinct category
3. Import from `utils.{module}`

### New Avatar Data
1. Create directory `data/avatars/{avatar_id}/`
2. Generate files using `avatars/{model}/genavatar.py`:
   - `full_imgs/` - Full frame images
   - `coords.pkl` - Face coordinates
   - `latents.pt` - VAE latents
   - `mask/` - Face masks
   - `mask_coords.pkl` - Mask coordinates

## Special Directories

### `models/`
- **Purpose**: Model weights and checkpoints
- **Generated**: No (downloaded/trained externally)
- **Committed**: No (in `.gitignore`)
- **Contents**:
  - `wav2lip.pth` - Wav2Lip weights
  - `whisper/` - Whisper model
  - MuseTalk weights (VAE, UNet, etc.)

### `data/avatars/{avatar_id}/`
- **Purpose**: Per-avatar preprocessed data
- **Generated**: Yes (via `genavatar.py`)
- **Committed**: Typically yes (for deployment)
- **Required files**:
  - `full_imgs/` - Original frames
  - `coords.pkl` - Face bounding boxes
  - `latents.pt` - VAE encoded latents
  - `mask/` - Face region masks
  - `mask_coords.pkl` - Mask coordinates

### `web/`
- **Purpose**: Static frontend served by aiohttp
- **Generated**: No
- **Committed**: Yes
- **Access**: `http://server:port/{filename}`

### `.planning/codebase/`
- **Purpose**: Codebase analysis documents
- **Generated**: Yes (by GSD tools)
- **Committed**: Yes (for team reference)
- **Contents**:
  - `ARCHITECTURE.md` - System architecture
  - `STRUCTURE.md` - Project structure
  - `STACK.md` - Technology stack
  - `CONVENTIONS.md` - Coding conventions

## Import Patterns

### Absolute Imports
```python
from avatars.base_avatar import BaseAvatar
from server.session_manager import session_manager
from utils.logger import logger
import registry
```

### Plugin Loading (Dynamic)
```python
# In base_avatar.py
_tts_modules = {
    'edgetts': 'tts.edge',
    'gpt-sovits': 'tts.sovits',
    ...
}
importlib.import_module(_tts_modules[opt.tts])
self.tts = registry.create("tts", opt.tts, opt=opt, parent=self)
```

### TYPE_CHECKING Imports
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from avatars.base_avatar import BaseAvatar
```

---

*Structure analysis: 2026/05/11*
