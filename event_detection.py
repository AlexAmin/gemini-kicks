import os
import json
from typing import List, Dict
from llama_api_client import LlamaAPIClient
from pydantic_core.core_schema import json_schema
from type.basketball_event import BasketballEvent
from util.load_prompt_file import load_prompt_file
from schemas.basketball_events_schema import BASKETBALL_EVENTS_SCHEMA

client = LlamaAPIClient(api_key=os.environ.get("LLAMA_API_KEY"))

def detect(transcription: List[Dict[str, any]], offset: float) -> List[Dict[str, float]]:
    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        response_format=BASKETBALL_EVENTS_SCHEMA,
        messages=[
            {
                "role": "system",
                "content": load_prompt_file("prompts/basketball_event_detection_prompt.md")
            },
            {
                "role": "user",
                "content": json.dumps(transcription)
            }
        ],
        temperature=0.7
    )
    output = json.loads(completion.completion_message.content.text)
    return output["events"]


demo = [
    {
        "timestamp": 60,
        "text": " und die Beine von K\u00f6ln."
    },
    {
        "timestamp": 62,
        "text": " Das ist ein guter Pass von Michael Duvaux."
    },
    {
        "timestamp": 65,
        "text": " Da ist der Korridor so winzig,"
    },
    {
        "timestamp": 67,
        "text": " muss genau so kommen und landet in den Armen von Tatschenkov."
    },
    {
        "timestamp": 75,
        "text": " Unsauber."
    },
    {
        "timestamp": 77,
        "text": " Dieser Einwurf von K\u00e4rlesen."
    },
    {
        "timestamp": 84,
        "text": " Vogtmann sagt Danke."
    },
    {
        "timestamp": 86,
        "text": " Beide Mannschaften und die Ballverluste."
    },
    {
        "timestamp": 89,
        "text": " Das ist ein sehr guter Torwart."
    },
    {
        "timestamp": 91,
        "text": " Bayern 6, MBC 6."
    },
    {
        "timestamp": 93,
        "text": " Zu diesem Zeitpunkt echt nicht wenig."
    },
    {
        "timestamp": 95,
        "text": " DeVoe."
    },
    {
        "timestamp": 97,
        "text": " Two-Man-Game mit John Bryant."
    },
    {
        "timestamp": 99,
        "text": " Das geht komplett in die Hose."
    },
    {
        "timestamp": 101,
        "text": " Wackeliger Start."
    },
    {
        "timestamp": 103,
        "text": " Der Wei\u00dfenfelser in dieses zweite Viertel."
    },
    {
        "timestamp": 111,
        "text": " Also klar, gut von Vogtmann Druck gemacht."
    },
    {
        "timestamp": 114,
        "text": " Aber das ist einfach schlampig."
    },
    {
        "timestamp": 117,
        "text": " und Callison und ein bisschen John Bryant."
    }
]

if __name__ == "__main__":
    result = detect(demo, 0.0)
    print(result)
