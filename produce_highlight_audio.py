import os
import subprocess
import time

from util_io import get_temp_path


def produce_highlight_audio(intro_audio_path: str, summary_audio_path: str, highlight_title: str,
                            highlight_start: float, highlight_end: float) -> str:
    # Generate TTS for summary
    # ffmpeg command to combine background radio with intro and summary audio
    timestamp = str(int(time.time()))
    output_path = os.path.join(get_temp_path("highlights-audio"),
                               f"audio_highlight-{highlight_title}-{highlight_start}-{highlight_end}.mp3")

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