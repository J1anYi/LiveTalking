# Technology Stack

## Runtime Environment
- Python version: 3.10+
- CUDA/PyTorch version: CUDA 12.4 / PyTorch 2.5.0 (recommended)
- OS support: Linux (Ubuntu 20.04/24.04), Windows, macOS

## Core Dependencies

### Deep Learning / AI
| Library | Version | Purpose |
|---------|---------|---------|
| torch | 2.5.0 | Deep learning framework for model inference |
| torchvision | 0.20.0 | Image processing for vision models |
| transformers | 4.46.2 | HuggingFace models (Hubert, etc.) |
| diffusers | - | Diffusion model support |
| accelerate | - | Accelerated inference |
| lpips | 0.1.3 | Learned perceptual image similarity |
| tensorboardX | - | Training visualization |

### Web / Streaming
| Library | Version | Purpose |
|---------|---------|---------|
| aiohttp | - | Async HTTP server |
| aiohttp_cors | - | CORS support for aiohttp |
| aiortc | - | WebRTC implementation in Python |
| websockets | 12.0 | WebSocket client/server |
| flask | - | Web framework (legacy support) |
| flask_sockets | - | Flask WebSocket extension |
| gradio_client | - | Gradio API client for TTS services |

### Audio / Video
| Library | Version | Purpose |
|---------|---------|---------|
| opencv-python | - | Video/image processing |
| opencv-python-headless | - | Headless OpenCV for servers |
| ffmpeg-python | - | FFmpeg wrapper for media processing |
| librosa | - | Audio analysis and feature extraction |
| soundfile | 0.12.1 | Audio file I/O |
| resampy | - | Audio resampling |
| python_speech_features | - | Speech feature extraction (MFCC) |
| edge_tts | - | Microsoft Edge TTS client |
| azure-cognitiveservices-speech | - | Azure Speech SDK |
| imageio-ffmpeg | - | Video reading/writing |

### Scientific Computing
| Library | Version | Purpose |
|---------|---------|---------|
| numpy | - | Numerical computing |
| scipy | - | Scientific algorithms |
| pandas | - | Data manipulation |
| scikit-learn | - | Machine learning utilities |
| numba | - | JIT compilation for performance |

### 3D / Rendering
| Library | Version | Purpose |
|---------|---------|---------|
| trimesh | - | 3D mesh processing |
| PyMCubes | - | Marching cubes algorithm |
| dearpygui | - | GUI (optional) |

### Utilities
| Library | Version | Purpose |
|---------|---------|---------|
| omegaconf | - | Configuration management |
| configargparse | - | CLI + config file parsing |
| rich | - | Rich text/progress display |
| tqdm | - | Progress bars |
| packaging | - | Version handling |
| einops | - | Tensor operations |

## GPU Requirements

- Minimum GPU: NVIDIA GPU with 4GB VRAM (basic inference)
- Recommended GPU: NVIDIA GPU with 8GB+ VRAM (production use)
- CUDA version: 11.6+ (tested with 12.4)
- cuDNN version: 8+ (bundled with CUDA container)

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| Memory | 8GB | 16GB+ |
| GPU VRAM | 4GB | 8GB+ |
| Storage | 5GB | 10GB+ (for models) |

## Docker Support

Base image: `nvcr.io/nvidia/cuda:11.6.1-cudnn8-devel-ubuntu20.04`

Pre-built image available:
```
registry.cn-beijing.aliyuncs.com/codewithgpu2/lipku-metahuman-stream:2K9qaMBu8v
```
