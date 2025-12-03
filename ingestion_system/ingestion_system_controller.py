from shared.systemsio import SystemsIO, Endpoint
from shared.loader import load_and_validate_json_file
from ingestion_system.raw_session import RawSession
from ingestion_system.raw_session_db import RawSessionDB
from ingestion_system.flow_analysis import FlowAnalysis
from dataclasses import asdict
from shared.address import Address


class IngestionSystemController:
    LOCAL_CONFIG_PATH = "ingestion_system/ingestion_system_configuration.json"
    SHARED_CONFIG_PATH = "shared/shared_config.json"
    RECORD_SCHEMA = "ingestion_system/record.schema.json"
    LOCAL_CONFIG_SCHEMA = "ingestion_system/config.schema.json"
    SHARED_CONFIG_SCHEMA = "shared/shared_config.schema.json"

    def __init__(self):
        self.local_config = load_and_validate_json_file(self.LOCAL_CONFIG_PATH, self.LOCAL_CONFIG_SCHEMA)
        self.shared_config = load_and_validate_json_file(self.SHARED_CONFIG_PATH, self.SHARED_CONFIG_SCHEMA)
        self.ingestion_system_address = Address(**self.shared_config['addresses']['ingestionSystem'])
        self.preparation_system_address = Address(**self.shared_config['addresses']['preparationSystem'])
        self.evaluation_system_address = Address(**self.shared_config['addresses']['evaluationSystem'])
        self.db = RawSessionDB()
        self.io = SystemsIO([Endpoint("/api/record", self.RECORD_SCHEMA)], port=self.ingestion_system_address.port)
        self.analysis = FlowAnalysis()
        self.is_evaluation = True
        self.phase_counter = 0

    def run(self):
        raw_session = None
        while raw_session is None:
            json_record = self.io.receive("/api/record")

            uuid = json_record.get('uuid')
            if not uuid:
                continue

            self.db.store(json_record)
            raw_session = self.db.get_session(uuid, self.local_config['minimumRecords'])

        self.db.remove(raw_session.uuid)

        if not self.analysis.mark_missing_samples(raw_session, self.local_config["missingSamplesThreshold"]):
            return

        self._handle_phase(raw_session)

        self.io.send_json(self.preparation_system_address, "/process", asdict(raw_session))

    def _handle_phase(self, session: RawSession):
        limit = self.shared_config['systemPhase']['evaluationPhaseWindow'] if self.is_evaluation else self.shared_config['systemPhase']['productionPhaseWindow']

        if self.is_evaluation and session.label is not None:
            self.io.send_json(
                self.evaluation_system_address,
                "evaluate",
                {"uuid": session.uuid, "/label": session.label}
            )

        self.phase_counter += 1
        if self.phase_counter >= limit:
            self.is_evaluation = not self.is_evaluation
            self.phase_counter = 0


if __name__ == "__main__":
    controller = IngestionSystemController()
    controller.run()
