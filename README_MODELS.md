# Required Models for Wan 2.1 Video Generation

To use the video generation features, you must download the following models and place them in the correct directories within `backend/comfyui/models/`.

## 1. Diffusion Model (Wan 2.1 I2V)
Download the Wan 2.1 Image-to-Video model (480p or 720p).
*   **Filename:** `wan2.1_i2v_480p_14B_fp16.safetensors` (or similar)
*   **Location:** `backend/comfyui/models/diffusion_models/` (or `unet/` if using UNETLoader)
*   **Source:** HuggingFace (Wan-AI/Wan2.1-I2V-14B-480P)

## 2. Text Encoder (T5)
Download the T5 encoder.
*   **Filename:** `umt5_xxl_fp8_e4m3fn_scaled.safetensors`
*   **Location:** `backend/comfyui/models/text_encoders/` (or `clip/`)
*   **Source:** Comfy-Org/Wan_2.1_ComfyUI_repackaged

## 3. VAE
Download the Wan VAE.
*   **Filename:** `wan_2.1_vae.safetensors`
*   **Location:** `backend/comfyui/models/vae/`
*   **Source:** Comfy-Org/Wan_2.1_ComfyUI_repackaged

## 4. CLIP Vision
Download the CLIP Vision model for image conditioning.
*   **Filename:** `clip_vision_h.safetensors`
*   **Location:** `backend/comfyui/models/clip_vision/`

## Important Note
After downloading these models, you may need to restart the ComfyUI server:
```bash
# In backend/comfyui
pkill -f "python main.py"
source venv/bin/activate
python main.py --listen 127.0.0.1 --port 8188
```
