from shared.jsonio import JsonIO
from shared.loader import load_and_validate_json_file
from ingestion_system.raw_session import RawSession
from ingestion_system.raw_session_db import RawSessionDB
from ingestion_system.flow_analysis import FlowAnalysis
from dataclasses import asdict
from shared.address import Address


class IngestionSystemController:
    CONFIG_PATH = "ingestion_system/ingestion_system_configuration.json"
    RECORD_SCHEMA = {
        "type": "object",
        "properties": {
            # 'type' remains a single scalar string to identify the batch/record category
            "type": {
                "type": "string",
                "enum": [
                    "transaction_data",
                    "network_data",
                    "location_data",
                    "label"
                ]
            },

            # ARRAYS start here
            "timestamp": {
                "type": "array",
                "items": {
                    "type": ["number", "string"]
                }
            },
            "amount": {
                "type": "array",
                "items": {
                    "type": "number"
                }
            },
            "source_ip": {
                "type": "array",
                "items": {
                    "type": "string",
                    "format": "ipv4"
                }
            },
            "dest_ip": {
                "type": "array",
                "items": {
                    "type": "string",
                    "format": "ipv4"
                }
            },
            "latitude": {
                "type": "array",
                "items": {
                    "type": "number",
                    "minimum": -90,
                    "maximum": 90
                }
            },
            "longitude": {
                "type": "array",
                "items": {
                    "type": "number",
                    "minimum": -180,
                    "maximum": 180
                }
            },

            "label": {
                "type": "string",
            }
        },
        "required": ["type"],
    }
    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "port": {
                "type": "integer",
                "minimum": 1,
                "maximum": 65535
            },
            "minimumRecords": {
                "type": "integer",
                "minimum": 0
            },
            "missingSamplesThreshold": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
            },
            "evaluationSystemAddress": {
                "type": "object",
                "properties": {
                    "ip": {
                        "type": "string",
                        "format": "ipv4"
                    },
                    "port": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 65535
                    }
                },
                "required": ["ip", "port"]
            },
            "preparationSystemAddress": {
                "type": "object",
                "properties": {
                    "ip": {
                        "type": "string",
                        "format": "ipv4"
                    },
                    "port": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 65535
                    }
                },
                "required": ["ip", "port"]
            },
            "evaluationPhaseWindow": {
                "type": "integer",
                "minimum": 1
            },
            "productionPhaseWindow": {
                "type": "integer",
                "minimum": 1
            }
        },
        "required": [
            "port",
            "minimumRecords",
            "missingSamplesThreshold",
            "evaluationSystemAddress",
            "preparationSystemAddress",
            "evaluationPhaseWindow",
            "productionPhaseWindow"
        ]
    }

    def __init__(self):
        self.config = load_and_validate_json_file(self.CONFIG_PATH, self.CONFIG_SCHEMA)
        self.db = RawSessionDB()
        self.io = JsonIO({"/api/record": self.RECORD_SCHEMA}, listening_port=self.config['port'])
        self.analysis = FlowAnalysis()
        self.is_evaluation = True
        self.phase_counter = 0

    def run(self):
        raw_session = None
        while raw_session is None:
            json_record = self.io.receive("api/record")

            uuid = json_record.get('uuid')
            if not uuid:
                continue

            self.db.store(json_record)

            raw_session = self.db.get_complete_session(uuid, self.config)

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
        self.io.send(asdict(raw_session), Address(**self.config['preparationSystemAddress']), "process")

    def _handle_phase_logic(self, session: RawSession):
        limit = self.config['evaluationPhaseWindow'] if self.is_evaluation else self.config['productionPhaseWindow']
        print(f"[Phase] {'EVAL' if self.is_evaluation else 'PROD'} ({self.phase_counter + 1}/{limit})")

        if self.is_evaluation and session.label is not None:
            self.io.send({"uuid": session.uuid, "label": session.label},
                         Address(**self.config['evaluationSystemAddress']), "evaluate")

        self.phase_counter += 1
        if self.phase_counter >= limit:
            self.is_evaluation = not self.is_evaluation
            self.phase_counter = 0
            print(f">>> SWITCH PHASE TO {'EVAL' if self.is_evaluation else 'PROD'} <<<")


if __name__ == "__main__":
    controller = IngestionSystemController()
    controller.run()
