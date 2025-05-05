from models.soccer_event_type import SoccerEventTypes
from models.soccer_event import SoccerEvent

SOCCER_EVENTS_SCHEMA = {
    "type": "object",
    "properties": {
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [e.value for e in SoccerEventTypes]
                    },
                    "confidence": {
                        "type": "number",
                        "format": "float",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "0.0 no confidence. 1.0 maximum confidence"
                    },
                    "timestamp": {
                        "type": "number",
                        "format": "float"
                    }
                },
                "required": ["type", "confidence", "timestamp"]
            }
        }
    },
    "required": ["events"]
}
