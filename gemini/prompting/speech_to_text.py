import time
import types
from typing import List

from google.genai.types import Part

from gemini.gemini_client import gemini_client
from models.transcription_segment import TranscriptionSegment


def get_segments_array(transcription: List[str]) -> List[TranscriptionSegment]:
    split_lines: List[List[str]] = [segment.split(";") for segment in transcription if len(segment) > 3]

    return [
        TranscriptionSegment(
            timestamp=float(segment[0]),
            text=segment[1]
        ) for segment in split_lines
    ]


def transcribe(file_path: str) -> List[TranscriptionSegment]:
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            audios = []
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
                audios.append(Part.from_bytes(
                    data=file_bytes,
                    mime_type="audio/mp3"
                ))

            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash-lite", contents=[
                    # Use semicolon to prevent separating the actual text
                    "Transcribe and output second;text as semicolon separated CSV. Example output \"15;hello world\"",
                    audios
                ]
            )
            transcriptions = get_segments_array(response.text.replace("```", "").split("\n")[2:])
            print(f"Transcriptions {transcriptions}")
            return transcriptions
        except Exception as e:
            # Gemini sometimes goes down and returns a 503 error...
            # google.genai.errors.ServerError: 503 UNAVAILABLE.
            # {'error': {'code': 503, 'message': 'The model is overloaded. Please try again later.', 'status': 'UNAVAILABLE'}}
            print("Transcribe failed because Gemini went down... retrying...")
            retry_count += 1
            if retry_count == max_retries:
                raise e
            time.sleep(2 ** retry_count)  # Exponential backoff
    raise Exception("Failed to transcribe audio")


if __name__ == "__main__":
    start_time = time.time()
    result = transcribe("ger-mex-33-37.mp3")
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Transcription completed in {execution_time:.2f} seconds")
    print(f"Transcription result: {result}")
