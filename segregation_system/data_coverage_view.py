
import plotly.graph_objects as go
import plotly.express as px

from segregation_system.data_coverage_model import DataCoverageModel

class DataCoverageView:

    def __init__(self):
        pass

    def build_chart(self, model: DataCoverageModel):

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
                mode='markers',
                marker={'color': flat_colors},
                fill=None,
            )
        )

        fig.update_layout(
            polar={'radialaxis': {'visible': True}}, # , 'range': [0, 1]
            showlegend=False,
            title="Data coverage report"
        )

        fig.write_image("data_coverage_report.png")
