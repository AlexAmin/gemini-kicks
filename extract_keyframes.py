import os
import subprocess
import time
import tempfile
from glob import glob
from typing import List

from team_recognition import team_recognition
from utils_video import chunk_list


def extract_keyframes(input_path) -> List[str]:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    timestamp = str(int(time.time()))
    # Create timestamp directory
    timestamp_dir = os.path.join(tempfile.gettempdir(), "llama-hoops", str(timestamp))
    os.makedirs(timestamp_dir, exist_ok=True)

    keyframe_cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", "select=eq(pict_type\\,I)",
        "-vsync", "vfr",
        "-q:v", "1",
        os.path.join(timestamp_dir, f"keyframe-{timestamp}_%03d.jpg")
    ]
    print(" ".join(keyframe_cmd))
    print(timestamp_dir)

    result = subprocess.run(keyframe_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed with error: {result.stderr}")

    keyframe_files = sorted(glob(os.path.join(timestamp_dir, "*.jpg")))
    return keyframe_files




if __name__ == "__main__":
    keyframe_files = extract_keyframes("lakers-short.mp4")

    # Split into chunks of 8
    file_chunks = chunk_list(keyframe_files, 8)

    # Process each chunk
    for chunk in file_chunks:
        print(team_recognition(chunk))


