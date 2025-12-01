import json

from ingestion_system.raw_session import RawSession
from shared.jsonio import JsonIO
from shared.address import Address
from shared.loader import load_and_validate_json_file

from preparation_system.data_corrector import DataCorrector
from preparation_system.feature_extractor import FeatureExtractor


class PreparationSystem:
	CONFIG_PATH = "preparation_system/json/config.json"
	CONFIG_SCHEMA = {
		"type": "object",
		"properties": {
			"developmentPhase": {"type": "boolean"},
			"classificationSystemAddress": {"type": "string"},
			"segregationSystemAddress": {"type": "string"},
			"maxTransactionsAmount": {"type": "number", "minimum": 0},
			"extractedFeatures": {
				"type": "array",
				"items": {"type": "string"}
			}
		},
		"required": [
			"developmentPhase",
			"classificationSystemAddress",
			"segregationSystemAddress",
			"maxTransactionsAmount",
			"extractedFeatures"
		]
	}

	RAW_SESSION_SCHEMA = {
		"type": "object",
		"properties": {
			"uuid": {"type": "string"},
			"timestamp": {
				"type": "array",
				"items": {"type": ["number", "null"]}
			},
			"amount": {
				"type": "array",
				"items": {"type": ["number", "null"]}
			},
			"source_ip": {
				"type": "array",
				"items": {"type": ["string", "null"]}
			},
			"dest_ip": {
				"type": "array",
				"items": {"type": ["string", "null"]}
			},
			"longitude": {
				"type": "array",
				"items": {"type": ["number", "null"]}
			},
			"latitude": {
				"type": "array",
				"items": {"type": ["number", "null"]}
			},
			"label": {
				"type": ["string", "number", "null"]
			}
		},
		"required": [
			"uuid",
			"timestamp",
			"amount",
			"source_ip",
			"dest_ip",
			"longitude",
			"latitude"
		]
	}

	def __init__(self):
		# Load and validate configuration using shared loader utility
		self.config = load_and_validate_json_file(self.CONFIG_PATH, self.CONFIG_SCHEMA)
		# Porta su cui il Preparation System ascolta richieste dall'Ingestion System
		# Deve corrispondere a ingestion_system_configuration.json -> preparationSystemAddress.port
		self.port = 5003

		self.io = JsonIO({"/process": self.RAW_SESSION_SCHEMA}, listening_port=self.port)
		self.corrector = DataCorrector(float(self.config["maxTransactionsAmount"]))
		self.extractor = FeatureExtractor(self.config["extractedFeatures"])

	@staticmethod
	def _parse_address(addr_str: str) -> Address:
		if not addr_str or ":" not in addr_str:
			raise ValueError(f"Invalid address format: {addr_str}")
		host, port_str = addr_str.split(":", 1)
		return Address(host, int(port_str))

	def _route_features(self, features: dict):
		"""Route extracted features to the correct downstream system."""
		if self.config["developmentPhase"]:
			target = self._parse_address(self.config["segregationSystemAddress"])
			endpoint = "api/prepared-session"
		else:
			target = self._parse_address(self.config["classificationSystemAddress"])
			endpoint = "api/features"

		print(f"[PreparationSystem] Sending prepared data to {target} ({endpoint})...")
		ok = self.io.send(features, target, endpoint)
		if not ok:
			print("[PreparationSystem] Failed to send prepared data.")

	def run(self):
		print(f"[PreparationSystem] Listening on port {self.port}. Development phase: {self.config['developmentPhase']}")

		while True:
			data = self.io.receive("/process")
			if data is None:
				continue

			try:
				session = RawSession(**data)
			except TypeError as e:
				print(f"[PreparationSystem] Invalid RawSession received: {e}")
				continue

			print(f"[PreparationSystem] Received RawSession {session.uuid}")

			# First handle missing samples, then clip absolute outliers
			session = self.corrector.correct_missing_samples(session)
			session = self.corrector.correct_absolute_outiers(session)

			features = self.extractor.extract_features(session)
			print(f"[PreparationSystem] Extracted features for {session.uuid}: {features}")

			self._route_features(features)


if __name__ == "__main__":
	system = PreparationSystem()
	system.run()

