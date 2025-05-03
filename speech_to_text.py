import os
from groq import Groq
from typing import List, Dict

from models.basketball_event import BasketballEvent
from models.transcription_segment import TranscriptionSegment

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_segments_array(transcription, offset_start: float = 0.0) -> List[TranscriptionSegment]:
    return [
        TranscriptionSegment(
            timestamp=segment["start"] + offset_start,
            text=segment["text"]
        ) for segment in transcription.segments
    ]


def transcribe(file_path: str, offset_start: float) -> List[TranscriptionSegment]:
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3-turbo",
            prompt="Specify context or spelling",
            response_format="verbose_json",
            timestamp_granularities=["segment"],
            language="en",
            temperature=0.0
        )
        data = get_segments_array(transcription, offset_start)
        return data


if __name__ == "__main__":
    transcribe("basketball-60-sec.flac", 0)
