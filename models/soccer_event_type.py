from enum import Enum

from enum import Enum

class SoccerEventTypes(Enum):
    FOUL = "Foul"
    PENALTY_KICK = "Penalty Kick"
    CORNER_KICK = "Corner Kick"
    THROW_IN = "Throw-in"
    OFFSIDE = "Offside"
    SUBSTITUTION = "Substitution"
    GOAL = "Goal" # Optional, depending if you want exact size or common events
    YELLOW_CARD = "Yellow Card" # Optional