from enum import Enum

class AttackRiskLevel(str, Enum):
    """
    Enum for different risk levels.
    """
    NORMAL = "normal"
    MODERATE = "moderate"
    HIGH = "high"