import os
import subprocess
import time
from glob import glob
from typing import List

from gemini.prompting.team_recognition import team_recognition
from utils_av import chunk_list
from util_io import get_temp_path

def extract_keyframes(input_path) -> List[str]:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    timestamp = str(int(time.time()))
    timestamp_dir = get_temp_path("keyframes")
    keyframe_cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vf", "select=eq(pict_type\\,I)",
        "-vsync", "vfr",
        "-q:v", "1",
        os.path.join(timestamp_dir, f"keyframe{timestamp}_%03d.jpg")
    ]
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
        print(f"recognized team: {team_recognition(chunk)}")


