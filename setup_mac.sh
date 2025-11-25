#!/bin/bash

# PixelDojo Setup Script for macOS (Apple Silicon)
# This script installs all dependencies and sets up ComfyUI

set -e

echo "🎬 PixelDojo Setup - Starting..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew already installed"
fi

# Install Python 3.12
echo "🐍 Installing Python 3.12..."
brew install python@3.12

# Install FFmpeg
echo "🎥 Installing FFmpeg..."
brew install ffmpeg

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Clone ComfyUI if it doesn't exist
if [ ! -d "comfyui" ]; then
    echo "📥 Cloning ComfyUI..."
    git clone https://github.com/comfyanonymous/ComfyUI.git comfyui
else
    echo "✅ ComfyUI already cloned"
fi

# Install ComfyUI dependencies with MPS support
echo "📦 Installing ComfyUI dependencies (with Apple Silicon MPS support)..."
cd comfyui

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3.12 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install PyTorch with MPS support
echo "🔥 Installing PyTorch with MPS support..."
pip install torch torchvision torchaudio

# Install ComfyUI requirements
echo "📦 Installing ComfyUI requirements..."
pip install -r requirements.txt

# Install ComfyUI Manager
echo "📦 Installing ComfyUI Manager..."
cd custom_nodes
if [ ! -d "ComfyUI-Manager" ]; then
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
fi
cd ..

echo "✅ Setup complete!"
echo ""
echo "To start ComfyUI, run:"
echo "  cd backend/comfyui"
echo "  source venv/bin/activate"
echo "  python main.py --listen 127.0.0.1 --port 8188"
echo ""
echo "To start the PixelDojo backend, run:"
echo "  cd backend"
echo "  python -m venv venv"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  uvicorn app.main:app --reload --port 8001"

