import os
import json
import time
from typing import List, Dict
from groq import Groq
from typing import List, Dict

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_segments_array(transcription, offset_start: float = 0.0):
    """Convert transcription segments to array of timestamp-text objects"""
    return [{"timestamp": segment["start"] + offset_start, "text": segment["text"]} for segment in
            transcription.segments]


def transcribe(file_path: str, offset_start: float) -> List[Dict[str, any]]:
    start_time = time.time()
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

        end_time = time.time()
        print(f"Transcription took {end_time - start_time:.2f} seconds")
        return get_segments_array(transcription, offset_start)

if __name__ == "__main__":
    speech_to_text("basketball-60-sec.flac", 0)
