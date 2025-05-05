import os
from typing import List

from models.soccer_event import SoccerEvent
from util_io import get_temp_path
from utils_av import clip_segment, overlay_video


def produce_highlight_video(
        input_path: str,
        highlights: List[SoccerEvent],
        intro_audio_path: str,
        intro_duration: float,
        highlight_title: str,
        highlight_start: float,
        highlight_end: float
):
    # return if no highlights are found
    if len(highlights) == 0: return
    # encode video & extract the highlights from the clips using ffmpeg
    event_names = [highlight.type for highlight in highlights]
    event_names = '-'.join(event_names[:3])
    file_name = f"clip_{highlight_start}-{highlight_end}-{event_names}-{highlight_title}.mp4"
    clip_output_dir = get_temp_path("clips")
    highlight_output_dir = get_temp_path("highlights-video")
    raw_video_highlight_path = os.path.join(highlight_output_dir, file_name)
    clip_segment(input_path, highlight_start, highlight_end, intro_audio_path, raw_video_highlight_path, intro_duration)
    # overlay sponsor slate on the video
    overlay_path = "assets/sponsor-overlay.mp4"
    compiled_file_name = f"video_highlight-{highlight_title}-{highlight_start}-{highlight_end}-{event_names}.mp4"
    compiled_path = os.path.join(highlight_output_dir, compiled_file_name)
    overlay_video(input_path=raw_video_highlight_path, intro_audio_path=intro_audio_path, overlay_path=overlay_path,
                  output_path=compiled_path, intro_duration=intro_duration)
    os.remove(raw_video_highlight_path)

    # return clip local path
    return raw_video_highlight_path
