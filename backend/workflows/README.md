# ComfyUI Workflows

This directory contains ComfyUI workflow templates (JSON files) that define how videos are generated.

## Current Workflow

`video_generation.json` - A basic workflow template for image-to-video generation.

## Customizing Workflows

The current workflow is a simplified template. You'll need to:

1. **Export your workflow from ComfyUI**:
   - Open ComfyUI in your browser
   - Build your desired workflow (with AnimateDiff, IPAdapter, etc.)
   - Click "Save (API Format)" to export as JSON
   - Save it here as `video_generation.json`

2. **Update the generator code**:
   - The `_inject_image_and_prompt` method in `generator.py` needs to match your workflow's node structure
   - Adjust node IDs and input names based on your actual workflow

3. **Recommended workflow components for video**:
   - **AnimateDiff** nodes for temporal consistency
   - **IPAdapter** for image conditioning
   - **WAN 2.2** or similar video models
   - **VAE Decode** to convert latents to images
   - **Video Combine** or similar to create video output

## MPS Optimization

For Apple Silicon, ensure your workflow uses:
- Models compatible with MPS (GGUF formats work well)
- Lower batch sizes (1-2)
- Resolution 512x512 or lower for faster generation

