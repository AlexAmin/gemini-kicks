import os
import time
import tempfile
import subprocess

from util_io import get_temp_path


def clip_video(start, end, path) -> str:
    timestamp = str(int(time.time()))
    output_path = os.path.join(get_temp_path("clips"), f"clip_{timestamp}.mp4")

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
