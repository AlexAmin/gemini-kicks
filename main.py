import os
import argparse
import tempfile
from typing import List
from os.path import join as path_join
from event_detection import detect
from speech_to_text import transcribe
from models.basketball_event import BasketballEvent
from utils import get_video_duration_in_seconds, create_16khz_mono_wav_from_video, clip_segment

def publish_clip(clip_local_path):
    # publish clips to configured distribution channels
    # CODE
    return {
        'status': 'success',
        'message': 'Clip published successfully.'
    }

def produce_highlight_clip(input_path, highlights: List[BasketballEvent], clip_local_path):
    # encode video clips using ffmpeg
    earlist_start = min([highlight['start'] for highlight in highlights])
    latest_end = max([highlight['end'] for highlight in highlights])
    # ffmpeg command to extract the highlights
    clip_segment(input_path, earlist_start, latest_end, clip_local_path)
    # return clip local path
    print(f"Produced highlight clip: {clip_local_path} and found {len(highlights)} highlights")


def process_video(input_path: str, working_dir: str):
    # very input video file and working directory
    assert input_path is not None, "Input video file is required."
    assert os.path.isfile(input_path), f"Input video file '{input_path}' does not exist."
    if working_dir is None:
        working_dir = ensure_llama_hoops_dir()
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    assert os.path.isdir(working_dir), f"Working directory '{working_dir}' does not exist."

    # loop thorugh video using a rolling window
    offset_start = 0.0
    window_duration_in_seconds = 60.0
    video_duration_in_seconds = get_video_duration_in_seconds(input_path)
    assert video_duration_in_seconds > 0, f"Video duration is invalid: {video_duration_in_seconds}"

    while offset_start < video_duration_in_seconds - window_duration_in_seconds:
        # create a local chunk of audio (rolling windows)
        # ensure audio is encoded in 16khz mono wav format
        chunk_path = create_16khz_mono_wav_from_video(
            input_path,
            offset_start,
            offset_start + window_duration_in_seconds,
            working_dir)

        # transcribe audio chunk using groq API
        transcript = transcribe(chunk_path, offset_start)

        # detect highlights in rolling window to identify key moments
        highlights = detect(transcript, offset_start)

        # encode video clips using ffmpeg
        clip_local_path = os.path.join(working_dir, 'clip.mp4')
        produce_highlight_clip(input_path, highlights, clip_local_path)
        
        # public clips to configured distribution channels
        publish_clip(clip_local_path)

        # update offset start for next rolling window
        offset_start += window_duration_in_seconds


def ensure_llama_hoops_dir():
    llama_hoops_dir = path_join(tempfile.gettempdir(), 'llama-hoops')
    if not os.path.exists(llama_hoops_dir):
        os.makedirs(llama_hoops_dir)
    print("Temp directory:", llama_hoops_dir)
    return llama_hoops_dir


def parse_cli_args():
    parser = argparse.ArgumentParser(description='llama-hoops', add_help=False)
    parser.add_argument('-input', nargs='?', default='lakers_mavs_20250409.mp4', help='Input video of an NBA match.')
    parser.add_argument('-wd', nargs='?', default=ensure_llama_hoops_dir(), help='Data working directory.')
    args = parser.parse_args()
    return args


def main():
    # parse input parameters and resolve app path
    args = parse_cli_args()

    # main processing function that loops 
    # through the video using a rolling window
    process_video(args.input, args.wd)


if __name__ == '__main__':
    main()
