#!/bin/bash

# PixelDojo Startup Script
# This script helps you start all services

echo "🎬 PixelDojo Startup"
echo ""
echo "This script will help you start the application."
echo "Make sure you've run ./setup_mac.sh first!"
echo ""

# Check if ComfyUI is set up
if [ ! -d "backend/comfyui" ]; then
    echo "❌ ComfyUI not found. Please run ./setup_mac.sh first."
    exit 1
fi

echo "Starting services..."
echo ""
echo "1. Start ComfyUI in one terminal:"
echo "   cd backend/comfyui"
echo "   source venv/bin/activate"
echo "   python main.py --listen 127.0.0.1 --port 8188"
echo ""
echo "2. Start the backend API in another terminal:"
echo "   cd backend"
echo "   source venv/bin/activate  # or: python3.12 -m venv venv && source venv/bin/activate"
echo "   pip install -r requirements.txt  # if not already installed"
echo "   uvicorn app.main:app --reload --port 8001"
echo ""
echo "3. Start the frontend in another terminal:"
echo "   cd frontend"
echo "   npm install  # if not already installed"
echo "   npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
echo "Note: You need to run these in separate terminal windows/tabs."

