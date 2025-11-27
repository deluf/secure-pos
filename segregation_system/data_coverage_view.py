
import plotly.graph_objects as go
import plotly.express as px

from data_coverage_model import DataCoverageModel, FeatureSamples
from feature import Feature

class DataCoverageView:

    def __init__(self):
        pass

    def build_chart(self, model: DataCoverageModel):

        flat_features = []
        flat_samples = []
        flat_colors = []

        colors = px.colors.qualitative.Plotly
        for i, element in enumerate(model.coverage):
            for sample in element.samples:
                flat_features.append(element.feature.name)
                flat_samples.append(sample)
                flat_colors.append(colors[i % len(colors)])

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=flat_samples,
                theta=flat_features,
                mode='markers',
                marker={'color': flat_colors},
                fill=None,
            )
        )

        fig.update_layout(
            polar={'radialaxis': {'visible': True, 'range': [0, 1]}},
            showlegend=False,
            title="Data coverage report"
        )

        fig.write_image("coverage_report.png")
