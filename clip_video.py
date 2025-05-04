import os
import time
import tempfile
import subprocess


def clip_video(start, end, path) -> str:
    timestamp = str(int(time.time()))
    output_dir = os.path.join(tempfile.gettempdir(), "llama-hoops", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"clip_{timestamp}.mp4")

    cmd = [
        "ffmpeg",
        "-i", path,
        "-ss", str(start),
        "-to", str(end),
        "-c", "copy",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return output_path
