import json
import os
import base64
from typing import List

from llama_api_client import LlamaAPIClient

from schemas.teams_schema import TEAMS_SCHEMA
from utils_images import base64_encode_image_file
from utils_llm import load_prompt_file

client = LlamaAPIClient(api_key=os.environ.get("LLAMA_API_KEY"))


def team_recognition(file_paths: [str]) -> [str]:
    images = []
    for file_path in file_paths:
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
    return output


if __name__ == "__main__":
    result = team_recognition([
        "test_data/test-images/keyframe-1746318762_003.jpg",
        "test_data/test-images/keyframe-1746318762_004.jpg",
        "test_data/test-images/keyframe-1746318762_005.jpg",
        "test_data/test-images/keyframe-1746318762_006.jpg"
    ])
    print(result)
