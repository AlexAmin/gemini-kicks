from models.soccer_event import SoccerEvent
from models.soccer_event_type import SoccerEventTypes

TEAMS_SCHEMA = {
    "type": "object",
    "required": ["teams"],
    "properties": {
        "teams": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "Each item in the array is the name of one team",
            },
        },
    },
}
