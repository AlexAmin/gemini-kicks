import json
import os
import base64
from typing import List

from llama_api_client import LlamaAPIClient

from models.transcription_segment import TranscriptionSegment
from schemas.players_schema import PLAYERS_SCHEMA
from schemas.teams_schema import TEAMS_SCHEMA
from utils_images import base64_encode_image_file
from utils_llm import load_prompt_file
from utils_av import chunk_list

client = LlamaAPIClient(api_key=os.environ.get("LLAMA_API_KEY"))


def player_recognition(transcripts: List[TranscriptionSegment]) -> List[str]:
    input = json.dumps([item.to_dict() for item in transcripts])
    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        response_format=PLAYERS_SCHEMA,
        messages=[
            {
                "role": "system",
                "content": load_prompt_file("prompts/player_recognition_prompt.md")
            },
            {
                "role": "user",
                "content": input
            }
        ],
        temperature=0.0
    )

    output = json.loads(completion.completion_message.content.text)["players"]
    return output
