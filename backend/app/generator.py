from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
import json
import requests
import time
import subprocess
import shutil
import tempfile
import os
from .comfy_wrapper import ComfyUIWrapper


class VideoGenerator(ABC):
    """Abstract base class for video generators"""
    
    @abstractmethod
    def generate(self, image_path: str, prompt: str, duration_seconds: int, fast_mode: bool = False) -> Optional[str]:
        """Generate a video from an image and prompt. Returns path to output video."""
        pass


class LocalComfyUIGenerator(VideoGenerator):
    """Local ComfyUI-based video generator"""
    
    def __init__(self, comfyui_path: str = "comfyui", workflow_path: str = "workflows/video_generation.json"):
        self.comfy = ComfyUIWrapper(comfyui_path)
        # Handle both relative and absolute paths
        if Path(workflow_path).is_absolute():
            self.workflow_path = Path(workflow_path)
        else:
            # Assume workflow is relative to backend directory
            self.workflow_path = Path(__file__).parent.parent / workflow_path
        # Output directory relative to backend
        self.output_dir = Path(__file__).parent.parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)
    
    def _load_workflow(self) -> Dict[str, Any]:
        """Load the workflow template"""
        if not self.workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {self.workflow_path}")
        
        with open(self.workflow_path, 'r') as f:
            return json.load(f)
    
    def _inject_image_and_prompt(self, workflow: Dict[str, Any], image_filename: str, prompt: str, duration_seconds: int = 5, fast_mode: bool = False) -> Dict[str, Any]:
        """Inject image, prompt, and duration into workflow. If fast_mode, also apply speed optimizations."""
        
        # Calculate frame count for duration
        # Wan model uses 16fps, and length must be (multiple of 4) + 1
        fps = 16
        raw_frames = duration_seconds * fps
        # Round to nearest valid value: (multiple of 4) + 1
        frame_count = ((raw_frames // 4) * 4) + 1
        # Clamp between reasonable limits
        frame_count = max(17, min(frame_count, 481))  # 17 frames (~1s) to 481 frames (~30s)
        
        print(f"DEBUG: Duration {duration_seconds}s -> {frame_count} frames at {fps}fps")
        
        for node_id, node_data in workflow.items():
            if isinstance(node_data, dict):
                # Look for image input nodes (typically LoadImage)
                if node_data.get("class_type") == "LoadImage":
                    node_data["inputs"]["image"] = image_filename
                
                # Look for text prompt nodes (typically CLIPTextEncode with "Positive" in title)
                if node_data.get("class_type") == "CLIPTextEncode":
                    if node_data.get("_meta", {}).get("title") == "Positive Prompt":
                        node_data["inputs"]["text"] = prompt
                
                # Set frame count in WanImageToVideo node
                if node_data.get("class_type") == "WanImageToVideo":
                    node_data["inputs"]["length"] = frame_count
                    print(f"DEBUG: Set WanImageToVideo length to {frame_count}")
                    
                    # Fast mode: also lower resolution
                    if fast_mode:
                        node_data["inputs"]["width"] = 640
                        node_data["inputs"]["height"] = 384
                        print(f"DEBUG: Fast mode - reduced resolution to 640x384")
                
                # Fast mode optimizations
                if fast_mode:
                    # Reduce steps from 30 to 15 (aggressive)
                    if node_data.get("class_type") == "KSampler":
                        original_steps = node_data["inputs"].get("steps", 30)
                        node_data["inputs"]["steps"] = 15
                        # Lower CFG for faster convergence
                        node_data["inputs"]["cfg"] = 3.5
                        print(f"DEBUG: Fast mode - reduced steps from {original_steps} to 15, CFG to 3.5")
                    
                    # Use FP8 quantization for faster inference
                    if node_data.get("class_type") == "UNETLoader":
                        original_dtype = node_data["inputs"].get("weight_dtype", "default")
                        node_data["inputs"]["weight_dtype"] = "fp8_e4m3fn"
                        print(f"DEBUG: Fast mode - changed weight_dtype from {original_dtype} to fp8_e4m3fn")
        
        return workflow
    
    def generate(self, image_path: str, prompt: str, duration_seconds: int, fast_mode: bool = False) -> Optional[str]:
        """Generate video using local ComfyUI"""
        print(f"DEBUG: Starting generation with image={image_path}, prompt={prompt}, fast_mode={fast_mode}")
        
        # Ensure ComfyUI is running
        if not self.comfy.is_running():
            print("DEBUG: ComfyUI not running, attempting to start...")
            if not self.comfy.start():
                print("ERROR: Failed to start/connect to ComfyUI")
                raise RuntimeError("Could not connect to ComfyUI. Check if it's running.")
        
        print(f"DEBUG: ComfyUI is running at {self.comfy.base_url}")
        
        # Upload image
        print(f"DEBUG: Uploading image {image_path}...")
        image_filename = self.comfy.upload_image(image_path)
        if not image_filename:
            print("ERROR: Failed to upload image")
            raise RuntimeError("Failed to upload image to ComfyUI")
        print(f"DEBUG: Image uploaded as {image_filename}")
        
        # Load and prepare workflow
        print(f"DEBUG: Loading workflow from {self.workflow_path}")
        workflow = self._load_workflow()
        workflow = self._inject_image_and_prompt(workflow, image_filename, prompt, duration_seconds=duration_seconds, fast_mode=fast_mode)
        
        # Queue prompt
        print("DEBUG: Queuing video generation...")
        prompt_id = self.comfy.queue_prompt(workflow)
        
        if not prompt_id:
            print("ERROR: Failed to queue prompt")
            raise RuntimeError("Failed to queue workflow in ComfyUI. Check ComfyUI logs for errors.")
        
        print(f"DEBUG: Prompt queued with ID: {prompt_id}")
        
        # Wait for completion
        return self._wait_for_completion(prompt_id)
    
    def _wait_for_completion(self, prompt_id: str, timeout: int = 1200) -> Optional[str]:
        """Wait for a prompt to complete and return the output path"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check history
            history = self.comfy.get_history(prompt_id)
            if history and prompt_id in history:
                print(f"DEBUG: Found history for {prompt_id}")
                outputs = history[prompt_id].get("outputs", {})
                
                # First check for VHS video outputs (gifs key contains videos too)
                for node_id, node_output in outputs.items():
                    if "gifs" in node_output:
                        for video in node_output["gifs"]:
                            filename = video["filename"]
                            subfolder = video.get("subfolder", "")
                            type_ = video.get("type", "output")
                            
                            print(f"DEBUG: Found VHS video output: {filename}")
                            
                            # Download the video file
                            video_url = f"{self.comfy.base_url}/view?filename={filename}&subfolder={subfolder}&type={type_}"
                            
                            try:
                                response = requests.get(video_url)
                                if response.status_code == 200:
                                    output_filename = f"video_{int(time.time())}.mp4"
                                    output_path = self.output_dir / output_filename
                                    self.output_dir.mkdir(parents=True, exist_ok=True)
                                    
                                    with open(output_path, "wb") as f:
                                        f.write(response.content)
                                    
                                    print(f"DEBUG: Video saved to {output_path}")
                                    return str(output_path)
                                else:
                                    print(f"ERROR: Failed to download video: {response.status_code}")
                            except Exception as e:
                                print(f"ERROR: Exception downloading video: {e}")
                
                # Fallback: Check for image outputs and stitch them
                image_files = []
                for node_id, node_output in outputs.items():
                    if "images" in node_output:
                        for image in node_output["images"]:
                            image_files.append(image)
                
                if not image_files:
                    print("DEBUG: No video or image outputs found")
                    return None
                
                print(f"DEBUG: Found {len(image_files)} frames. Downloading and stitching...")
                
                # Create temp directory for frames
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    frame_paths = []
                    
                    # Download all frames
                    for i, img in enumerate(image_files):
                        filename = img["filename"]
                        subfolder = img["subfolder"]
                        type_ = img["type"]
                        
                        img_url = f"{self.comfy.base_url}/view?filename={filename}&subfolder={subfolder}&type={type_}"
                        
                        try:
                            response = requests.get(img_url)
                            if response.status_code == 200:
                                # Save with sequential naming for ffmpeg
                                frame_name = f"frame_{i:05d}.png"
                                frame_path = temp_path / frame_name
                                with open(frame_path, "wb") as f:
                                    f.write(response.content)
                                frame_paths.append(frame_path)
                            else:
                                print(f"Error downloading frame {filename}: {response.status_code}")
                        except Exception as e:
                            print(f"Exception downloading frame {filename}: {e}")
                    
                    if not frame_paths:
                        print("ERROR: Failed to download any frames")
                        return None
                        
                    # Stitch with ffmpeg
                    output_filename = f"video_{int(time.time())}.mp4"
                    output_path = self.output_dir / output_filename
                    self.output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # ffmpeg command: 16 fps, glob pattern for inputs
                    ffmpeg_cmd = [
                        "ffmpeg",
                        "-y",
                        "-framerate", "16",
                        "-i", str(temp_path / "frame_%05d.png"),
                        "-c:v", "libx264",
                        "-pix_fmt", "yuv420p",
                        str(output_path)
                    ]
                    
                    print(f"DEBUG: Running ffmpeg: {' '.join(ffmpeg_cmd)}")
                    try:
                        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
                        print(f"DEBUG: Video saved to {output_path}")
                        return str(output_path)
                    except subprocess.CalledProcessError as e:
                        print(f"ERROR: ffmpeg failed: {e.stderr.decode()}")
                        return None
            
            time.sleep(2)
        
        return None
