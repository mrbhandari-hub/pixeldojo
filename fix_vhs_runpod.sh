#!/bin/bash

# Fix VideoHelperSuite on RunPod
# Run this if VHS nodes aren't loading

echo "🔧 Fixing VideoHelperSuite..."

# Find ComfyUI directory
if [ -d "/workspace/runpod-slim/ComfyUI" ]; then
    COMFY_DIR="/workspace/runpod-slim/ComfyUI"
elif [ -d "/workspace/ComfyUI" ]; then
    COMFY_DIR="/workspace/ComfyUI"
else
    echo "❌ ComfyUI not found!"
    exit 1
fi

echo "Using ComfyUI at: $COMFY_DIR"
cd "$COMFY_DIR/custom_nodes"

# Remove and reinstall VHS
echo "Removing old VideoHelperSuite..."
rm -rf ComfyUI-VideoHelperSuite

echo "Cloning fresh VideoHelperSuite..."
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git

cd ComfyUI-VideoHelperSuite

# Install dependencies explicitly
echo "Installing dependencies..."
pip install imageio imageio-ffmpeg opencv-python-headless pillow numpy

# Install from requirements if exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Run install script
if [ -f "install.py" ]; then
    echo "Running install.py..."
    python3 install.py
fi

# Verify the module structure
echo ""
echo "Checking module structure..."
if [ -f "videohelpersuite/__init__.py" ]; then
    echo "✅ videohelpersuite/__init__.py exists"
else
    echo "⚠️  Missing __init__.py"
fi

if [ -f "videohelpersuite/nodes.py" ]; then
    echo "✅ videohelpersuite/nodes.py exists"
else
    echo "⚠️  Missing nodes.py"
fi

# Test import
echo ""
echo "Testing import..."
cd "$COMFY_DIR"
python3 -c "
import sys
sys.path.insert(0, 'custom_nodes/ComfyUI-VideoHelperSuite')
try:
    from videohelpersuite import nodes
    print('✅ Import successful!')
    print('Available:', dir(nodes)[:5], '...')
except Exception as e:
    print(f'❌ Import failed: {e}')
"

echo ""
echo "Done! Restart ComfyUI:"
echo "  pkill -f main.py"
echo "  cd $COMFY_DIR && python main.py --listen 0.0.0.0 --port 8188"




