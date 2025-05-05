import argparse
import json
import os
import tempfile
from os.path import join as path_join
from typing import List

from api.api import start_api
from clip_video import clip_video
from gemini.extract_keyframes import extract_keyframes
from gemini.prompting.event_detection import detect
from gemini.prompting.event_summary import highlight_summary
from gemini.prompting.player_recognition import player_recognition
from gemini.prompting.speech_to_text import transcribe
from gemini.prompting.team_recognition import team_recognition
from gemini.text_to_speech import text_to_speech
from models.soccer_event import SoccerEvent
from models.summary_length import SummaryLength
from models.transcription_segment import TranscriptionSegment
from produce_highlight_audio import produce_highlight_audio
from produce_highlight_video import produce_highlight_video
from util_io import get_temp_path
from utils_av import \
    get_video_duration_in_seconds, \
    create_16khz_mono_wav_from_video
from utils_llm import get_transcripts_for_highlights

start_api()

def process_video(input_path: str, working_dir: str):
    # very input video file and working directory
    assert input_path is not None, "Input video file is required."
    assert os.path.isfile(input_path), f"Input video file '{input_path}' does not exist."
    if working_dir is None:
        working_dir = ensure_gemini_kicks_dir()
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    assert os.path.isdir(working_dir), f"Working directory '{working_dir}' does not exist."

    teams: List[str] = []
    intro_audio_path: str | None = None
    intro_duration: float = 0.0
    # loop through video using a rolling window
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
    print("Recognizing teams...")
    clipped_video: str = clip_video(video_duration_in_seconds / 2,
                                    (video_duration_in_seconds / 2) + window_duration_in_seconds, input_path)
    keyframes: List[str] = extract_keyframes(clipped_video)
    teams: List[str] = team_recognition(keyframes)
    print(f"Recognized teams {teams}")
    intro_audio_path = text_to_speech(f"{teams[0]} {teams[1]}!!!! Highlights powered by Gemini", "intro-audio")
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
        highlights: List[SoccerEvent] = detect(transcript, offset_start)
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
        video_clip_path = produce_highlight_video(input_path, highlights, intro_audio_path, intro_duration,
                                                 player_string, highlights_start_timestamp, highlights_end_timestamp)
        print(f"Produced video highlight clip: {video_clip_path}")
        audio_clip_path = produce_highlight_audio(intro_audio_path, summary_tts_path, player_string,
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





def ensure_gemini_kicks_dir():
    gemini_kicks_dir = path_join(tempfile.gettempdir(), "gemini-kicks")
    if not os.path.exists(gemini_kicks_dir):
        os.makedirs(gemini_kicks_dir)
    print("Temp directory:", gemini_kicks_dir)
    return gemini_kicks_dir


def parse_cli_args():
    parser = argparse.ArgumentParser(description='gemini-kicks', add_help=False)
    parser.add_argument('-input', nargs='?', default='ger-mex-36-37.mp4', help='Input video of an soccer match.')
    parser.add_argument('-wd', nargs='?', default=ensure_gemini_kicks_dir(), help='Data working directory.')
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
