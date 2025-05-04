import os
import argparse
import tempfile
import time
import json
from typing import List
from os.path import join as path_join

from api.api import start_api
from clip_video import clip_video
from event_detection import detect
from os.path import join as path_join
from event_summary import highlight_summary
from extract_keyframes import extract_keyframes
from models.summary_length import SummaryLength
from models.transcription_segment import TranscriptionSegment
from player_recognition import player_recognition
from speech_to_text import transcribe
from models.basketball_event import BasketballEvent
from team_recognition import team_recognition
from text_to_speech import text_to_speech
from util_io import get_temp_path
from utils_llm import get_transcripts_for_highlights
from utils_av import \
    get_video_duration_in_seconds, \
    create_16khz_mono_wav_from_video, \
    produce_audio_highlight, \
    overlay_video, \
    clip_segment
import subprocess

start_api()


def produce_highlight_clip(input_path, highlights: List[BasketballEvent], intro_audio_path: str, intro_duration: float,
                           highlight_title: str, highlight_start: float, highlight_end: float):
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
    overlay_path = "assets/sponsor_overlay.mp4"
    compiled_file_name = f"video_highlight-{highlight_title}-{highlight_start}-{highlight_end}-{event_names}.mp4"
    compiled_path = os.path.join(highlight_output_dir, compiled_file_name)
    overlay_video(raw_video_highlight_path, overlay_path, compiled_path, 0.75, intro_duration)
    os.remove(raw_video_highlight_path)

    # return clip local path
    return raw_video_highlight_path


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

    # Prepare path for status file
    status_path = get_temp_path("status")
    status_file = os.path.join(status_path, "status.json")
    with open(status_file, "w") as f:
        json.dump({"status": "intro", "teams": ", ".join(teams), "full_duration": video_duration_in_seconds}, f)

    # Prepare Intro based on the first window in the video
    print("Preparing Intro Audio")
    clipped_video: str = clip_video(video_duration_in_seconds / 2,
                                    (video_duration_in_seconds / 2) + window_duration_in_seconds, input_path)
    keyframes: List[str] = extract_keyframes(clipped_video)
    teams = team_recognition(keyframes)
    intro_audio_path = text_to_speech(f"{teams[0]} {teams[1]}!!!! Highlights with meta and groq", "intro-audio")
    intro_duration = get_video_duration_in_seconds(intro_audio_path)
    print(f"Intro Audio Generated for {teams} @ {intro_audio_path}")
    all_transcripts: List[TranscriptionSegment] = []
    all_players = []

    while offset_start < video_duration_in_seconds - window_duration_in_seconds:
        # create a local chunk of audio (rolling windows)
        # ensure audio is encoded in 16khz mono wav format
        window_start = offset_start
        window_end = offset_start + window_duration_in_seconds

        # Write status for use in frontend
        with open(status_file, "w") as f:
            json.dump({"status": "generating", "window_start": window_start, "window_end": window_end, "teams": ", ".join(teams), "full_duration": video_duration_in_seconds}, f)

        # Begin Analysis
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
        highlight_data: tuple[tuple[float, float], List[TranscriptionSegment]] = get_transcripts_for_highlights(
            transcript, highlights)
        highlights_start_timestamp = highlight_data[0][0]
        highlights_end_timestamp = highlight_data[0][1]
        highlight_transcripts = highlight_data[1]
        print(f"highlights {highlight_data}")
        # Remember the highlights for the full summary later
        all_transcripts.extend(highlight_transcripts)

        # Generate a clean summary for tts
        players = player_recognition(highlight_transcripts)
        player_string = "_".join(players)
        if len(player_string) == 0:
            player_string = "?"
        all_players.extend(players)
        summary = highlight_summary(highlight_transcripts, SummaryLength.MEDIUM)
        print("Generated highlight summary")

        # Generate TTS
        summary_tts_path = text_to_speech(summary)
        print(f"Created TTS for summary at {summary_tts_path}")

        # encode video clips using ffmpeg
        video_clip_path = produce_highlight_clip(input_path, highlights, intro_audio_path, intro_duration,
                                                 player_string, highlights_start_timestamp, highlights_end_timestamp)
        print(f"Produced video highlight clip: {video_clip_path}")
        audio_clip_path = produce_audio_highlight(intro_audio_path, summary_tts_path, player_string,
                                                  highlights_start_timestamp, highlights_end_timestamp)
        print(f"Produced audio highlight clip: {audio_clip_path}")

    with open(status_file, "w") as f:
        json.dump({"status": "audio-summary", "teams": ", ".join(teams), "full_duration": video_duration_in_seconds}, f)
    # Generate a full summary for the whole match
    print("Generating audio summary for the whole match.. ")
    full_summary: str = highlight_summary(all_transcripts, SummaryLength.XXL)
    # Create TTS for it
    full_summary_tts_path: str = text_to_speech(full_summary, "_".join(all_players), "full-summary")
    print(f"Full summary generated at {full_summary_tts_path}")
    with open(status_file, "w") as f:
        json.dump({"status": "done", "teams": ", ".join(teams), "full_duration": video_duration_in_seconds}, f)


def produce_audio_highlight(intro_audio_path: str, summary_audio_path: str, highlight_title: str,
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
