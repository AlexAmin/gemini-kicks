from dataclasses import dataclass
from models.soccer_event_type import SoccerEventTypes

@dataclass
class SoccerEvent:
    type: SoccerEventTypes
    confidence: float
    timestamp: float
