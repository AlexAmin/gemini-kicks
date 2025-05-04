import os
import time
from groq import Groq
from typing import List
from models.transcription_segment import TranscriptionSegment

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_segments_array(transcription) -> List[TranscriptionSegment]:
    return [
        TranscriptionSegment(
            timestamp=segment["start"],
            text=segment["text"]
        ) for segment in transcription.segments
    ]

def transcribe(file_path: str) -> List[TranscriptionSegment]:
    max_retries = 3
    retry_count = 0

    # Retry because the Groq API sometimes goes down
    # (groq.InternalServerError: Error code: 503 - {'error': {'message': 'Service Unavailable', 'type': 'internal_server_error'}})
    while retry_count < max_retries:
        try:
            with open(file_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=file,
                    model="whisper-large-v3-turbo",
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                    language="en",
                    temperature=0.0
                )
                data = get_segments_array(transcription)
                return data
        except Exception as e:
            print("Transcribe failed because Groq went down... retrying...")
            retry_count += 1
            if retry_count == max_retries:
                raise e
            time.sleep(2 ** retry_count)  # Exponential backoff
    raise Exception("Failed to transcribe audio")


if __name__ == "__main__":
    transcribe("basketball-60-sec.flac", 0)
