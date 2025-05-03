from enum import Enum

class BasketballEventType(Enum):
    FREE_THROW = "Free Throw"
    FOUL = "Foul"
    STEAL = "Steal"
    TURNOVER = "Turnover"
    TIMEOUT = "Timeout"
    SUBSTITUTION = "Substitution"
