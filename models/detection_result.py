from typing import List
from dataclasses import dataclass
from models.basketball_event import BasketballEvent

@dataclass
class DetectionResult:
    trainOfThought: str
    events: List[BasketballEvent]
    