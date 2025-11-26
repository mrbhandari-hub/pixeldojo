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
            response = requests.get(f"{self.base_url}/system_stats", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"DEBUG: is_running check failed: {e}")
            return False
    
    def start(self) -> bool:
        """Start ComfyUI server"""
        print(f"DEBUG: Checking connection to ComfyUI at {self.base_url}")
        if self.is_running():
            print("ComfyUI is running/accessible")
            return True
        
        # If using a remote URL, don't try to start a local process
        if os.getenv("COMFYUI_URL"):
            print(f"ERROR: Could not connect to remote ComfyUI at {self.base_url}")
            print("Please check if the RunPod instance is running and the port is correct.")
            return False
        
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
            print(f"DEBUG: Sending workflow to {self.base_url}/prompt")
            response = requests.post(
                f"{self.base_url}/prompt",
                json=prompt_data,
                timeout=30
            )
            
            # Check for errors in response
            result = response.json()
            
            if "error" in result:
                print(f"ERROR from ComfyUI: {result['error']}")
                if "node_errors" in result:
                    for node_id, errors in result["node_errors"].items():
                        print(f"  Node {node_id}: {errors}")
                return None
            
            if response.status_code != 200:
                print(f"ERROR: ComfyUI returned status {response.status_code}")
                print(f"Response: {result}")
                return None
                
            prompt_id = result.get("prompt_id")
            print(f"DEBUG: Got prompt_id: {prompt_id}")
            return prompt_id
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Network error queueing prompt: {e}")
            return None
        except Exception as e:
            print(f"ERROR: Unexpected error queueing prompt: {e}")
            import traceback
            traceback.print_exc()
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
                files = {'image': (os.path.basename(image_path), f, 'image/png')}
                data = {'overwrite': 'true'}
                print(f"DEBUG: Uploading to {self.base_url}/upload/image")
                response = requests.post(
                    f"{self.base_url}/upload/image",
                    files=files,
                    data=data,
                    timeout=60
                )
                print(f"DEBUG: Upload response status: {response.status_code}")
                response.raise_for_status()
                result = response.json()
                print(f"DEBUG: Upload result: {result}")
                return result.get("name")
        except Exception as e:
            print(f"Error uploading image: {e}")
            import traceback
            traceback.print_exc()
            return None

