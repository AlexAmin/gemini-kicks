import json
from typing import List

from google.genai import types

from gemini.gemini_client import gemini_client
from models.detection_result import DetectionResult
from models.soccer_event import SoccerEvent
from models.transcription_segment import TranscriptionSegment
from schemas.soccer_events_schema import SOCCER_EVENTS_SCHEMA
from utils_llm import load_prompt_file


def detect(transcription: List[TranscriptionSegment], offset: float) -> List[SoccerEvent]:
    transcription_json: str = json.dumps([item.to_dict() for item in transcription])
    prompt: str = load_prompt_file("prompts/soccer_event_detection_prompt.md")

    completion = gemini_client.models.generate_content(
        model="gemini-2.5-flash-preview-04-17",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=1024),
            response_mime_type="application/json",
            response_schema=SOCCER_EVENTS_SCHEMA,
            system_instruction=prompt
        ),
        contents=[
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=transcription_json)]
            ),

        ]
    )
    output = json.loads(completion.text)

    result = DetectionResult(**output)

    # Fix events is null
    if result.events is None:
        result.events = []

    # Convert dictionary events to BasketballEvent instances
    result.events = [SoccerEvent(**event) for event in result.events]

    # Add offset to timestamps for convenience
    result.events = [SoccerEvent(**{**event.__dict__, "timestamp": event.timestamp + offset}) for event in
                     result.events]

    return result.events


if __name__ == "__main__":
    # load demo transcript for testing
    from test_data.demo_transcript import demo_transcript

    # run event detection on demo transcript
    result = detect(demo_transcript, 0.0)
    print(f"event detection result {result}")
