from typing import List
from models.soccer_event import SoccerEvent
from models.transcription_segment import TranscriptionSegment


def load_prompt_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()


def get_timestamp_range(highlights: List[SoccerEvent]) -> tuple[float, float]:
    if not highlights: return -1, -1
    timestamps = [event.timestamp for event in highlights]
    return min(timestamps), max(timestamps)


def extract_highlight_data(transcripts: List[TranscriptionSegment], min_timestamp: float, max_timestamp: float) \
        -> List[TranscriptionSegment]:
    if not transcripts:
        return []
    return [t for t in transcripts if min_timestamp <= t.timestamp <= max_timestamp]


def get_transcripts_for_highlights(
        transcripts: List[TranscriptionSegment],
        highlights: List[SoccerEvent]
) -> tuple[tuple[float, float], List[TranscriptionSegment]]:
    if len(highlights) == 0: return (0.0, 0.0), []
    min_timestamp, max_timestamp = get_timestamp_range(highlights)

    # Sometimes there is only one transcript with detection, in this case we'll just assume a timespan
    if min_timestamp == max_timestamp:
        max_timestamp = min_timestamp + 60

    # Find the relevant transcripts within the timestamp range
    filtered_transcripts = extract_highlight_data(transcripts, min_timestamp, max_timestamp)
    min_timestamp = min_timestamp - 10  # 10 second pre-buffer
    return (min_timestamp, max_timestamp), filtered_transcripts
