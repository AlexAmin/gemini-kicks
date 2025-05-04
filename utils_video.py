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
        '-loglevel', 'error',
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


def clip_segment(input_path, start_time, end_time, audio_path: str, output_path):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    cmd = [
        "ffmpeg",
        "-loglevel", "error",
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", input_path,
        # "-i", audio_path,
        # "-map", "0:v",  # take video from first input
        # "-map", "1:a",  # take audio from second input
        "-c:v", "copy",  # copy video codec
        "-y",  # overwrite output file
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr}")


def overlay_video(input_path, overlay_path, output_path, overlay_scale=1.0):
    ffmpeg_command = [
        "ffmpeg",
        "-loglevel", "error",
        "-i", input_path,
        "-i", overlay_path,
        "-filter_complex",
        "[1:v]scale=iw*"+str(overlay_scale)+":ih*"+str(overlay_scale)+"[scaled];"
        "[0:v][scaled]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2:enable='lte(t,3.5)'",
        "-c:a", "copy",
        output_path
    ]
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg error: {e.stderr}") from e
