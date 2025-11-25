import subprocess
import time
import requests
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path


class ComfyUIWrapper:
    """Wrapper for managing ComfyUI instance and API interactions"""
    
    def __init__(self, comfyui_path: str = "comfyui", port: int = 8188):
        self.comfyui_path = Path(comfyui_path)
        self.port = port
        # Allow overriding URL for cloud/remote instances
        self.base_url = os.getenv("COMFYUI_URL", f"http://127.0.0.1:{port}")
        self.process: Optional[subprocess.Popen] = None
        self.client_id = "pixeldojo-client"
    
    def is_running(self) -> bool:
        """Check if ComfyUI is running"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start(self) -> bool:
        """Start ComfyUI server"""
        if self.is_running():
            print("ComfyUI is already running")
            return True
        
        venv_python = self.comfyui_path / "venv" / "bin" / "python"
        if not venv_python.exists():
            venv_python = "python3"
        
        main_py = self.comfyui_path / "main.py"
        if not main_py.exists():
            raise FileNotFoundError(f"ComfyUI not found at {self.comfyui_path}")
        
        print(f"Starting ComfyUI on port {self.port}...")
        comfyui_path_str = str(self.comfyui_path.resolve())
        self.process = subprocess.Popen(
            [str(venv_python), str(main_py), "--listen", "127.0.0.1", "--port", str(self.port)],
            cwd=comfyui_path_str,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to be ready
        max_attempts = 30
        for i in range(max_attempts):
            time.sleep(2)
            if self.is_running():
                print("ComfyUI started successfully")
                return True
        
        print("Failed to start ComfyUI")
        return False
    
    def stop(self):
        """Stop ComfyUI server"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            print("ComfyUI stopped")
    
    def queue_prompt(self, workflow: Dict[str, Any]) -> Optional[str]:
        """Queue a prompt/workflow in ComfyUI and return the prompt_id"""
        if not self.is_running():
            raise RuntimeError("ComfyUI is not running")
        
        prompt_data = {
            "prompt": workflow,
            "client_id": self.client_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/prompt",
                json=prompt_data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get("prompt_id")
        except Exception as e:
            print(f"Error queueing prompt: {e}")
            return None
    
    def get_history(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get the history for a specific prompt_id"""
        if not self.is_running():
            return None
        
        try:
            response = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=5)
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        if not self.is_running():
            return {"queue_running": [], "queue_pending": []}
        
        try:
            response = requests.get(f"{self.base_url}/queue", timeout=5)
            response.raise_for_status()
            return response.json()
        except:
            return {"queue_running": [], "queue_pending": []}
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """Upload an image to ComfyUI and return the filename"""
        if not self.is_running():
            raise RuntimeError("ComfyUI is not running")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                data = {'overwrite': 'true'}
                response = requests.post(
                    f"{self.base_url}/upload/image",
                    files=files,
                    data=data,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                return result.get("name")
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None

