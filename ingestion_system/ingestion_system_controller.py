from shared.jsonio import JsonIO
from ingestion_system.ingestion_system_configuration import IngestionSystemConfiguration
from ingestion_system.raw_session import RawSession
from ingestion_system.raw_session_db import RawSessionDB
from ingestion_system.flow_analysis import FlowAnalysis
from dataclasses import asdict


class IngestionSystemController:
    LISTENING_PORT = 6969
    RECORD_SCHEMA = {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": [
                    "transaction_data",
                    "network_data",
                    "location_data",
                    "label"
                ]
            },

            "timestamp": {
                "type": ["number", "string"]
            },
            "amount": {
                "type": "number"
            },
            "source_ip": {
                "type": "string",
                "format": "ipv4"
            },
            "dest_ip": {
                "type": "string",
                "format": "ipv4"
            },
            "latitude": {
                "type": "number",
                "minimum": -90,
                "maximum": 90
            },
            "longitude": {
                "type": "number",
                "minimum": -180,
                "maximum": 180
            },
            "label": {
                "type": "string",
            }
        },
        # Only 'type' is mandatory
        "required": ["type"],
    }

    def __init__(self):
        self.config = IngestionSystemConfiguration()
        self.db = RawSessionDB()
        self.io = JsonIO({"/api/record": self.RECORD_SCHEMA}, listening_port=self.LISTENING_PORT)
        self.analysis = FlowAnalysis()
        self.is_evaluation = True
        self.phase_counter = 0

    def run(self):
        raw_session = None
        while raw_session is None:
            json_record = self.io.receive("api/record")

            uuid = json_record['uuid']
            if not uuid:
                continue

            self.db.store(json_record)

            raw_session = self.db.get_complete_session(uuid)

        print(f"[Controller] Session {raw_session.uuid} has all 3 parts. Processing...")

        # 4. Remove from Buffer (Ref: "empty the buffer once the raw session is created" )
        self.db.remove(raw_session.uuid)

        # 5. Validate (Mark Missing Samples)
        # This is where we check if we actually have 10 samples or if the data is too sparse.
        if not self.analysis.mark_missing_samples(raw_session, self.config):
            print("[Controller] Session Discarded (Too many missing samples)")
            return

        # 6. Phase Logic
        self._handle_phase_logic(raw_session)

        # 7. Send
        self.io.send(asdict(raw_session), self.config.preparation_system_address, "process")

    def _handle_phase_logic(self, session: RawSession):
        limit = self.config.evaluation_phase_limit if self.is_evaluation else self.config.production_phase_limit
        print(f"[Phase] {'EVAL' if self.is_evaluation else 'PROD'} ({self.phase_counter + 1}/{limit})")

        if self.is_evaluation and session.label is not None:
            self.io.send({"uuid": session.uuid, "label": session.label},
                         self.config.evaluation_system_address, "evaluate")

        self.phase_counter += 1
        if self.phase_counter >= limit:
            self.is_evaluation = not self.is_evaluation
            self.phase_counter = 0
            print(f">>> SWITCH PHASE TO {'EVAL' if self.is_evaluation else 'PROD'} <<<")


if __name__ == "__main__":
    controller = IngestionSystemController()
    controller.run()
