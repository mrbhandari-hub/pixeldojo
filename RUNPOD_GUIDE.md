# ☁️ PixelDojo Cloud Setup Guide (RunPod)

This guide will help you set up a powerful, cost-effective cloud backend for PixelDojo using RunPod.

## Why RunPod?
*   **Cost:** Pay only for what you use (~$0.44/hr for RTX 3090).
*   **Power:** Access to high-end GPUs (24GB+ VRAM) needed for Wan 2.1.
*   **Ease:** Pre-configured templates for ComfyUI.

---

## Step 1: Create a RunPod Account
1.  Go to [RunPod.io](https://www.runpod.io/).
2.  Sign up and add at least $10 credits (enough for ~20 hours of usage).

## Step 2: Deploy a GPU Pod
1.  Go to **Pods** > **Deploy**.
2.  Select **Community Cloud** (cheaper) or **Secure Cloud**.
3.  Choose a GPU:
    *   **Recommended:** **RTX 3090** or **RTX 4090** (24GB VRAM).
    *   *Note: Wan 2.1 requires significant VRAM. Do not use anything less than 24GB.*
4.  Select a Template:
    *   Search for "ComfyUI".
    *   Select **RunPod ComfyUI** (usually by `runpod` or `theally`).
5.  **Important:** Click "Customize Deployment" (or "Edit Template Args").
    *   **Expose TCP Ports:** Add `8188`.
    *   **Expose HTTP Ports:** **Remove** `8188` from this list if it's there (it cannot be in both).
    *   Set **Volume Size** to at least **60GB** (Models are huge!).
6.  Click **Deploy**.

## Step 3: Run the Setup Script
1.  Once the Pod is "Running", click the **Connect** button.
2.  Select **Start Web Terminal** (or connect via SSH if you prefer).
3.  In the terminal, run these commands to download the setup script and run it:

```bash
cd /workspace
# Clone your repository
git clone https://github.com/mrbhandari-hub/pixeldojo.git
cd pixeldojo

# Make the script executable and run it
chmod +x runpod_setup.sh
./runpod_setup.sh
```

4.  Wait for the downloads to finish (this will take 10-20 minutes depending on speed).

## Step 4: Connect PixelDojo
1.  Once setup is done, start ComfyUI in the RunPod terminal:
    ```bash
    cd /workspace/ComfyUI
    python3 main.py --listen 0.0.0.0 --port 8188
    ```
    > **Note:** If you see `OSError: [Errno 98] address already in use`, it means ComfyUI is already running in the background. Run `pkill -f main.py` to stop it, then try again.

2.  Go back to your RunPod dashboard.
3.  Click **Connect** > **TCP Port Mappings**.
4.  Find the public IP and port mapping for 8188 (e.g., `123.45.67.89:12345`).
5.  Update your local `backend/app/comfy_wrapper.py` or `.env` file to point to this URL instead of `127.0.0.1:8188`.

## Step 5: Save Money! 💸
**CRITICAL:** When you are done generating videos for the day:
1.  Go to your RunPod dashboard.
2.  **Stop** the Pod.
    *   *Stopping* preserves your disk (models stay saved), but you pay a small storage fee (~$0.10/day).
    *   *Terminating* deletes everything (you lose models).
3.  Start it again next time you need it!
