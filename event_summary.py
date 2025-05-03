import os
import json
from typing import List, Dict
from llama_api_client import LlamaAPIClient
from pydantic_core.core_schema import json_schema

from models.basketball_event import BasketballEvent
from models.transcription_segment import TranscriptionSegment
from test_data.demo_transcript import demo_transcript
from util.load_prompt_file import load_prompt_file
from schemas.basketball_events_schema import BASKETBALL_EVENTS_SCHEMA

client = LlamaAPIClient(api_key=os.environ.get("LLAMA_API_KEY"))

def highlight_summary(transcripts: List[TranscriptionSegment]) -> str:
    transcription_json = json.dumps([item.to_dict() for item in transcripts])
    prompt = load_prompt_file("prompts/event_summary_prompt.md")
    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
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
    output = completion.completion_message.content.text
    return output

if __name__ == "__main__":
    result = highlight_summary(demo_transcript)
    print(result)
