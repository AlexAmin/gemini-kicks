import os
import json
from typing import List, Dict

from llama_api_client import LlamaAPIClient
from pydantic_core.core_schema import json_schema

client = LlamaAPIClient(
    api_key=os.environ.get("LLAMA_API_KEY"),  # This is the default and can be omitted
)

schema = {
    "type": "json_schema",
    "json_schema": {
        "schema": {
            "properties": {
                "trainOfThought": {"type": "array", "items": {"type": "string"}},
                "events": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["Free Throw", "Foul", "Steal", "Turnover", "Timeout", "Substitution"],
                                "description": "What type of event is it?"
                            },
                            "timestamp": {
                                "type": "number",
                                "description": "The input phrase that made you decide that there was an event. Minimum 5 words."
                            }
                        },
                        "required": ["type", "timestamp"]
                    }},
            },
            "required": ["trainOfThought", "events"],
            "type": "object"
        }
    }
}


def event_detection(transcription: List[Dict[str, any]]) -> List[Dict[str, float]]:
    completion = client.chat.completions.create(
        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
        response_format=schema,
        messages=[
            {
                "role": "system",
                "content": """Analyze the following text and detect any basketball events. The possible events are:
            - Free Throw: When a player attempts to score by shooting from the free-throw line after a foul
            - Foul: When a player breaks the rules resulting in a penalty
            - Steal: When a defensive player takes the ball from the offensive player
            - Turnover: When a team loses possession of the ball to the opposing team
            - Timeout: When a team or official stops the game temporarily
            - Substitution: When a player is replaced by another player from the bench
            """
            },
            {
                "role": "user",
                "content": json.dumps(transcription)
            }
        ],
        temperature=0.7
    )
    return json.loads(completion.completion_message.content.text)


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
    result = event_detection(demo)
    print(result)
