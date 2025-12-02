from shared.systemsio import SystemsIO, Endpoint
from shared.loader import load_and_validate_json_file
from ingestion_system.raw_session import RawSession
from ingestion_system.raw_session_db import RawSessionDB
from ingestion_system.flow_analysis import FlowAnalysis
from dataclasses import asdict
from shared.address import Address


class IngestionSystemController:
    CONFIG_PATH = "ingestion_system/ingestion_system_configuration.json"
    RECORD_SCHEMA = "ingestion_system/record_schema.json"
    CONFIG_SCHEMA = "ingestion_system/config_schema.json"

    def __init__(self):
        self.config = load_and_validate_json_file(self.CONFIG_PATH, self.CONFIG_SCHEMA)
        self.db = RawSessionDB()
        self.io = SystemsIO([Endpoint("/api/record", self.RECORD_SCHEMA)], port=self.config['port'])
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

            raw_session = self.db.get_complete_session(uuid, self.config)

        print(f"[Controller] Session {raw_session.uuid} has all {self.config['minimumRecords']} parts. Processing...")

        self.db.remove(raw_session.uuid)

        if not self.analysis.mark_missing_samples(raw_session, self.config):
            print("[Controller] Session Discarded (Too many missing samples)")
            return

        self._handle_phase_logic(raw_session)

        self.io.send_json(Address(**self.config['preparationSystemAddress']), "/process", asdict(raw_session))

    def _handle_phase_logic(self, session: RawSession):
        limit = self.config['evaluationPhaseWindow'] if self.is_evaluation else self.config['productionPhaseWindow']
        print(f"[Phase] {'EVAL' if self.is_evaluation else 'PROD'} ({self.phase_counter + 1}/{limit})")

        if self.is_evaluation and session.label is not None:
            self.io.send_json(Address(**self.config['evaluationSystemAddress']),
                              "evaluate", {"uuid": session.uuid, "/label": session.label})

        self.phase_counter += 1
        if self.phase_counter >= limit:
            self.is_evaluation = not self.is_evaluation
            self.phase_counter = 0
            print(f">>> SWITCH PHASE TO {'EVAL' if self.is_evaluation else 'PROD'} <<<")


if __name__ == "__main__":
    controller = IngestionSystemController()
    controller.run()
