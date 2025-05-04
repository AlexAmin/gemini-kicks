from typing import List
from models.basketball_event import BasketballEvent
from models.transcription_segment import TranscriptionSegment

def load_prompt_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()


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

