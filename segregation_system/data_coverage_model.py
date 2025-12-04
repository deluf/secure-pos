"""
Defines the model for the data coverage report
"""

from typing import Final

import numpy as np

from segregation_system.prepared_sessions_db import PreparedSession
from shared.feature import Feature

class DataCoverageModel:
    """
    Represents the model for the data coverage report

    :ivar normalized_features_samples: A dictionary that stores [0, 1] normalized feature samples
    :type normalized_features_samples: dict[Feature, np.ndarray]
    """

    # Feature -> (Attribute Name, Min, Max)
    FEATURE_CONFIG: Final[dict[Feature, tuple[str, float, float]]] = {
        Feature.MAD_TIMESTAMPS: ("mad_timestamps", 0, 600),
        Feature.MAD_AMOUNTS: ("mad_amounts", 0, 1000),
        Feature.MEDIAN_LONGITUDE: ("median_longitude", -180, 180),
        Feature.MEDIAN_LATITUDE: ("median_latitude", -90, 90),
        Feature.MEDIAN_SOURCE_IP: ("median_source_ip", 0, 4294967295),
        Feature.MEDIAN_DESTINATION_IP: ("median_destination_ip", 0, 4294967295)
    }

    def __init__(self, sessions: list[PreparedSession]):
        self.normalized_features_samples = {}

        if not sessions:
            for feature in self.FEATURE_CONFIG:
                self.normalized_features_samples[feature] = np.array([])
            return

        for feature, (attr_name, t_min, t_max) in self.FEATURE_CONFIG.items():
            raw_values = [getattr(s, attr_name) for s in sessions]
            arr = np.array(raw_values, dtype=np.float32)
            np.clip(arr, t_min, t_max, out=arr)
            arr -= t_min
            arr /= t_max - t_min
            self.normalized_features_samples[feature] = arr
