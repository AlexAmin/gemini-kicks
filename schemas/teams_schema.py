
from models.basketball_event import BasketballEvent
from models.basketball_event_type import BasketballEventType

TEAMS_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "schema": {
            "properties": {
                "teams": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "Each item in the array is the name of one team",
                    },
                },
            },

            "required": ["teams"],
            "type": "object"
        }
    }
}
