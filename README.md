# PixelDojo: Local AI Video Generator

A local-first web application that transforms images into AI-generated videos using ComfyUI on macOS (Apple Silicon).

## Architecture

- **Frontend**: Next.js (React) with Tailwind CSS - Modern UI for image uploads and video playback
- **Backend**: Python FastAPI - Orchestrates ComfyUI, handles video stitching with FFmpeg
- **Engine**: Local ComfyUI instance running in API mode

## Setup

### Prerequisites

- macOS (Apple Silicon - M1/M2/M3/M4)
- Homebrew (will be installed automatically if missing)

### Installation

1. Run the setup script:
   ```bash
   ./setup_mac.sh
   ```

   This will:
   - Install Homebrew (if needed)
   - Install Python 3.12 and FFmpeg
   - Clone and set up ComfyUI with Apple Silicon (MPS) support
   - Install ComfyUI Manager and required custom nodes

2. Set up the backend:
   ```bash
   cd backend
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

### Start ComfyUI (in one terminal)

```bash
cd backend/comfyui
source venv/bin/activate
python main.py --listen 127.0.0.1 --port 8188
```

### Start the Backend API (in another terminal)

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

### Start the Frontend (in another terminal)

```bash
cd frontend
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. Upload an image (drag & drop or click to select)
2. Enter a text prompt describing the video you want
3. Adjust the duration slider (5 seconds to 5 minutes)
4. Click "Generate Video"
5. Wait for processing (progress will be shown)
6. Download your generated video when complete

## How It Works

1. **Image Upload**: The frontend sends the image to the backend API
2. **Workflow Injection**: The backend loads a ComfyUI workflow template and injects your image and prompt
3. **Video Generation**: For longer videos (>5s), multiple clips are generated and stitched together using FFmpeg
4. **Progress Tracking**: The frontend polls the backend for status updates
5. **Video Delivery**: Once complete, the video is available for download

## Future: Cloud GPU Support

The architecture is designed to easily switch to cloud GPU services (RunPod, Vast.ai, etc.) by implementing a new `VideoGenerator` class that calls cloud APIs instead of local ComfyUI.

## Notes

- First-time setup may take 30-60 minutes (downloading models, etc.)
- Video generation time depends on your Mac's performance and video length
- For 5-minute videos, expect multiple clips to be generated and stitched
- Monitor Activity Monitor to ensure sufficient memory is available

## Troubleshooting

- **ComfyUI won't start**: Check that Python 3.12 and all dependencies are installed
- **Out of memory**: Close other applications, reduce video resolution in workflow
- **Slow generation**: This is expected on local hardware - consider cloud GPUs for production use

