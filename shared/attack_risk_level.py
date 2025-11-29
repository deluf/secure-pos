import enum

class AttackRiskLevel(enum.Enum):
    """
    Enum for different risk levels.
    """
    NORMAL = "normal"
    MODERATE = "moderate"
    HIGH = "high"