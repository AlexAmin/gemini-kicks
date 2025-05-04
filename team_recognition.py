import json
import os
import base64
from typing import List

from llama_api_client import LlamaAPIClient

from schemas.teams_schema import TEAMS_SCHEMA
from utils_images import base64_encode_image_file
from utils_llm import load_prompt_file
from utils_video import chunk_list

client = LlamaAPIClient(api_key=os.environ.get("LLAMA_API_KEY"))


def team_recognition(file_paths: List[str]) -> List[str]:
    # Llama API supports a max of 8 files
    file_chunks = chunk_list(file_paths, 8)
    teams = []
    images = []
    #for chunk in file_chunks:
    chunk = file_chunks[0]
    for file_path in chunk:
        base64_image = base64_encode_image_file(file_path)
        images.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpg;base64,{base64_image}"
            }
        })
    
    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        response_format=TEAMS_SCHEMA,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": load_prompt_file("prompts/team_recognition_prompt.md")
                    },
                    *images
                ]
            }
        ],
        temperature=0.0
    )
    output = json.loads(completion.completion_message.content.text)["teams"]
    teams.extend(output)

    # Filter duplicates case-insensitively
    unique_teams = []
    seen = set()
    for team in teams:
        normalized = team.lower().replace(" ", "")
        if normalized not in seen:
            seen.add(normalized)
            unique_teams.append(team)

    return unique_teams[:2]


if __name__ == "__main__":
    result = team_recognition([
        "test_data/test-images/keyframe-1746318762_003.jpg",
        "test_data/test-images/keyframe-1746318762_004.jpg",
        "test_data/test-images/keyframe-1746318762_005.jpg",
        "test_data/test-images/keyframe-1746318762_006.jpg"
    ])
    print(f"recornized team from fframes: {result}")
