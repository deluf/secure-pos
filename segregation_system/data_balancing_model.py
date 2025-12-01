from shared.attack_risk_level import AttackRiskLevel

class DataBalancingModel:
    def __init__(
        self,
        balancing_tolerance: float,
        target_sessions_per_class: int,
        session_counts: dict[AttackRiskLevel, int],
    ):
        self.balancing_tolerance = balancing_tolerance
        self.target_sessions_per_class = target_sessions_per_class
        self.session_counts = session_counts
