#!/bin/bash

# RunPod Setup Script for PixelDojo
# Run this script inside your RunPod terminal

set -e  # Exit on error

echo "🚀 Starting PixelDojo Cloud Setup..."

# 1. Install System Dependencies
echo "📦 Installing system dependencies..."
apt-get update && apt-get install -y ffmpeg git wget python3-pip

# 2. Setup Workspace
cd /workspace

# Use existing ComfyUI if available (RunPod templates often have it)
if [ -d "runpod-slim/ComfyUI" ]; then
    echo "✅ Using existing ComfyUI at runpod-slim/ComfyUI"
    COMFY_DIR="/workspace/runpod-slim/ComfyUI"
elif [ -d "ComfyUI" ]; then
    echo "✅ Using existing ComfyUI"
    COMFY_DIR="/workspace/ComfyUI"
else
    echo "📥 Cloning ComfyUI..."
    git clone https://github.com/comfyanonymous/ComfyUI.git
    COMFY_DIR="/workspace/ComfyUI"
    cd ComfyUI
    pip install -r requirements.txt
fi

cd "$COMFY_DIR"

# 3. Install Custom Nodes
echo "🔌 Installing Custom Nodes..."
mkdir -p custom_nodes
cd custom_nodes

# ComfyUI Manager
if [ ! -d "ComfyUI-Manager" ]; then
    echo "Installing ComfyUI-Manager..."
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
fi

# VideoHelperSuite (Required for video export)
echo "Installing ComfyUI-VideoHelperSuite..."
if [ -d "ComfyUI-VideoHelperSuite" ]; then
    echo "Removing existing VideoHelperSuite for clean install..."
    rm -rf ComfyUI-VideoHelperSuite
fi

git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
cd ComfyUI-VideoHelperSuite

# Install VHS dependencies
echo "Installing VideoHelperSuite dependencies..."
pip install imageio imageio-ffmpeg opencv-python-headless

# Check if requirements.txt exists and install
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Run install.py if it exists
if [ -f "install.py" ]; then
    echo "Running VHS install.py..."
    python3 install.py || echo "Warning: install.py had issues but continuing..."
fi

cd ..

# WAN 2.1 Wrapper (for image-to-video)
if [ ! -d "ComfyUI-WanVideoWrapper" ]; then
    echo "Installing WAN Video Wrapper..."
    git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git
    cd ComfyUI-WanVideoWrapper
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    cd ..
fi

cd "$COMFY_DIR"

# 4. Create Model Directories (using ComfyUI's expected folder names)
echo "📁 Creating model directories..."
mkdir -p models/unet          # For UNETLoader
mkdir -p models/clip          # For CLIPLoader  
mkdir -p models/vae           # For VAELoader
mkdir -p models/clip_vision   # For CLIP Vision
mkdir -p models/checkpoints

# 5. Download Models
echo "⬇️  Downloading Models (This may take a while)..."

# --- Wan 2.1 Models (Image-to-Video) ---
echo "Downloading Wan 2.1 I2V Model (~28GB)..."
if [ ! -f "models/unet/wan2.1_i2v_480p_14B_fp16.safetensors" ]; then
    wget -c --show-progress -P models/unet/ \
        "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/diffusion_models/wan2.1_i2v_480p_14B_fp16.safetensors"
fi

echo "Downloading Wan 2.1 Text Encoder (~5GB)..."
if [ ! -f "models/clip/umt5_xxl_fp8_e4m3fn_scaled.safetensors" ]; then
    wget -c --show-progress -P models/clip/ \
        "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
fi

echo "Downloading Wan 2.1 VAE (~335MB)..."
if [ ! -f "models/vae/wan_2.1_vae.safetensors" ]; then
    wget -c --show-progress -P models/vae/ \
        "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors"
fi

echo "Downloading CLIP Vision (~3.9GB)..."
if [ ! -f "models/clip_vision/clip_vision_h.safetensors" ]; then
    wget -c --show-progress -P models/clip_vision/ \
        "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors"
fi

# 6. Verify Installation
echo ""
echo "🔍 Verifying installation..."
echo "Custom nodes installed:"
ls -la custom_nodes/

echo ""
echo "Checking VideoHelperSuite..."
if [ -d "custom_nodes/ComfyUI-VideoHelperSuite/videohelpersuite" ]; then
    echo "✅ VideoHelperSuite module found"
else
    echo "⚠️  VideoHelperSuite module NOT found - may need manual fix"
fi

echo ""
echo "Models downloaded:"
echo "  UNET:"; ls models/unet/*.safetensors 2>/dev/null || echo "    (none)"
echo "  CLIP:"; ls models/clip/*.safetensors 2>/dev/null || echo "    (none)"
echo "  VAE:"; ls models/vae/*.safetensors 2>/dev/null || echo "    (none)"
echo "  CLIP Vision:"; ls models/clip_vision/*.safetensors 2>/dev/null || echo "    (none)"

echo ""
echo "============================================"
echo "✅ Setup Complete!"
echo "============================================"
echo ""
echo "🚀 Starting ComfyUI server on port 8188..."
echo ""

# Auto-start ComfyUI
python main.py --listen 0.0.0.0 --port 8188
