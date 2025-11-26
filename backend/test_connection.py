import requests
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("COMFYUI_URL")
print(f"Testing connection to {url}...")
try:
    resp = requests.get(f"{url}/system_stats", timeout=5)
    print(f"Status: {resp.status_code}")
    print(resp.text[:100])
except Exception as e:
    print(f"Error: {e}")
