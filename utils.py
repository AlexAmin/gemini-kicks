import os
import subprocess
from typing import List
from models.basketball_event import BasketballEvent
from models.transcription_segment import TranscriptionSegment

def load_prompt_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()


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
    return output_path


def clip_segment(input_path, start_time, end_time, output_path):
    cmd = [
        "ffmpeg",
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", input_path,
        "-c", "copy",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr}")


def overlay_video(input_path, overlay_path, output_path, overlay_scale=0.5):
    ffmpeg_command = [
    "ffmpeg",
    "-i", input_path,
    "-i", overlay_path,
    "-filter_complex",
    "[1:v]scale=iw*"+str(overlay_scale)+":ih*"+str(overlay_scale)+"[scaled];[0:v][scaled]overlay=0:0:shortest=1",
    "-c:a", "copy",
    output_path
    ]
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg error: {e.stderr}") from e


def get_timestamp_range(highlights: List[BasketballEvent]) -> tuple[float, float]:
    if not highlights: return [None, None]
    timestamps = [event.timestamp for event in highlights]
    return min(timestamps), max(timestamps)

def get_transcripts_for_highlights(transcripts: List[TranscriptionSegment], highlights: List[BasketballEvent]) -> List[TranscriptionSegment]:
    if len(highlights) == 0: return []
    min_timestamp, max_timestamp = get_timestamp_range(highlights)
    filtered_transcripts = [
        transcript for transcript in transcripts
        if min_timestamp <= transcript.timestamp <= max_timestamp
    ]
    return filtered_transcripts

