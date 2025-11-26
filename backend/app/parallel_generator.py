"""
Parallel Video Generation System

Strategy: Generate video in 5-second chunks across multiple ComfyUI instances,
then stitch them together for longer videos.
"""

import os
import asyncio
import aiohttp
import tempfile
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import json
import time


@dataclass
class ComfyWorker:
    """Represents a ComfyUI worker instance"""
    url: str
    name: str
    busy: bool = False


class ParallelVideoGenerator:
    """
    Generates long videos by splitting work across multiple ComfyUI instances.
    
    For a 30-second video:
    - With 1 worker: 25-30 minutes
    - With 6 workers: ~5 minutes (6x speedup)
    """
    
    def __init__(self, workers: List[str] = None, workflow_path: str = None):
        """
        Initialize with list of ComfyUI worker URLs.
        
        Args:
            workers: List of ComfyUI URLs, e.g., ["http://worker1:8188", "http://worker2:8188"]
            workflow_path: Path to the video generation workflow JSON
        """
        self.workers = [ComfyWorker(url=url, name=f"worker_{i}") for i, url in enumerate(workers or [])]
        self.workflow_path = Path(workflow_path) if workflow_path else None
        self.output_dir = Path(__file__).parent.parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        self.fps = 16
        self.chunk_duration = 5  # seconds per chunk
        
    def add_worker(self, url: str):
        """Add a ComfyUI worker"""
        self.workers.append(ComfyWorker(url=url, name=f"worker_{len(self.workers)}"))
        
    def calculate_chunks(self, total_duration: int) -> List[Dict]:
        """
        Split duration into chunks for parallel processing.
        
        Returns list of chunk configs with start_frame, end_frame, etc.
        """
        chunks = []
        chunk_frames = self.chunk_duration * self.fps + 1  # 81 frames for 5 sec
        total_frames = total_duration * self.fps + 1
        
        current_frame = 0
        chunk_id = 0
        
        while current_frame < total_frames:
            end_frame = min(current_frame + chunk_frames, total_frames)
            chunks.append({
                "chunk_id": chunk_id,
                "start_frame": current_frame,
                "end_frame": end_frame,
                "frame_count": end_frame - current_frame,
                "is_first": chunk_id == 0,
                "is_last": end_frame >= total_frames
            })
            # Overlap by 1 frame for smooth transitions
            current_frame = end_frame - 1
            chunk_id += 1
            
        return chunks
    
    async def upload_image(self, session: aiohttp.ClientSession, worker: ComfyWorker, image_path: str) -> Optional[str]:
        """Upload image to a worker"""
        try:
            with open(image_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('image', f, filename=os.path.basename(image_path))
                data.add_field('overwrite', 'true')
                
                async with session.post(f"{worker.url}/upload/image", data=data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get("name")
        except Exception as e:
            print(f"Error uploading to {worker.name}: {e}")
        return None
    
    async def queue_prompt(self, session: aiohttp.ClientSession, worker: ComfyWorker, 
                          workflow: Dict, chunk_info: Dict) -> Optional[str]:
        """Queue a generation prompt on a worker"""
        try:
            # Modify workflow for this chunk
            workflow_copy = json.loads(json.dumps(workflow))  # Deep copy
            
            # Set frame count for this chunk
            for node_id, node_data in workflow_copy.items():
                if isinstance(node_data, dict):
                    if node_data.get("class_type") == "WanImageToVideo":
                        node_data["inputs"]["length"] = chunk_info["frame_count"]
            
            prompt_data = {
                "prompt": workflow_copy,
                "client_id": f"parallel-{chunk_info['chunk_id']}"
            }
            
            async with session.post(f"{worker.url}/prompt", json=prompt_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("prompt_id")
        except Exception as e:
            print(f"Error queueing on {worker.name}: {e}")
        return None
    
    async def wait_for_completion(self, session: aiohttp.ClientSession, worker: ComfyWorker,
                                  prompt_id: str, timeout: int = 600) -> Optional[Dict]:
        """Wait for a prompt to complete and return output info"""
        start = time.time()
        while time.time() - start < timeout:
            try:
                async with session.get(f"{worker.url}/history/{prompt_id}") as resp:
                    if resp.status == 200:
                        history = await resp.json()
                        if prompt_id in history:
                            return history[prompt_id].get("outputs", {})
            except:
                pass
            await asyncio.sleep(2)
        return None
    
    async def download_video(self, session: aiohttp.ClientSession, worker: ComfyWorker,
                            output_info: Dict, save_path: Path) -> bool:
        """Download generated video from worker"""
        for node_id, node_output in output_info.items():
            if "gifs" in node_output:
                for video in node_output["gifs"]:
                    filename = video["filename"]
                    subfolder = video.get("subfolder", "")
                    type_ = video.get("type", "output")
                    
                    url = f"{worker.url}/view?filename={filename}&subfolder={subfolder}&type={type_}"
                    
                    try:
                        async with session.get(url) as resp:
                            if resp.status == 200:
                                with open(save_path, 'wb') as f:
                                    f.write(await resp.read())
                                return True
                    except Exception as e:
                        print(f"Error downloading from {worker.name}: {e}")
        return False
    
    async def generate_chunk(self, session: aiohttp.ClientSession, worker: ComfyWorker,
                            workflow: Dict, chunk_info: Dict, image_filename: str,
                            temp_dir: Path) -> Optional[Path]:
        """Generate a single chunk on a worker"""
        print(f"[{worker.name}] Starting chunk {chunk_info['chunk_id']} ({chunk_info['frame_count']} frames)")
        
        # Queue the prompt
        prompt_id = await self.queue_prompt(session, worker, workflow, chunk_info)
        if not prompt_id:
            print(f"[{worker.name}] Failed to queue chunk {chunk_info['chunk_id']}")
            return None
        
        print(f"[{worker.name}] Queued chunk {chunk_info['chunk_id']}, prompt_id: {prompt_id}")
        
        # Wait for completion
        outputs = await self.wait_for_completion(session, worker, prompt_id)
        if not outputs:
            print(f"[{worker.name}] Timeout waiting for chunk {chunk_info['chunk_id']}")
            return None
        
        # Download result
        output_path = temp_dir / f"chunk_{chunk_info['chunk_id']:03d}.mp4"
        if await self.download_video(session, worker, outputs, output_path):
            print(f"[{worker.name}] Completed chunk {chunk_info['chunk_id']}")
            return output_path
        
        return None
    
    def stitch_videos(self, chunk_paths: List[Path], output_path: Path) -> bool:
        """Stitch video chunks together using ffmpeg"""
        if not chunk_paths:
            return False
        
        # Create concat file
        concat_file = output_path.parent / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for path in sorted(chunk_paths):
                f.write(f"file '{path}'\n")
        
        # Use ffmpeg to concatenate
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            concat_file.unlink()  # Clean up
            return True
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            return False
    
    async def generate_parallel(self, image_path: str, prompt: str, 
                               duration_seconds: int) -> Optional[str]:
        """
        Generate a long video using parallel workers.
        
        Args:
            image_path: Path to the source image
            prompt: Text prompt for generation
            duration_seconds: Total video duration
            
        Returns:
            Path to the final stitched video, or None on failure
        """
        if not self.workers:
            raise ValueError("No workers configured")
        
        if not self.workflow_path or not self.workflow_path.exists():
            raise FileNotFoundError("Workflow not found")
        
        # Load workflow
        with open(self.workflow_path) as f:
            base_workflow = json.load(f)
        
        # Calculate chunks
        chunks = self.calculate_chunks(duration_seconds)
        print(f"Splitting {duration_seconds}s video into {len(chunks)} chunks")
        
        async with aiohttp.ClientSession() as session:
            # Upload image to all workers
            print("Uploading image to workers...")
            image_filename = None
            for worker in self.workers:
                filename = await self.upload_image(session, worker, image_path)
                if filename:
                    image_filename = filename
                    # Update workflow with image filename
                    for node_id, node_data in base_workflow.items():
                        if isinstance(node_data, dict):
                            if node_data.get("class_type") == "LoadImage":
                                node_data["inputs"]["image"] = filename
                            if node_data.get("class_type") == "CLIPTextEncode":
                                if node_data.get("_meta", {}).get("title") == "Positive Prompt":
                                    node_data["inputs"]["text"] = prompt
            
            if not image_filename:
                print("Failed to upload image to any worker")
                return None
            
            # Create temp directory for chunks
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Generate chunks in parallel
                tasks = []
                for i, chunk in enumerate(chunks):
                    worker = self.workers[i % len(self.workers)]
                    task = self.generate_chunk(session, worker, base_workflow, chunk, 
                                              image_filename, temp_path)
                    tasks.append(task)
                
                # Wait for all chunks
                chunk_paths = await asyncio.gather(*tasks)
                chunk_paths = [p for p in chunk_paths if p is not None]
                
                if len(chunk_paths) != len(chunks):
                    print(f"Warning: Only {len(chunk_paths)}/{len(chunks)} chunks completed")
                
                if not chunk_paths:
                    return None
                
                # Stitch together
                output_filename = f"video_{int(time.time())}.mp4"
                output_path = self.output_dir / output_filename
                
                if self.stitch_videos(chunk_paths, output_path):
                    print(f"Final video saved to {output_path}")
                    return str(output_path)
        
        return None


# Quick setup for single vs parallel mode
def create_generator(workers: List[str] = None, workflow_path: str = None):
    """
    Factory function to create appropriate generator.
    
    For single worker (current setup), use the existing LocalComfyUIGenerator.
    For multiple workers, use ParallelVideoGenerator.
    """
    if workers and len(workers) > 1:
        return ParallelVideoGenerator(workers=workers, workflow_path=workflow_path)
    else:
        from .generator import LocalComfyUIGenerator
        return LocalComfyUIGenerator(workflow_path=workflow_path)



