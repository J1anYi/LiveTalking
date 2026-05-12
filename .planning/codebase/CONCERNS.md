# Project Overview & Startup Guide

**Analysis Date:** 2026/05/11

## What is This Project?

LiveTalking is a **real-time interactive streaming digital human system** that achieves synchronized audio-video dialogue. It generates a lip-synced digital avatar that can speak text input in real-time, suitable for virtual presenters, AI assistants, and interactive streaming applications.

The system supports multiple avatar models (wav2lip, musetalk, ultralight) and can output via WebRTC, RTMP push, or virtual camera. It integrates with various TTS services and LLM providers for conversational capabilities.

## Key Features

1. **Multiple Digital Human Models**: wav2lip, musetalk, Ultralight-Digital-Human
2. **Real-time Lip Sync**: Audio-driven facial animation with synchronized lip movements
3. **Voice Cloning**: Support for multiple TTS services with voice customization
4. **Speech Interruption**: Digital human can be interrupted while speaking
5. **WebRTC Output**: Real-time streaming via WebRTC protocol
6. **Virtual Camera Output**: Direct output to virtual camera for OBS/meeting software
7. **Custom Action Choreography**: Play custom videos when the digital human is not speaking
8. **Multi-concurrency**: Support multiple simultaneous sessions

## How to Start

### Prerequisites

- [ ] Python 3.10+
- [ ] CUDA 12.4 compatible GPU (RTX 3060+ for wav2lip, RTX 3080Ti+ for musetalk)
- [ ] FFmpeg with libx264 support
- [ ] Conda (recommended for environment management)

### Hardware Requirements

| Model | Minimum GPU | Recommended GPU |
|-------|-------------|-----------------|
| wav2lip256 | RTX 3060 (60 fps) | RTX 3080Ti (120 fps) |
| musetalk | RTX 3080Ti (42 fps) | RTX 4090 (72 fps) |
| ultralight | Lower requirements | - |

### Installation Steps

```bash
# Step 1: Create conda environment
conda create -n nerfstream python=3.10
conda activate nerfstream

# Step 2: Install PyTorch (CUDA 12.4)
# Check your CUDA version first: nvidia-smi
# For CUDA 12.4:
conda install pytorch==2.5.0 torchvision==0.20.0 torchaudio==2.5.0 pytorch-cuda=12.4 -c pytorch -c nvidia

# Step 3: Install dependencies
pip install -r requirements.txt
```

### Model Download

Download from Quark Cloud Drive: https://pan.quark.cn/s/83a750323ef0
Or Google Drive: https://drive.google.com/drive/folders/1FOC_MD6wdogyyX_7V1d4NDIO7P9NlSAJ

Required files for wav2lip:
1. `wav2lip256.pth` -> copy to `models/wav2lip.pth`
2. `wav2lip256_avatar1.tar.gz` -> extract and copy folder to `data/avatars/`

### Running the Server

```bash
# Basic run with WebRTC output
python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar1

# With musetalk model
python app.py --transport webrtc --model musetalk --avatar_id musetalk_avatar

# With custom TTS
python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar1 --tts gpt-sovits --TTS_SERVER http://127.0.0.1:9880
```

### Access the Web Interface

After starting the server, access:
- WebRTC client: `http://<serverip>:8010/webrtcapi.html`
- Dashboard: `http://<serverip>:8010/dashboard.html`

## Configuration Options

### CLI Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--model` | wav2lip | Avatar model: musetalk/wav2lip/ultralight |
| `--avatar_id` | wav2lip256_avatar1 | Avatar ID in data/avatars |
| `--tts` | edgetts | TTS plugin: edgetts/gpt-sovits/cosyvoice/fishtts/tencent/doubao/indextts2/azuretts/qwentts |
| `--transport` | webrtc | Output: webrtc/rtcpush/rtmp/virtualcam |
| `--listenport` | 8010 | Web listen port |
| `--batch_size` | 16 | Inference batch size |
| `--fps` | 25 | Video FPS (must be 25) |
| `--max_session` | 1 | Maximum concurrent sessions |
| `--customvideo_config` | '' | Path to custom action JSON config |
| `--REF_FILE` | zh-CN-YunxiaNeural | Reference file or voice model ID for TTS |
| `--TTS_SERVER` | http://127.0.0.1:9880 | TTS server URL |
| `--push_url` | http://localhost:1985/rtc/v1/whip/... | Push URL for rtcpush mode |

### Environment Variables

| Variable | Purpose | Required For |
|----------|---------|--------------|
| `DASHSCOPE_API_KEY` | Alibaba Qwen LLM API key | LLM chat mode |
| `HF_ENDPOINT` | HuggingFace mirror URL | Download models in China |
| `AZURE_SPEECH_KEY` | Azure Speech service key | Azure TTS |
| `AZURE_TTS_REGION` | Azure Speech region | Azure TTS |
| `TENCENT_APPID` | Tencent Cloud AppID | Tencent TTS |
| `TENCENT_SECRET_KEY` | Tencent Cloud secret key | Tencent TTS |
| `TENCENT_SECRET_ID` | Tencent Cloud secret ID | Tencent TTS |
| `DOUBAO_APPID` | Doubao AppID | Doubao TTS |
| `DOUBAO_TOKEN` | Doubao token | Doubao TTS |

### TTS Configuration

Available TTS plugins in `tts/` directory:
- `edge.py` - EdgeTTS (Microsoft Edge TTS, free)
- `azure.py` - Azure Cognitive Services TTS
- `tencent.py` - Tencent Cloud TTS
- `doubao.py` - Doubao TTS
- `sovits.py` - GPT-SoVITS (voice cloning)
- `cosyvoice.py` - CosyVoice
- `fish.py` - Fish-Speech TTS
- `indextts2.py` - IndexTTS2
- `qwentts.py` - Qwen TTS
- `xtts.py` - XTTS

Example for GPT-SoVITS:
```bash
python app.py --tts gpt-sovits --TTS_SERVER http://127.0.0.1:9880 --REF_FILE reference.wav --REF_TEXT "参考文本"
```

### Custom Video Config

File: `data/custom_config.json`

```json
[
   {
        "audiotype": 2,
        "imgpath": "data/customvideo/image",
        "audiopath": "data/customvideo/audio.wav"
   }
]
```

Use with: `--customvideo_config data/custom_config.json`

## Network Requirements

- **TCP port 8010** (configurable via `--listenport`)
- **UDP ports 1-65536** for WebRTC (must be open on firewall)

For cloud deployment (AutoDL), UDP ports may be restricted and require TURN/SRS service.

## Docker Quick Start

```bash
docker run --gpus all -it --network=host --rm registry.cn-zhangjiakou.aliyuncs.com/codewithgpu3/lipku-livetalking:toza2irpHZ
```

Code is in `/root/livetalking`. Run `git pull` first for latest code.

## Common Issues

### 1. HuggingFace Access Issues (China)

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### 2. pytorch3d Installation Fails

```bash
git clone https://github.com/facebookresearch/pytorch3d.git
python setup.py install
```

### 3. WebSocket Connection Error

Modify `python/site-packages/flask_sockets.py`:
```python
# Change:
self.url_map.add(Rule(rule, endpoint=f))
# To:
self.url_map.add(Rule(rule, endpoint=f, websocket=True))
```

### 4. Protobuf Version Issues

```bash
pip uninstall protobuf
pip install protobuf==3.20.1
```

### 5. FFmpeg Version for RTMP

FFmpeg must have libx264 support. Check with `ffmpeg` command output.

### 6. Video Not Loading

Ensure firewall allows UDP ports for WebRTC. For restricted environments, deploy SRS or TURN service.

## Performance Notes

- **inferfps**: GPU inference frame rate (should be >25 for real-time)
- **finalfps**: Final streaming frame rate (should be >25 for real-time)
- If `inferfps > 25` but `finalfps < 25`: CPU performance insufficient
- Both CPU and GPU affect concurrent session capacity

---

*Project analysis: 2026/05/11*
