import json
from typing import List

from google.genai import types

from gemini.gemini_client import gemini_client
from schemas.teams_schema import TEAMS_SCHEMA
from utils_llm import load_prompt_file


def team_recognition(file_paths: List[str]) -> List[str]:
    images = []
    for file_path in file_paths[:5]:
        with open(file_path, 'rb') as f:
            image_bytes = f.read()
            images.append(types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/png'
            ))

    completion = gemini_client.models.generate_content(
        model="gemini-2.5-flash-preview-04-17",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=1024),
            response_mime_type="application/json",
            response_schema=TEAMS_SCHEMA,
            system_instruction=load_prompt_file("prompts/team_recognition_prompt.md")
        ),
        contents=[*images]
    )
    output = json.loads(completion.text)
    return output["teams"]


if __name__ == "__main__":
    result = team_recognition([
        "test_data/test-images/keyframe1746476897_001.jpg",
        "test_data/test-images/keyframe1746476897_002.jpg",
        "test_data/test-images/keyframe1746476897_003.jpg",
        "test_data/test-images/keyframe1746476897_004.jpg"
    ])
    print(f"recognized team from frames: {result}")
