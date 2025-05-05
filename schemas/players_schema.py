from models.soccer_event import SoccerEvent
from models.soccer_event_type import SoccerEventTypes

PLAYERS_SCHEMA = {
    "type": "object",
    "required": ["players"],
    "properties": {
        "players": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "Each item in the array is the name of one player",
            },
        },
    },
}
