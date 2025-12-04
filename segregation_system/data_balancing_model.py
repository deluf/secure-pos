"""
Defines the model for the data balancing report
"""

from collections import Counter

from segregation_system.prepared_sessions_db import PreparedSession
from shared.attack_risk_level import AttackRiskLevel

class DataBalancingModel:
    """
    Represents the model for the data balancing report

    :ivar balancing_tolerance: The tolerance level allowed for class balancing [0, 1]
    :type balancing_tolerance: float
    :ivar target_sessions_per_class: The target number of sessions expected per class
    :type target_sessions_per_class: int
    :ivar session_counts: A dictionary mapping risk levels to the number of times they
     appear in the dataset
    :type session_counts: dict[AttackRiskLevel, int]
    """
    def __init__(
        self,
        balancing_tolerance: float,
        target_sessions_per_class: int,
        sessions: list[PreparedSession]
    ) -> None:
        self.balancing_tolerance = balancing_tolerance
        self.target_sessions_per_class = target_sessions_per_class
        counts = Counter(session.label for session in sessions)
        self.session_counts = {
            level: counts[level]
            for level in AttackRiskLevel
        }
