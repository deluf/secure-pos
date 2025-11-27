
import matplotlib.pyplot as plt
import numpy as np

from data_balancing_model import DataBalancingModel

class DataBalancingView:
    def build_chart(self, model: DataBalancingModel) -> None:
        labels = ['Normal', 'Moderate', 'High']
        sessions = [
            model.normal_risk_sessions,
            model.moderate_risk_sessions,
            model.high_risk_sessions
        ]
        colors = ['green', 'orange', 'red']

        target = model.target_sessions_per_class
        tolerance = model.balancing_tolerance
        mean_sessions = float(np.mean(sessions))

        _, ax = plt.subplots(figsize=(10, 6))

        ax.bar(labels, sessions, color=colors)

        ax.axhline(y=target, color='blue', linewidth=2, label='Target')
        ax.axhline(y=mean_sessions, color='black', linewidth=2, label='Mean')
        ax.axhline(y=mean_sessions + mean_sessions * tolerance,
                   color='black', linestyle='--', label=f'Mean +/- tolerance ({tolerance})')
        ax.axhline(y=mean_sessions - mean_sessions * tolerance, color='black', linestyle='--')

        ax.set_ylabel("Number of sessions")
        ax.set_xlabel("Risk level")
        ax.set_title("Data balancing report")
        ax.legend()

        plt.savefig('balancing_report.png')
