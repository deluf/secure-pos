"""
Defines the model for the data coverage report
"""

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
    """
    Represents the model for the data coverage report

    :ivar normalized_features_samples: A dictionary that stores [0, 1] normalized feature samples
    :type normalized_features_samples: dict[Feature, np.ndarray]
    """
    def __init__(self, feature_samples: dict[Feature, list[float|int]]):
        """
        Initializes the object and normalizes feature samples based on predefined bounds

        :param feature_samples: A dictionary that maps a feature to its samples
        :type feature_samples: dict[Feature, list[float|int]]
        """
        self.normalized_features_samples = {}
        for feature, values in feature_samples.items():
            t_min, t_max = BOUNDS[feature]
            arr = np.array(values, copy=False)
            np.clip(arr, t_min, t_max, out=arr) # Limit the samples to the theoretical range
            normalized_samples = (arr - t_min) / (t_max - t_min)
            self.normalized_features_samples[feature] = normalized_samples
