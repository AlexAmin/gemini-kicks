from typing import Dict
from dataclasses import dataclass

@dataclass(frozen=True)
class TranscriptionSegment:
    timestamp: float
    text: str

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "text": self.text,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "TranscriptionSegment":
        return cls(
            timestamp=data["timestamp"],
            text=data["text"]
        )
