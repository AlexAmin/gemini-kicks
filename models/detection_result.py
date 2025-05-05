from typing import List
from dataclasses import dataclass
from models.soccer_event import SoccerEvent

@dataclass
class DetectionResult:
    events: List[SoccerEvent]
    