from type.basketball_event import BasketballEvent

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
                                "enum": [e.value for e in BasketballEvent]
                            },
                            "confidence": {
                                "type": "number",
                                "description": "0 no confidence. 1 maximum confidence"
                            },
                            "timestamp": {
                                "type": "number",
                                "description": "The input phrase that made you decide that there was an event. Minimum 5 words."
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
