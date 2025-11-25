from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
import json
import time
from .comfy_wrapper import ComfyUIWrapper


class VideoGenerator(ABC):
    """Abstract base class for video generators"""
    
    @abstractmethod
    def generate(self, image_path: str, prompt: str, duration_seconds: int) -> Optional[str]:
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
    
    def _inject_image_and_prompt(self, workflow: Dict[str, Any], image_filename: str, prompt: str) -> Dict[str, Any]:
        """Inject image and prompt into workflow"""
        # This is a simplified version - actual workflow structure depends on your ComfyUI workflow
        # You'll need to adjust node IDs based on your actual workflow
        for node_id, node_data in workflow.items():
            if isinstance(node_data, dict):
                # Look for image input nodes (typically LoadImage)
                if node_data.get("class_type") == "LoadImage":
                    node_data["inputs"]["image"] = image_filename
                # Look for text prompt nodes (typically CLIPTextEncode)
                if "text" in node_data.get("inputs", {}):
                    node_data["inputs"]["text"] = prompt
        
        return workflow
    
    def generate(self, image_path: str, prompt: str, duration_seconds: int) -> Optional[str]:
        """Generate video using local ComfyUI"""
        # Ensure ComfyUI is running
        if not self.comfy.is_running():
            if not self.comfy.start():
                return None
        
        # Upload image
        image_filename = self.comfy.upload_image(image_path)
        if not image_filename:
            return None
        
        # Load and prepare workflow
        workflow = self._load_workflow()
        workflow = self._inject_image_and_prompt(workflow, image_filename, prompt)
        
        # Queue prompt
        print("Queuing video generation...")
        prompt_id = self.comfy.queue_prompt(workflow)
        
        if not prompt_id:
            return None
        
        # Wait for completion
        return self._wait_for_completion(prompt_id)
    
    def _wait_for_completion(self, prompt_id: str, timeout: int = 1200) -> Optional[str]:
        """Wait for a prompt to complete and return the output path"""
        start_time = time.time()
        # Track the latest file in the output directory
        output_dir = self.comfy.comfyui_path / "output"
        initial_files = set(output_dir.glob("*.mp4")) if output_dir.exists() else set()
        
        while time.time() - start_time < timeout:
            # Check for new files
            if output_dir.exists():
                current_files = set(output_dir.glob("*.mp4"))
                new_files = current_files - initial_files
                
                if new_files:
                    # Found a new file!
                    # Wait a moment to ensure it's fully written (VHS usually writes to temp then moves)
                    # But we can also check history to be sure
                    history = self.comfy.get_history(prompt_id)
                    if history and prompt_id in history:
                        # Job is done
                        # Return the most recent new file
                        latest = sorted(list(new_files), key=lambda p: p.stat().st_mtime)[-1]
                        return str(latest)
            
            # Check if job failed or finished without file (via history)
            history = self.comfy.get_history(prompt_id)
            if history and prompt_id in history:
                # Job finished, if we didn't find a file yet, check one last time
                if output_dir.exists():
                    current_files = set(output_dir.glob("*.mp4"))
                    new_files = current_files - initial_files
                    if new_files:
                        latest = sorted(list(new_files), key=lambda p: p.stat().st_mtime)[-1]
                        return str(latest)
                return None
            
            time.sleep(2)
        
        return None

