"""
Defines the model for the data balancing report
"""
from segregation_system.prepared_sessions_db import PreparedSession
from shared.attack_risk_level import AttackRiskLevel

class DataBalancingModel:
    """
    Represents the model for the data balancing report

    :ivar balancing_tolerance: The tolerance level allowed for class balancing
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
    ):
        """
        Initializes the class attributes
        FIXME:
        :param balancing_tolerance: The tolerance level allowed for class balancing [0, 1]
        :type balancing_tolerance: float
        :param target_sessions_per_class: The target number of sessions expected per class
        :type target_sessions_per_class: int
        :param session_counts: A dictionary mapping risk levels to the number of times they
         appear in the dataset
        :type session_counts: dict[AttackRiskLevel, int]
        """
        self.balancing_tolerance = balancing_tolerance
        self.target_sessions_per_class = target_sessions_per_class

        session_counts = {}
        for session in sessions:
            session_counts[session.label] = session_counts.get(session.label, 0) + 1
        # Ensures that all levels are present in the dictionary
        self.session_counts = self.session_counts = {
            level: session_counts.get(level, 0)
            for level in AttackRiskLevel
        }
