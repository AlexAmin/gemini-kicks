import os
import subprocess
import time
import tempfile
from glob import glob

from team_recognition import team_recognition


def extract_keyframes(input_path):
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

    return timestamp_dir


def chunk_list(lst, n):
    """Split a list into chunks of size n"""
    return [lst[i:i + n] for i in range(0, len(lst), n)]


if __name__ == "__main__":
    output_dir = extract_keyframes("lakers-short.mp4")

    # Find all keyframe files
    keyframe_files = sorted(glob(os.path.join(output_dir, "*.jpg")))

    # Split into chunks of 8
    file_chunks = chunk_list(keyframe_files, 8)

    # Process each chunk
    for chunk in file_chunks:
        print(team_recognition(chunk))

    print(output_dir)
