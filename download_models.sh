#!/bin/bash

# Base directory for models
MODELS_DIR="backend/comfyui/models"

# Create directories
mkdir -p "$MODELS_DIR/diffusion_models"
mkdir -p "$MODELS_DIR/text_encoders"
mkdir -p "$MODELS_DIR/vae"
mkdir -p "$MODELS_DIR/clip_vision"

# Function to download file if it doesn't exist
download_file() {
    url="$1"
    dest="$2"
    name="$3"

    if [ -f "$dest" ]; then
        echo "✅ $name already exists at $dest"
    else
        echo "⬇️  Downloading $name..."
        curl -L -o "$dest" "$url"
        if [ $? -eq 0 ]; then
            echo "✅ Successfully downloaded $name"
        else
            echo "❌ Failed to download $name"
            exit 1
        fi
    fi
}

echo "🚀 Starting model downloads for Wan 2.1 Video Generation..."
echo "This may take a while as the files are large (several GBs)."

# 1. Wan 2.1 I2V Model (480p)
download_file \
    "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/diffusion_models/wan2.1_i2v_480p_14B_fp16.safetensors" \
    "$MODELS_DIR/diffusion_models/wan2.1_i2v_480p_14B_fp16.safetensors" \
    "Wan 2.1 I2V Model"

# 2. T5 Encoder
download_file \
    "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" \
    "$MODELS_DIR/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" \
    "T5 Encoder"

# 3. VAE
download_file \
    "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors" \
    "$MODELS_DIR/vae/wan_2.1_vae.safetensors" \
    "Wan VAE"

# 4. CLIP Vision
download_file \
    "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors" \
    "$MODELS_DIR/clip_vision/clip_vision_h.safetensors" \
    "CLIP Vision Model"

echo "🎉 All downloads complete!"
echo "Please restart your ComfyUI server to load the new models."
