import os
import argparse
import tempfile
import time
from typing import List
from os.path import join as path_join

from clip_video import clip_video
from event_detection import detect
from event_summary import highlight_summary
from extract_keyframes import extract_keyframes
from models.summary_length import SummaryLength
from models.transcription_segment import TranscriptionSegment
from speech_to_text import transcribe
from models.basketball_event import BasketballEvent
from team_recognition import team_recognition
from text_to_speech import text_to_speech
from util_io import get_temp_path
from utils_llm import get_transcripts_for_highlights
from utils_video import \
    get_video_duration_in_seconds, \
    create_16khz_mono_wav_from_video, \
    overlay_video, \
    clip_segment
import subprocess



def produce_highlight_clip(input_path, highlights: List[BasketballEvent], intro_audio_path: str, intro_duration: float):
    # return if no highlights are found
    if len(highlights) == 0: return
    # encode video clips using ffmpeg
    earlist_start = min([highlight.timestamp for highlight in highlights])
    earlist_start = earlist_start - 15 if earlist_start - 15 > 0 else 0
    latest_end = max([highlight.timestamp for highlight in highlights]) + 15
    # ffmpeg command to extract the highlights
    event_names = [highlight.type for highlight in highlights]
    event_names = '_'.join(event_names)
    file_name = f"clip_{earlist_start}_{latest_end}_{event_names}.mp4"
    output_dir = get_temp_path("highlights-video")
    full_path = os.path.join(output_dir, file_name)
    clip_segment(input_path, earlist_start, latest_end, intro_audio_path, full_path, intro_duration)

    # overlay sponsor slate on the video
    overlay_path = "assets/sponsor_overlay.mp4"
    compiled_file_name = f"compiled_{earlist_start}_{latest_end}_{event_names}.mp4"
    compiled_path = os.path.join(output_dir, compiled_file_name)
    overlay_video(full_path, overlay_path, compiled_path, 0.75, intro_duration)
    os.remove(full_path)

    # return clip local path
    return full_path


def process_video(input_path: str, working_dir: str):
    # very input video file and working directory
    assert input_path is not None, "Input video file is required."
    assert os.path.isfile(input_path), f"Input video file '{input_path}' does not exist."
    if working_dir is None:
        working_dir = ensure_llama_hoops_dir()
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    assert os.path.isdir(working_dir), f"Working directory '{working_dir}' does not exist."

    teams: List[str] = []
    intro_audio_path: str | None = None
    intro_duration: float = 0.0
    # loop thorugh video using a rolling window
    offset_start = 0.0
    window_duration_in_seconds = 60.0
    video_duration_in_seconds = get_video_duration_in_seconds(input_path)
    assert video_duration_in_seconds > 0, f"Video duration is invalid: {video_duration_in_seconds}"

    # Prepare Intro based on the first window in the video
    print("Preparing Intro Audio")
    clipped_video: str = clip_video(0, window_duration_in_seconds, input_path)
    keyframes: List[str] = extract_keyframes(clipped_video)
    teams = team_recognition(keyframes)
    intro_audio_path = text_to_speech(f"{teams[0]}!! versus {teams[1]}!! Highlights! by meta and groq")
    intro_duration = get_video_duration_in_seconds(intro_audio_path)
    print(f"Intro Audio Generated for {teams} @ {intro_audio_path}")
    all_transcripts: List[TranscriptionSegment] = []

    while offset_start < video_duration_in_seconds - window_duration_in_seconds:
        # create a local chunk of audio (rolling windows)
        # ensure audio is encoded in 16khz mono wav format
        window_start = offset_start
        window_end = offset_start + window_duration_in_seconds
        print(f"> Analyze {window_start} - {window_end}")
        chunk_path = create_16khz_mono_wav_from_video(
            input_path,
            window_start,
            window_end,
            working_dir)

        # transcribe audio chunk using groq API
        transcript: List[TranscriptionSegment] = transcribe(chunk_path)

        os.remove(chunk_path)

        # detect highlights in a rolling window to identify key moments
        highlights: List[BasketballEvent] = detect(transcript, offset_start)
        print(f"Found {len(highlights)} highlights")

        # update offset start for the next rolling window
        offset_start += window_duration_in_seconds

        # Don't continue if there are no highlights
        if len(highlights) == 0: continue

        # Find the text segments relevant to these highlights
        highlight_transcripts: List[TranscriptionSegment] = get_transcripts_for_highlights(transcript, highlights)

        # Remember the highlights for the full summary later
        all_transcripts.extend(highlight_transcripts)

        # Generate a clean summary for tts
        summary = highlight_summary(highlight_transcripts, SummaryLength.LONG)
        print("Generated highlight summary")

        # Generate TTS
        summary_tts_path = text_to_speech(summary)
        print(f"Created TTS for summary at {summary_tts_path}")

        # encode video clips using ffmpeg
        video_clip_path = produce_highlight_clip(input_path, highlights, intro_audio_path, intro_duration)
        print(f"Produced video highlight clip: {video_clip_path}")
        audio_clip_path = produce_audio_highlight(intro_audio_path, summary_tts_path)
        print(f"Produced audio highlight clip: {audio_clip_path}")

    # Generate a full summary for the whole match
    print("Generating audio summary for the whole match.. ")
    full_summary: str = highlight_summary(all_transcripts, SummaryLength.XXL)
    # Create TTS for it
    full_summary_tts_path: str = text_to_speech(full_summary, "full-summary")
    print(f"Full summary generated at {full_summary_tts_path}")


def produce_audio_highlight(intro_audio_path: str, summary_audio_path: str) -> str:
    # Generate TTS for summary
    # ffmpeg command to combine background radio with intro and summary audio
    timestamp = str(int(time.time()))
    output_path = os.path.join(get_temp_path("highlights-audio"), f"audio-highlight-{timestamp}.mp3")

    cmd = [
        "ffmpeg",
        "-i", intro_audio_path,
        "-i", summary_audio_path,
        "-y",
        output_path
    ]

    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


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
