#!/bin/bash

# RunPod Setup Script for PixelDojo
# Run this script inside your RunPod terminal

echo "🚀 Starting PixelDojo Cloud Setup..."

# 1. Install System Dependencies
echo "📦 Installing system dependencies..."
apt-get update && apt-get install -y ffmpeg git wget

# 2. Setup Workspace
cd /workspace
if [ ! -d "ComfyUI" ]; then
    echo "📥 Cloning ComfyUI..."
    git clone https://github.com/comfyanonymous/ComfyUI.git
    cd ComfyUI
    pip install -r requirements.txt
else
    echo "✅ ComfyUI already exists"
    cd ComfyUI
fi

# 3. Install Manager & Custom Nodes
echo "🔌 Installing Custom Nodes..."
cd custom_nodes

# ComfyUI Manager
if [ ! -d "ComfyUI-Manager" ]; then
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
fi

# VideoHelperSuite (Required for video export)
if [ ! -d "ComfyUI-VideoHelperSuite" ]; then
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
    cd ComfyUI-VideoHelperSuite
    pip install -r requirements.txt
    cd ..
fi

cd .. # Back to ComfyUI root

# 4. Download Models (Wan 2.1 & LTX Video)
echo "⬇️  Downloading Models (This may take a while)..."

# Create directories
mkdir -p models/diffusion_models
mkdir -p models/text_encoders
mkdir -p models/vae
mkdir -p models/clip_vision
mkdir -p models/checkpoints

# --- Wan 2.1 Models ---
echo "Downloading Wan 2.1 Models..."
wget -nc -P models/diffusion_models/ https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/diffusion_models/wan2.1_i2v_480p_14B_fp16.safetensors
wget -nc -P models/text_encoders/ https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors
wget -nc -P models/vae/ https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors
wget -nc -P models/clip_vision/ https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors

# --- LTX Video Models (Alternative) ---
echo "Downloading LTX Video Models..."
wget -nc -P models/checkpoints/ https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.1.safetensors

echo "✅ Setup Complete!"
echo "To start ComfyUI, run:"
echo "python main.py --listen 0.0.0.0 --port 8188"
