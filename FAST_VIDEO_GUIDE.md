# Fast Long Video Generation Guide

## Current Setup (1x H100)
- **5 sec video**: ~4-5 minutes
- **30 sec video**: ~25-30 minutes
- **60 sec video**: ~50-60 minutes

---

## Option 1: Parallel Workers (6x Speedup) ⭐ RECOMMENDED

Spin up multiple cheaper GPUs and generate chunks in parallel.

### Setup: 6x A40 Workers ($2.40/hr total)

1. **Create 6 RunPod pods** with these settings:
   - GPU: A40 (48GB VRAM) @ $0.40/hr each
   - Template: RunPod PyTorch
   - Volume: 100GB
   - HTTP Port: 8188

2. **On each pod**, run the setup:
```bash
cd /workspace && git clone https://github.com/mrbhandari-hub/pixeldojo.git && cd pixeldojo && chmod +x runpod_setup.sh && ./runpod_setup.sh
```

3. **Update your `.env`** with all worker URLs:
```env
COMFYUI_WORKERS=https://pod1-8188.proxy.runpod.net,https://pod2-8188.proxy.runpod.net,https://pod3-8188.proxy.runpod.net,https://pod4-8188.proxy.runpod.net,https://pod5-8188.proxy.runpod.net,https://pod6-8188.proxy.runpod.net
```

### Results with 6 Workers:
| Duration | Time | Cost |
|----------|------|------|
| 5 sec | ~1 min | $0.04 |
| 30 sec | ~5 min | $0.20 |
| 60 sec | ~10 min | $0.40 |

---

## Option 2: Single Bigger GPU (Simpler)

Use a more powerful GPU for faster per-frame generation.

| GPU | VRAM | Time for 30s | Cost/hr | Total Cost |
|-----|------|--------------|---------|------------|
| H100 SXM | 80GB | ~25 min | $2.69 | $1.12 |
| H200 | 141GB | ~15 min | ~$4.00 | $1.00 |
| 8x A100 | 640GB | ~5 min | ~$15.00 | $1.25 |

---

## Option 3: Reduce Quality for Speed

### A. Use FP8 Quantized Model (2x faster)

Update workflow to use FP8:
```json
"weight_dtype": "fp8_e4m3fn"
```

Download FP8 model:
```bash
wget -O models/unet/wan2.1_i2v_480p_14B_fp8.safetensors \
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/diffusion_models/wan2.1_i2v_480p_14B_fp8_e4m3fn_scaled.safetensors"
```

### B. Reduce Sampling Steps (1.5x faster)

Change from 30 to 20 steps in workflow:
```json
"steps": 20
```

### C. Lower Resolution (2x faster)

Change resolution in WanImageToVideo node:
```json
"width": 640,
"height": 360
```

### Combined: FP8 + 20 steps + 360p = **~6x faster**
- 30 sec video in ~4-5 minutes on single H100

---

## Option 4: Video Extension Pipeline

Instead of generating all frames at once, generate a seed and extend:

1. Generate 3-sec seed video
2. Use video extension to add more frames
3. Repeat until desired length

This can be parallelized for even faster results.

---

## Quick Comparison

| Method | 30 sec Video Time | Setup Complexity | Cost |
|--------|-------------------|------------------|------|
| 1x H100 (current) | 25 min | Easy | $1.12 |
| 6x A40 parallel | 5 min | Medium | $0.20 |
| 1x H100 + FP8 + low qual | 8 min | Easy | $0.36 |
| 1x H200 | 15 min | Easy | $1.00 |

---

## My Recommendation

**For fastest results**: Use 6x A40 parallel workers
**For best quality/speed**: Use H100 + FP8 model + 20 steps
**For simplicity**: Keep current H100, accept longer generation times



