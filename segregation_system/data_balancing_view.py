import matplotlib.pyplot as plt
import numpy as np

from data_balancing_model import DataBalancingModel
from shared.attack_risk_level import AttackRiskLevel

class DataBalancingView:
    def build_chart(self, model: DataBalancingModel) -> None:
        labels = [AttackRiskLevel.NORMAL, AttackRiskLevel.MODERATE, AttackRiskLevel.HIGH]
        sessions = [
            model.session_counts[AttackRiskLevel.NORMAL],
            model.session_counts[AttackRiskLevel.MODERATE],
            model.session_counts[AttackRiskLevel.HIGH]
        ]
        colors = ['green', 'orange', 'red']

        target = model.target_sessions_per_class
        tolerance = model.balancing_tolerance
        mean = float(np.mean(sessions))

        _, ax = plt.subplots(figsize=(10, 6))

        ax.bar(labels, sessions, color=colors)

        ax.axhline(y=target, color='blue', linewidth=2, label='Target')
        ax.axhline(y=mean, color='black', linewidth=2, label='Mean')
        ax.axhline(y=mean + mean * tolerance, color='black', linestyle='--', label=f'Mean +/- tolerance ({tolerance})')
        ax.axhline(y=mean - mean * tolerance, color='black', linestyle='--')

        ax.set_ylabel("Number of sessions")
        ax.set_xlabel("Attack risk level")
        ax.set_title("Data balancing report")
        ax.legend()

        plt.savefig('data_balancing_report.png')
