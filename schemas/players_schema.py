
from models.basketball_event import BasketballEvent
from models.basketball_event_type import BasketballEventType

PLAYERS_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "schema": {
            "properties": {
                "players": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "Each item in the array is the name of one player",
                    },
                },
            },
            "required": ["players"],
            "type": "object"
        }
    }
}
