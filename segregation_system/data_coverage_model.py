import numpy as np

from shared.feature import Feature

BOUNDS = {
    Feature.MAD_TIMESTAMPS: (0, 3600),
    Feature.MAD_AMOUNTS: (0, 5000),
    Feature.MEDIAN_LONGITUDE: (-180, 180),
    Feature.MEDIAN_LATITUDE: (-90, 90),
    Feature.MEDIAN_SOURCE_IP: (0, 4294967295),
    Feature.MEDIAN_DESTINATION_IP: (0, 4294967295)
}

class DataCoverageModel:
    def __init__(self, feature_samples: dict[Feature, list[float|int]]):
        self.normalized_features_samples = {}
        for feature, values in feature_samples.items():
            arr = np.array(values)
            t_min, t_max = BOUNDS[feature]
            arr = np.clip(arr, t_min, t_max) # Limit the samples to the theoretical range
            normalized_values = (arr - t_min) / (t_max - t_min)
            self.normalized_features_samples[feature] = normalized_values
