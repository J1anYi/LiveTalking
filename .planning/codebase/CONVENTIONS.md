# Coding Conventions

**Analysis Date:** 2026-05-11

## Python Style

**Python Version:**
- Not explicitly pinned in requirements.txt
- Uses modern Python features: dataclasses, TYPE_CHECKING, typing module, walrus operator
- Compatible with Python 3.9+ (type hint syntax with `list[...]`)

**Type Hints Usage:**
- Partial adoption throughout codebase
- Used for critical interfaces: `NDArray[np.float32]`, `tuple[str, dict]`
- `TYPE_CHECKING` pattern for avoiding circular imports (see `tts/base_tts.py`, `streamout/base_output.py`)
- Return types often omitted for private methods

**Import Style:**
- Standard library first, third-party second, local imports last
- Absolute imports preferred: `from utils.logger import logger`
- Lazy imports in some performance-critical paths: `importlib.import_module()` pattern in `app.py`

## Naming Conventions

**Files:**
- Pattern: lowercase with underscores (snake_case)
- Examples: `base_avatar.py`, `session_manager.py`, `musetalk_avatar.py`
- Test files: None present (should be `test_*.py` or `*_test.py`)

**Classes:**
- Pattern: PascalCase
- Base classes prefixed with `Base`: `BaseAvatar`, `BaseTTS`, `BaseOutput`
- Concrete implementations: `MuseReal`, `EdgeTTS`, `WebRTCOutput`
- Singleton pattern: `SessionManager` with `_instance` class variable

**Functions:**
- Pattern: snake_case
- Examples: `load_model()`, `parse_args()`, `build_avatar_session()`
- Private methods: single underscore prefix (`_init_streamer()`, `_rand_session_id()`)
- Factory functions: `load_model()`, `load_avatar()`, `warm_up()`

**Variables:**
- Pattern: snake_case
- Examples: `frame_list_cycle`, `input_stream`, `avatar_session`
- Constants: UPPER_CASE in module scope (`_REGISTRY`)

**Parameters:**
- Descriptive names: `quit_event`, `audio_chunk`, `eventpoint`
- Common parameter: `opt` for configuration/options object

## Architecture Patterns

### Plugin Pattern (Registry)

The codebase uses a decorator-based plugin registry system defined in `registry.py`:

**Registration:**
```python
from registry import register

@register("tts", "edgetts")
class EdgeTTS(BaseTTS):
    ...

@register("streamout", "webrtc")
class WebRTCOutput(BaseOutput):
    ...
```

**Creation:**
```python
import registry
self.tts = registry.create("tts", opt.tts, opt=opt, parent=self)
```

**Categories:**
- `"stt"` - Speech-to-text (ASR)
- `"llm"` - Large language models
- `"tts"` - Text-to-speech
- `"avatar"` - Digital human models (musetalk, wav2lip, ultralight)
- `"streamout"` - Output streams (webrtc, rtmp, virtualcam)

**Plugin Discovery:**
- Plugins registered at import time via `@register` decorator
- Module mapping in `app.py` determines which modules to import:
```python
_avatar_modules = {
    'musetalk': 'avatars.musetalk_avatar',
    'wav2lip': 'avatars.wav2lip_avatar',
    'ultralight': 'avatars.ultralight_avatar',
}
importlib.import_module(_avatar_modules[opt.model])
```

### Base Class Pattern

Base classes define contracts using ABC (Abstract Base Classes):

**Example from `streamout/base_output.py`:**
```python
from abc import ABC, abstractmethod

class BaseOutput(ABC):
    def __init__(self, opt=None, parent: Optional['BaseAvatar'] = None, **kwargs):
        self.opt = opt
        self.parent = parent

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def push_video_frame(self, frame) -> None: ...

    @abstractmethod
    def push_audio_frame(self, frame: NDArray[np.int16], eventpoint=None) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...
```

**Pattern:**
1. `__init__` accepts `opt` and `parent` parameters
2. Abstract methods define the interface contract
3. Concrete implementations register themselves
4. Optional methods provide default implementations (e.g., `get_buffer_size()`)

### Async Pattern

**Mixed threading and asyncio:**
- Threading: Used for inference pipeline (`Thread`, `Event`, `Queue`)
- Asyncio: Used for WebRTC (`aiortc`) and HTTP server (`aiohttp`)

**Bridging sync/async:**
```python
# In server/routes.py - running sync function in executor
asyncio.get_event_loop().run_in_executor(
    None, llm_response, params['text'], avatar_session, datainfo
)

# In server/session_manager.py - building session in thread pool
avatar_session = await asyncio.get_event_loop().run_in_executor(
    None, self.build_session_fn, sessionid, params
)
```

**Thread-based pipeline:**
```python
# In avatars/base_avatar.py
infer_thread = Thread(target=self.inference, args=(infer_quit_event,))
infer_thread.start()

process_thread = Thread(target=self.process_frames, args=(process_quit_event,))
process_thread.start()
```

### Singleton Pattern

Used for global managers:

```python
# In server/session_manager.py
class SessionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

session_manager = SessionManager()  # Module-level singleton
```

## Logging

**Framework:** Python standard library `logging`

**Setup (from `utils/logger.py`):**
```python
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler = logging.FileHandler('livetalking.log')
fhandler.setFormatter(formatter)
fhandler.setLevel(logging.INFO)
logger.addHandler(fhandler)
```

**Usage Pattern:**
- Import: `from utils.logger import logger`
- Info: `logger.info(f'Creating session {sessionid}')`
- Errors: `logger.exception('edgetts')` or `logger.error('message')`
- Debug: `logger.debug('sleep qsize=%d', buffer_size)`

**Language:** Log messages are primarily in Chinese

## Error Handling

**Exception Logging:**
```python
try:
    # operation
except Exception as e:
    logger.exception('operation_name:')
    return json_error(str(e))
```

**API Response Pattern (from `server/routes.py`):**
```python
def json_ok(data=None):
    return web.Response(
        content_type="application/json",
        text=json.dumps({"code": 0, "msg": "ok", "data": data}),
    )

def json_error(msg: str, code: int = -1):
    return web.Response(
        content_type="application/json",
        text=json.dumps({"code": code, "msg": str(msg)}),
    )
```

**Graceful Degradation:**
- Resampling fallback in `utils/audio.py` if resampy unavailable
- Device detection fallback in `utils/device.py` (CUDA -> MPS -> CPU)

## Documentation

**License Headers:**
- Apache 2.0 license header in major files
- Copyright attribution format in `avatars/base_avatar.py`, `avatars/musetalk_avatar.py`

**Docstrings:**
- Minimal usage
- Present in `registry.py` for public API:
```python
def register(category: str, name: str):
    """
    装饰器：注册插件类到全局注册表。

    用法::
        @register("tts", "edgetts")
        class EdgeTTS(BaseTTS): ...
    """
```

**Comments:**
- Chinese comments throughout codebase
- Section separators using `# --- Section Name ---------` pattern in `config.py`
- TODO markers: `# todo: 还可以主动调 avatar_session 释放` in `session_manager.py`

## Function Design

**Size:** Functions range from small utility functions to larger methods (50+ lines for `inference()` in `base_avatar.py`)

**Parameters:**
- Configuration via `opt` object (argparse Namespace)
- `**kwargs` for extensibility in base classes
- Event/queue-based communication between threads

**Return Values:**
- Factory functions return model/avatar tuples
- API handlers return aiohttp `web.Response`
- Inference methods modify queues rather than returning values

## Module Design

**Exports:**
- Public classes/functions at module level
- Private helpers with underscore prefix
- `__init__.py` files minimal or empty

**Barrel Files:** Not used - direct imports preferred

**Module Structure:**
```
tts/
  __init__.py
  base_tts.py      # Base class
  edge.py          # Concrete implementation
  cosyvoice.py     # Concrete implementation
  ...
```

## Key Files Reference

| Purpose | File Path |
|---------|-----------|
| Entry point | `app.py` |
| CLI config | `config.py` |
| Plugin registry | `registry.py` |
| Logger setup | `utils/logger.py` |
| Base avatar | `avatars/base_avatar.py` |
| Base TTS | `tts/base_tts.py` |
| Base output | `streamout/base_output.py` |
| Session manager | `server/session_manager.py` |
| API routes | `server/routes.py` |

---

*Convention analysis: 2026-05-11*
