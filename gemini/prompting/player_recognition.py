import json
from typing import List

from google.genai import types

from gemini.gemini_client import gemini_client
from models.transcription_segment import TranscriptionSegment
from schemas.players_schema import PLAYERS_SCHEMA
from test_data.demo_transcript import demo_transcript
from utils_llm import load_prompt_file


def player_recognition(transcripts: List[TranscriptionSegment]) -> List[str]:
    input = json.dumps([item.to_dict() for item in transcripts])
    completion = gemini_client.models.generate_content(
        model="gemini-2.5-flash-preview-04-17",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PLAYERS_SCHEMA,
            system_instruction=load_prompt_file("prompts/player_recognition_prompt.md")
        ),
        contents=[
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=input)]
            )
        ]
    )
    output = json.loads(completion.text)["players"]
    return output

if __name__ == "__main__":
    players = player_recognition(demo_transcript)
    print(f"recognized players: {players}")