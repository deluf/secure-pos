"""
Provides functionalities for visualizing the data coverage report as a radar chart
"""
import os

import plotly.graph_objects as go
import plotly.express as px

from segregation_system.data_coverage_model import DataCoverageModel

class DataCoverageView:
    """
    Represents the view for the data coverage chart
    """
    @staticmethod
    def build_chart(model: DataCoverageModel):
        """
        Builds a radar chart based on the provided data coverage model

        :param model: The normalized features and samples to be visualized
        :type model: DataCoverageModel
        :return: None
        """
        flat_features = []
        flat_samples = []
        flat_colors = []

        colors = px.colors.qualitative.Plotly
        for feature, samples in model.normalized_features_samples.items():
            for sample in samples:
                flat_features.append(feature.name)
                flat_samples.append(sample)
                flat_colors.append(colors[feature.value % len(colors)])

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=flat_samples,
                theta=flat_features,
                mode="markers",
                marker={"color": flat_colors},
                fill=None,
            )
        )

        fig.update_layout(
            polar={"radialaxis": {"visible": True}},
            showlegend=False,
            title="Data coverage report"
        )

        os.makedirs("output", exist_ok=True)
        fig.write_image("output/data_coverage_report.png")
        print("[DataCoverageView] Data coverage report saved to 'output/data_coverage_report.png'")
