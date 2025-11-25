from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
import uuid
import shutil
import os
from typing import Optional
from .generator import LocalComfyUIGenerator

app = FastAPI(title="PixelDojo API", version="1.0.0")

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Note: Backend runs on port 8001 (update uvicorn command accordingly)

# Initialize generator (paths relative to backend directory)
import os
backend_dir = Path(__file__).parent.parent
generator = LocalComfyUIGenerator(
    comfyui_path=str(backend_dir / "comfyui"),
    workflow_path=str(backend_dir / "workflows" / "video_generation.json")
)

# Store job status
job_status: dict[str, dict] = {}


@app.get("/")
async def root():
    return {"message": "PixelDojo API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


def generate_video_task(job_id: str, image_path: str, prompt: str, duration: int):
    """Background task for video generation"""
    try:
        video_path = generator.generate(image_path, prompt, duration)
        
        if video_path:
            job_status[job_id] = {
                "status": "completed",
                "progress": 100,
                "message": "Generation complete",
                "video_path": video_path
            }
        else:
            job_status[job_id] = {
                "status": "failed",
                "progress": 0,
                "message": "Generation failed - no video produced",
                "video_path": None
            }
    except Exception as e:
        job_status[job_id] = {
            "status": "failed",
            "progress": 0,
            "message": str(e),
            "video_path": None
        }


@app.post("/generate")
async def generate_video(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    prompt: str = Form(...),
    duration: int = Form(30)
):
    """Generate a video from an uploaded image and prompt"""
    job_id = str(uuid.uuid4())
    
    # Save uploaded image
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    image_path = upload_dir / f"{job_id}_{image.filename}"
    
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Initialize job status
    job_status[job_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Starting generation...",
        "video_path": None
    }
    
    # Start background task
    background_tasks.add_task(generate_video_task, job_id, str(image_path), prompt, duration)
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Generation started"
    }


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Get the status of a generation job"""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_status[job_id]


@app.get("/video/{job_id}")
async def get_video(job_id: str):
    """Download the generated video"""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    video_path = job_status[job_id].get("video_path")
    if not video_path or not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"pixeldojo_{job_id}.mp4"
    )

