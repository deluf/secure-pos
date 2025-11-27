from feature import Feature

class FeatureSamples:
    def __init__(self, feature: Feature, samples: list[float]):
        self.feature = feature
        self.samples = samples

class DataCoverageModel:
    def __init__(self, feature_samples: list[FeatureSamples]):
        self.coverage = feature_samples
