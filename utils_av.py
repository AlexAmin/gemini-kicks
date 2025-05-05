import os
import time
import subprocess
from util_io import get_temp_path


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


def clip_segment(input_path, start_time, end_time, intro_audio_path: str, output_path, intro_duration):
    if not os.path.exists(intro_audio_path):
        raise FileNotFoundError(f"Audio file not found: {intro_audio_path}")

    cmd = [
        "ffmpeg",
        "-loglevel", "error",
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", input_path,
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr}")


def overlay_video(input_path, intro_audio_path, overlay_path, output_path, intro_duration=1.0):
    ffmpeg_command = [
        "ffmpeg",
        "-hwaccel", "videotoolbox",
        "-i", input_path,
        "-hwaccel", "videotoolbox",
        "-i", overlay_path,
        "-i", intro_audio_path,
        "-filter_complex",
        f"[0:v][1:v]overlay=(W-w)/2:(H-h)/2:enable='lte(t,{intro_duration})'[v_interim];[v_interim]scale=trunc(iw/2)*2:trunc(ih/2)*2[v_out];[0:a]asplit=2[a0_vol][a0_norm];[a0_vol]atrim=end={intro_duration},asetpts=PTS-STARTPTS,volume=0.15[a0_vol_trim];[a0_norm]atrim=start={intro_duration},asetpts=PTS-STARTPTS[a0_norm_trim];[2:a]atrim=end={intro_duration},asetpts=PTS-STARTPTS[a2_trim];[a0_vol_trim][a2_trim]amix=inputs=2:duration=longest[a_mixed_initial];[a_mixed_initial][a0_norm_trim]concat=v=0:a=1[a_out]",
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "h264_videotoolbox",
        output_path

    ]
    print(" ".join(ffmpeg_command))
    try:
        subprocess.run(ffmpeg_command, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg error: {e.stderr}") from e


def produce_audio_summary(intro_audio_path: str, summary_audio_path: str) -> str:
    # Generate TTS for summary
    # ffmpeg command to combine background radio with intro and summary audio
    timestamp = str(int(time.time()))
    output_path = os.path.join(get_temp_path("highlights-audio"), f"audio-highlight-{timestamp}.mp3")
    cmd = [
        "ffmpeg",
        "-i", intro_audio_path,
        "-i", summary_audio_path,
        "-filter_complex",
        "[0:a][1:a]concat=n=2:v=0:a=1[out]",
        "-map",
        "[out]",
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def chunk_list(lst, n):
    """Split a list into chunks of size n"""
    return [lst[i:i + n] for i in range(0, len(lst), n)]
