#!/bin/bash
# ============================================
# PixelDojo - Complete RunPod Setup Script
# ============================================
# Run this in your RunPod web terminal!

set -e

echo "🚀 Starting PixelDojo RunPod Setup..."
echo ""

cd /workspace

# Install ComfyUI if not present
if [ ! -d "ComfyUI" ]; then
    echo "📦 Cloning ComfyUI..."
    git clone https://github.com/comfyanonymous/ComfyUI.git
fi

cd ComfyUI

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create model directories
echo "📁 Creating model directories..."
mkdir -p models/diffusion_models
mkdir -p models/text_encoders  
mkdir -p models/vae
mkdir -p models/clip_vision
mkdir -p models/unet

# Download Wan 2.1 models
echo ""
echo "⬇️  Downloading Wan 2.1 models (this will take a while)..."
echo ""

# 1. Wan 2.1 I2V Model (~28GB) - This goes in unet folder for UNETLoader
echo "📥 [1/4] Downloading Wan 2.1 I2V Model (~28GB)..."
wget -c --show-progress -O models/unet/wan2.1_i2v_480p_14B_fp16.safetensors \
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/diffusion_models/wan2.1_i2v_480p_14B_fp16.safetensors"

# 2. T5 Encoder (~5GB) - This goes in clip folder for CLIPLoader
echo "📥 [2/4] Downloading T5 Encoder (~5GB)..."
mkdir -p models/clip
wget -c --show-progress -O models/clip/umt5_xxl_fp8_e4m3fn_scaled.safetensors \
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"

# 3. VAE (~335MB)
echo "📥 [3/4] Downloading VAE (~335MB)..."
wget -c --show-progress -O models/vae/wan_2.1_vae.safetensors \
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors"

# 4. CLIP Vision (~3.9GB)
echo "📥 [4/4] Downloading CLIP Vision (~3.9GB)..."
wget -c --show-progress -O models/clip_vision/clip_vision_h.safetensors \
  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors"

echo ""
echo "✅ All models downloaded!"
echo ""
echo "🎬 Starting ComfyUI server..."
echo "   The server will be available on port 8188"
echo ""

# Start ComfyUI
python main.py --listen 0.0.0.0 --port 8188

