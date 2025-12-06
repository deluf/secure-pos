from ingestion_system.raw_session import RawSession
from requests import exceptions as requests_exceptions
from shared.systemsio import SystemsIO, Endpoint
from shared.address import Address
from shared.loader import load_and_validate_json_file

from preparation_system.data_corrector import DataCorrector
from preparation_system.feature_extractor import FeatureExtractor


class PreparationSystem:
	CONFIG_PATH = "preparation_system/json/config.json"
	CONFIG_SCHEMA_PATH = "preparation_system/json/config_schema.json"
	SHARED_CONFIG_PATH = "shared/json/shared_config.json"
	SHARED_CONFIG_SCHEMA_PATH = "shared/json/shared_config.schema.json"
	RAW_SESSION_SCHEMA_PATH = "preparation_system/json/raw_session.schema.json"
	PROCESS_ENDPOINT = "/process"

	def __init__(self):
		self.config = load_and_validate_json_file(self.CONFIG_PATH, self.CONFIG_SCHEMA_PATH)
		self.shared_config = load_and_validate_json_file(
			self.SHARED_CONFIG_PATH,
			self.SHARED_CONFIG_SCHEMA_PATH
		)

		prep_cfg = self.shared_config["addresses"]["preparationSystem"]
		self.io = SystemsIO(
			[Endpoint(self.PROCESS_ENDPOINT, self.RAW_SESSION_SCHEMA_PATH)],
			port=int(prep_cfg["port"]),
			host=prep_cfg["ip"]
		)

		self.classification_address = Address(
			self.shared_config["addresses"]["classificationSystem"]["ip"],
			int(self.shared_config["addresses"]["classificationSystem"]["port"])
		)
		self.segregation_address = Address(
			self.shared_config["addresses"]["segregationSystem"]["ip"],
			int(self.shared_config["addresses"]["segregationSystem"]["port"])
		)

		self.corrector = DataCorrector(float(self.config["maxTransactionsAmount"]))
		self.extractor = FeatureExtractor(self.config["extractedFeatures"])

	def run(self):
		prep_cfg = self.shared_config["addresses"]["preparationSystem"]
		print(
			f"[PreparationSystem] Listening on {prep_cfg['ip']}:{prep_cfg['port']}. "
			f"Production phase: {self.shared_config["systemPhase"]["productionPhase"]}"
		)

		while True:
			data = self.io.receive(self.PROCESS_ENDPOINT)
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

			if self.shared_config["systemPhase"]["productionPhase"]:
				target = self.classification_address
				endpoint = "/features"
			else:
				target = self.segregation_address
				endpoint = "/prepared-session"

			print(f"[PreparationSystem] Sending prepared data to {target} ({endpoint})...")
			try:
				SystemsIO.send_json(target, endpoint, features)
			except requests_exceptions.RequestException as exc:
				print(f"[PreparationSystem] Failed to send prepared data: {exc}")

			if self.shared_config["serviceFlag"]:
				break


if __name__ == "__main__":
	system = PreparationSystem()
	system.run()

