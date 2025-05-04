import os
import json
from typing import List
from utils_llm import load_prompt_file
from llama_api_client import LlamaAPIClient
from models.detection_result import DetectionResult
from models.basketball_event import BasketballEvent
from models.transcription_segment import TranscriptionSegment
from schemas.basketball_events_schema import BASKETBALL_EVENTS_SCHEMA

client = LlamaAPIClient(api_key=os.environ.get("LLAMA_API_KEY"))


def detect(transcription: List[TranscriptionSegment], offset: float) -> List[BasketballEvent]:
    transcription_json = json.dumps([item.to_dict() for item in transcription])
    prompt = load_prompt_file("prompts/basketball_event_detection_prompt.md")
    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        response_format=BASKETBALL_EVENTS_SCHEMA,
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": transcription_json
            }
        ],
        temperature=0.7
    )
    output = json.loads(completion.completion_message.content.text)
    result = DetectionResult(**output)

    # Fix events is null
    if result.events is None:
        result.events = []

    # Convert dictionary events to BasketballEvent instances
    result.events = [BasketballEvent(**event) for event in result.events]

    # Add offset to timestamps for convenience
    result.events = [BasketballEvent(**{**event.__dict__, "timestamp": event.timestamp + offset}) for event in
                     result.events]

    return result.events


if __name__ == "__main__":
    # load demo transcript for testing
    from test_data.demo_transcript import demo_transcript

    # run event detection on demo transcript
    result = detect(demo_transcript, 0.0)
    print(f"event detection result {result}")
