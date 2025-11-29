from typing import Dict, Any
from shared.jsonio import JsonIO
from ingestion_system.ingestion_system_configuration import IngestionSystemConfiguration
from ingestion_system.raw_session import RawSession
from ingestion_system.raw_session_db import RawSessionDB
from ingestion_system.flow_analysis import FlowAnalysis


class IngestionSystemController:
    def __init__(self):
        self.config = IngestionSystemConfiguration()
        self.db = RawSessionDB()
        self.io = JsonIO()
        self.analysis = FlowAnalysis()
        self.is_evaluation = True
        self.phase_counter = 0

    def run(self, record: dict) -> Dict[str, Any]:
        uuid = record.get('uuid')
        if not uuid: return {"error": "Missing UUID"}

        # 1. Store the partial record (Horizontal Aggregation)
        self.db.store(record)

        # 2. Check if we have all 3 parts (Transaction + Network + Location)
        # We do NOT check for 10 samples here, just the presence of the 3 system parts.
        raw_session = self.db.get_complete_session(uuid)

        if not raw_session:
            return {"status": "Accumulating", "uuid": uuid}

        print(f"[Controller] Session {uuid} has all 3 parts. Processing...")

        # 4. Remove from Buffer (Ref: "empty the buffer once the raw session is created" )
        self.db.remove(uuid)

        # 5. Validate (Mark Missing Samples)
        # This is where we check if we actually have 10 samples or if the data is too sparse.
        if not self.analysis.mark_missing_samples(raw_session, self.config):
            print("[Controller] Session Discarded (Too many missing samples)")
            return {"status": "Discarded", "reason": "Data Quality"}

        # 6. Phase Logic
        self._handle_phase_logic(raw_session)

        # 7. Send
        self.io.send(vars(raw_session), self.config.preparation_system_address, "process")

        return {"status": "Processed", "phase": "EVAL" if self.is_evaluation else "PROD"}

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