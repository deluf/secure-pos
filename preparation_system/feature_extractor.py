from statistics import median
from typing import Dict, Any

from ingestion_system.raw_session import RawSession


class FeatureExtractor:
	"""Extracts statistical features from a *corrected* RawSession.

	Assumes that:
	- all numeric sequences have no None values (handled in DataCorrector),
	- absolute outliers on amounts have already been clipped.
	"""

	def __init__(self, extracted_features: list[str]):
		self.extracted_features = extracted_features

	@staticmethod
	def _mad(values: list[float]) -> float:
		if not values:
			return 0.0
		m = median(values)
		deviations = [abs(v - m) for v in values]
		return float(median(deviations))

	@staticmethod
	def _ip_to_int(ip: str) -> int:
		parts = ip.split(".")
		if len(parts) != 4:
			return 0
		try:
			return (
				(int(parts[0]) << 24)
				+ (int(parts[1]) << 16)
				+ (int(parts[2]) << 8)
				+ int(parts[3])
			)
		except ValueError:
			return 0

	def extract_features(self, session: RawSession) -> Dict[str, Any]:
		"""Extract the configured features from a *corrected* RawSession.

		The feature names match those listed in preparation_system/json/config.json.
		"""
		result: Dict[str, Any] = {"uuid": session.uuid}

		if session.label is not None:
			result["label"] = session.label

		# At this point numeric lists (timestamp, amount, longitude, latitude)
		# are expected to be fully populated (no None) thanks to DataCorrector.
		timestamps = list(session.timestamp)
		amounts = list(session.amount)
		longitudes = list(session.longitude)
		latitudes = list(session.latitude)

		source_ips = list(session.source_ip)
		dest_ips = list(session.dest_ip)

		if "meanAbsoluteDeviationTransactionTimestamps" in self.extracted_features:
			result["meanAbsoluteDeviationTransactionTimestamps"] = self._mad(timestamps)

		if "meanAbsoluteDeviationTransactionAmounts" in self.extracted_features:
			result["meanAbsoluteDeviationTransactionAmounts"] = self._mad(amounts)

		if "medianLongitude" in self.extracted_features:
			result["medianLongitude"] = float(median(longitudes)) if longitudes else 0.0

		if "medianLatitude" in self.extracted_features:
			result["medianLatitude"] = float(median(latitudes)) if latitudes else 0.0

		if "medianSourceIP" in self.extracted_features:
			ip_ints = [self._ip_to_int(ip) for ip in source_ips]
			result["medianSourceIP"] = int(median(ip_ints)) if ip_ints else 0

		if "medianDestinationIP" in self.extracted_features:
			ip_ints = [self._ip_to_int(ip) for ip in dest_ips]
			result["medianDestinationIP"] = int(median(ip_ints)) if ip_ints else 0

		return result

