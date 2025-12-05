from shared.message_counter import PhaseMessageCounter
from shared.systemsio import SystemsIO, Endpoint
from shared.loader import load_and_validate_json_file
from ingestion_system.raw_session import RawSession
from ingestion_system.raw_session_db import RawSessionDB
from ingestion_system.flow_analysis import FlowAnalysis
from dataclasses import asdict
from shared.address import Address


class IngestionSystemController:
    LOCAL_CONFIG_PATH = "ingestion_system/json/ingestion_system_configuration.json"
    SHARED_CONFIG_PATH = "shared/json/shared_config.json"
    RECORD_SCHEMA = "ingestion_system/json/record.schema.json"
    LOCAL_CONFIG_SCHEMA = "ingestion_system/json/config.schema.json"
    SHARED_CONFIG_SCHEMA = "shared/json/shared_config.schema.json"

    INPUT_RECORD_ENDPOINT = "/record"
    EVALUATION_SYSTEM_ENDPOINT = "/actual-label"
    PREPARATION_SYSTEM_ENDPOINT = "/process"

    def __init__(self):
        self.local_config = load_and_validate_json_file(self.LOCAL_CONFIG_PATH, self.LOCAL_CONFIG_SCHEMA)
        self.shared_config = load_and_validate_json_file(self.SHARED_CONFIG_PATH, self.SHARED_CONFIG_SCHEMA)
        self.ingestion_system_address = Address(**self.shared_config['addresses']['ingestionSystem'])
        self.preparation_system_address = Address(**self.shared_config['addresses']['preparationSystem'])
        self.evaluation_system_address = Address(**self.shared_config['addresses']['evaluationSystem'])
        self.db = RawSessionDB()
        endpoints = [Endpoint(self.INPUT_RECORD_ENDPOINT, self.RECORD_SCHEMA)]
        self.io = SystemsIO(endpoints, port=self.ingestion_system_address.port)
        self.analysis = FlowAnalysis()
        evaluation_window = self.shared_config['systemPhase']['evaluationPhaseWindow']
        production_window = self.shared_config['systemPhase']['productionPhaseWindow']
        self.counter = PhaseMessageCounter("state/ingestion_counter.json", evaluation_window, production_window)

    def run(self):
        raw_session = None
        while raw_session is None:
            json_record = self.io.receive(self.INPUT_RECORD_ENDPOINT)

            uuid = json_record.get('uuid')
            if not uuid:
                continue

            self.db.store(json_record)
            raw_session = self.db.get_session(uuid, self.local_config['minimumRecords'])

        self.db.remove(raw_session.uuid)

        if not self.analysis.mark_missing_samples(raw_session, self.local_config["missingSamplesThreshold"]):
            return

        if self.counter.register_message():
            self.io.send_json(
                self.evaluation_system_address,
                self.EVALUATION_SYSTEM_ENDPOINT,
                {"uuid": raw_session.uuid, "label": raw_session.label}
            )

        self.io.send_json(self.preparation_system_address, self.PREPARATION_SYSTEM_ENDPOINT, asdict(raw_session))


if __name__ == "__main__":
    controller = IngestionSystemController()
    controller.run()
