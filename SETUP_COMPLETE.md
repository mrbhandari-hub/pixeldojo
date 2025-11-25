# Setup Complete! ✅

All dependencies have been installed and the project is ready to run.

## What Was Installed

### System Dependencies
- ✅ Homebrew (already installed)
- ✅ Python 3.12
- ✅ FFmpeg

### ComfyUI
- ✅ Cloned to `backend/comfyui/`
- ✅ Virtual environment created with Python 3.12
- ✅ PyTorch with MPS (Apple Silicon) support installed
- ✅ All ComfyUI dependencies installed
- ✅ ComfyUI Manager installed

### Backend (PixelDojo API)
- ✅ Virtual environment created at `backend/venv/`
- ✅ All Python dependencies installed (FastAPI, Uvicorn, etc.)
- ✅ Upload and output directories created

### Frontend
- ✅ Next.js project initialized
- ✅ Tailwind CSS configured
- ✅ Lucide React icons installed
- ✅ All npm dependencies installed

## Next Steps

### 1. Start ComfyUI (Terminal 1)
```bash
cd backend/comfyui
source venv/bin/activate
python main.py --listen 127.0.0.1 --port 8188
```

Wait for ComfyUI to fully start (you'll see "Starting server" message).

### 2. Start the Backend API (Terminal 2)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

You should see: `Uvicorn running on http://127.0.0.1:8001`

### 3. Start the Frontend (Terminal 3)
```bash
cd frontend
npm run dev
```

You should see: `Local: http://localhost:3000`

### 4. Open the Application
Open your browser and navigate to: **http://localhost:3000**

## Important Notes

### Workflow Customization Required
The current workflow template (`backend/workflows/video_generation.json`) is a basic placeholder. Before generating videos, you'll need to:

1. **Start ComfyUI** (step 1 above)
2. **Open ComfyUI in browser**: http://127.0.0.1:8188
3. **Build your video generation workflow** with:
   - AnimateDiff nodes for temporal consistency
   - IPAdapter for image conditioning
   - Video models (WAN 2.2, etc.)
   - Output nodes for video generation
4. **Export the workflow**: Click "Save (API Format)" in ComfyUI
5. **Replace the template**: Save the exported JSON to `backend/workflows/video_generation.json`
6. **Update the generator code**: Modify `backend/app/generator.py` to match your workflow's node structure

### First Run Tips
- The first time ComfyUI runs, it may download models (this can take time)
- Start with short videos (5-10 seconds) to test
- Monitor Activity Monitor to ensure sufficient memory
- For 5-minute videos, expect multiple clips to be generated and stitched

## Troubleshooting

### ComfyUI won't start
- Check that Python 3.12 is in your PATH: `which python3.12`
- Verify ComfyUI directory exists: `ls backend/comfyui`

### Backend errors
- Ensure virtual environment is activated: `source backend/venv/bin/activate`
- Check Python version: `python --version` (should be 3.12)

### Frontend won't load
- Check that port 3000 is available
- Verify npm dependencies: `cd frontend && npm install`

### Out of memory errors
- Close other applications
- Reduce video resolution in workflow (512x512 recommended)
- Generate shorter clips first

## Architecture Overview

- **Frontend**: Next.js app on port 3000
- **Backend API**: FastAPI on port 8001
- **ComfyUI**: Running on port 8188
- **Communication**: Frontend → Backend → ComfyUI API

All services must be running simultaneously for the application to work.

