import json
import os
from typing import List
from utils import load_prompt_file
from llama_api_client import LlamaAPIClient
from models.detection_result import DetectionResult
from models.basketball_event import BasketballEvent
from models.transcription_segment import TranscriptionSegment
from schemas.basketball_events_schema import BASKETBALL_EVENTS_SCHEMA

client = LlamaAPIClient(api_key=os.environ.get("LLAMA_API_KEY"))

def detect(transcription: List[TranscriptionSegment], offset: float) -> DetectionResult:
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
    # fix offset for each event
    if result.events is None:
        result.events = []
    for event in result.events:
        event['timestamp'] += offset

    return result


if __name__ == "__main__":
    # load demo transcript for testing
    from test_data.demo_transcript import demo_transcript
    # run event detection on demo transcript
    result = detect(demo_transcript, 0.0)
    print(result)
