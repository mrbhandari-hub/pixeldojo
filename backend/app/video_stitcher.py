import subprocess
from pathlib import Path
from typing import List, Optional


def stitch_videos(video_paths: List[str], output_path: Path) -> Optional[Path]:
    """Stitch multiple video clips together using FFmpeg"""
    if not video_paths:
        return None
    
    if len(video_paths) == 1:
        # Just copy the single video
        output_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cp", video_paths[0], str(output_path)], check=True)
        return output_path
    
    # Create a file list for FFmpeg concat
    concat_file = output_path.parent / "concat_list.txt"
    with open(concat_file, 'w') as f:
        for video_path in video_paths:
            # Use absolute path and escape single quotes
            abs_path = Path(video_path).resolve()
            f.write(f"file '{abs_path}'\n")
    
    # Use FFmpeg to concatenate
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",
                "-y",  # Overwrite output file
                str(output_path)
            ],
            check=True,
            capture_output=True
        )
        
        # Clean up concat file
        concat_file.unlink()
        
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return None

