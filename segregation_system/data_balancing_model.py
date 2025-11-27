
class DataBalancingModel:
    def __init__(
        self,
        balancing_tolerance: float,
        target_sessions_per_class: int,
        normal_risk_sessions: int,
        moderate_risk_sessions: int,
        high_risk_sessions: int
    ):
        self.balancing_tolerance = balancing_tolerance
        self.target_sessions_per_class = target_sessions_per_class
        self.normal_risk_sessions = normal_risk_sessions
        self.moderate_risk_sessions = moderate_risk_sessions
        self.high_risk_sessions = high_risk_sessions
