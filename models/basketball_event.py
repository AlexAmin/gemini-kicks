from dataclasses import dataclass
from models.basketball_event_type import BasketballEventType

@dataclass
class BasketballEvent:
    type: BasketballEventType
    confidence: float
    timestamp: float
