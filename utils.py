import os
import subprocess

def get_video_duration_in_seconds(path):
    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        path
    ]
    result = subprocess.run(
        command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True
    )
    duration_str = result.stdout.strip()
    try:
        return float(duration_str)
    except ValueError:
        raise RuntimeError(f"Could not parse duration: {duration_str}")
    

def create_16khz_mono_wav_from_video(path, start_time, end_time, working_dir):
    output_path = os.path.join(working_dir, 'chunk.wav')
    command = [
        'ffmpeg',
        '-ss', str(start_time),
        '-to', str(end_time),
        '-i', path,
        '-vn',
        '-ac', '1',
        '-ar', '16000',
        '-y', output_path
    ]
    result = subprocess.run(
        command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")
    if not os.path.isfile(output_path):
        raise FileNotFoundError(f"Output file was not created: {output_path}")
    print(f"Audio segment created: {output_path}")
