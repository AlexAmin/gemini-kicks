from models.basketball_event import BasketballEvent
from models.basketball_event_type import BasketballEventType

BASKETBALL_EVENTS_SCHEMA = {
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
                                "enum": [e.value for e in BasketballEventType]
                            },
                            "confidence": {
                                "type": "number",
                                "description": "0.0 no confidence. 1.0 maximum confidence"
                            },
                            "timestamp": {
                                "type": "number"
                            }
                        },
                        "required": ["type", "confidence", "timestamp"]
                    }},
            },
            "required": ["trainOfThought", "events"],
            "type": "object"
        }
    }
}
