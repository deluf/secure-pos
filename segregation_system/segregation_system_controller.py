"""
...
"""
import os
import random
import sys
import time
from random import randint
from dataclasses import asdict

import json
import jsonschema
from jsonschema import validate
from werkzeug.datastructures import FileStorage

from shared.systemsio import SystemsIO, Endpoint
from shared.address import Address
from shared.attack_risk_level import AttackRiskLevel

from segregation_system.data_balancing_model import DataBalancingModel
from segregation_system.data_balancing_view import DataBalancingView
from segregation_system.data_coverage_model import DataCoverageModel
from segregation_system.data_coverage_view import DataCoverageView
from segregation_system.data_splitter import DataSplitter
from shared.feature import Feature
from segregation_system.prepared_sessions_db import PreparedSessionsDB, PreparedSession

# Simulate the preparation system sending prepared sessions #
from faker import Faker
fake = Faker()
def SIMULATE_INCOMING_PREPARED_SESSIONS(self, received_sessions):
    dummy_session = PreparedSession(
        f"{received_sessions}",
        round(random.uniform(1, 60), 2),
        round(random.uniform(50, 500), 2),
        float(fake.longitude()),
        float(fake.latitude()),
        randint(0, 2 ** 32 - 1),
        randint(0, 2 ** 32 - 1),
        random.choice(list(AttackRiskLevel))
    )
    self.io.send_json(
        Address("127.0.0.1", 3000),
        "/prepared-session",
        asdict(dummy_session)
    )
    time.sleep(1)
# End simulation #

class SegregationSystemController:
    """
    ...
    """

    def __init__(self):
        self.configuration = self._json_load_and_validate(
            "configuration.json", "schemas/configuration.schema.json")
        self.io = SystemsIO(
            [Endpoint("/prepared-session", "schemas/prepared_session.schema.json"), Endpoint("/csv")],
            self.configuration["port"]
        )
        self.db = PreparedSessionsDB()
        self.splitter = DataSplitter(
            self.configuration["trainSplitPercentage"],
            self.configuration["testSplitPercentage"],
            self.configuration["validationSplitPercentage"]
        )
        self.service_flag = bool(self.configuration["serviceFlag"])

    @staticmethod
    def _json_load_and_validate(json_path: str, schema_path: str):
        try:
            with open(json_path, encoding="utf-8") as configuration_file:
                data = json.load(configuration_file)
            with open(schema_path, encoding="utf-8") as schema_file:
                schema = json.load(schema_file)
            validate(instance=data, schema=schema)
            return data

        except FileNotFoundError:
            print(f"[Controller] File not found: {json_path} or {schema_path}")
        except jsonschema.exceptions.ValidationError as e:
            print(f"[Controller] {json_path} does not follow {schema_path} specifications: {e.message}")
        except json.JSONDecodeError as e:
            print(f"[Controller] Invalid JSON syntax in {json_path}: {e}")
        sys.exit(-1)

    def run(self):
        """
        ...
        """
        received_sessions = 0
        minimum_number_of_sessions = int(self.configuration["minimumNumberOfSessions"])
        while received_sessions < minimum_number_of_sessions:
            # Simulate the preparation system sending prepared sessions #
            SIMULATE_INCOMING_PREPARED_SESSIONS(self, received_sessions) # NO RECORDS
            # End simulation #

            prepared_session_data = self.io.receive("/prepared-session")

            self.db.store(PreparedSession(**prepared_session_data))
            received_sessions += 1

        sessions = self.db.get_all()
        self.db.delete_all()
        print(f"[Controller] Loaded {len(sessions)} sessions from database")

        if not self.service_flag:
            session_counts = {}
            for session in sessions:
                session_counts[session.label] = session_counts.get(session.label, 0) + 1
            model = DataBalancingModel(
                balancing_tolerance=self.configuration["balancingTolerance"],
                target_sessions_per_class=self.configuration["targetSessionsPerClass"],
                session_counts=session_counts
            )
            DataBalancingView().build_chart(model)
            input("[Controller] Write the decision to 'input/data_balancing_result.json', then press <ENTER>...")
            # FIXME: ...

            features_samples = {
                Feature.MAD_TIMESTAMPS: [s.mad_timestamps for s in sessions],
                Feature.MAD_AMOUNTS: [s.mad_amounts for s in sessions],
                Feature.MEDIAN_LONGITUDE: [s.median_longitude for s in sessions],
                Feature.MEDIAN_LATITUDE: [s.median_latitude for s in sessions],
                Feature.MEDIAN_SOURCE_IP: [s.median_source_ip for s in sessions],
                Feature.MEDIAN_DESTINATION_IP: [s.median_destination_ip for s in sessions],
            }
            model = DataCoverageModel(features_samples)
            DataCoverageView().build_chart(model)
            input("[Controller] Write the decision to 'input/data_coverage_result.json', then press <ENTER>...")

            # FIXME: ...
        else:
            print("[Controller] Simulated user decision ...")
            # FIXME: ...

        self.splitter.split(sessions)

        time.sleep(5)

        self.io.send_file(Address("127.0.0.1", 3000), "/csv", "output/train_set.csv")
        time.sleep(2)
        self.io.send_file(Address("127.0.0.1", 3000), "/csv", "output/validation_set.csv")
        time.sleep(2)
        self.io.send_file(Address("127.0.0.1", 3000), "/csv", "output/test_set.csv")

        time.sleep(5)

        files_to_receive = ["train_set.csv", "validation_set.csv", "test_set.csv"]
        while files_to_receive:
            received_file = self.io.receive("/csv")
            if received_file not in files_to_receive:
                continue
            files_to_receive.remove(received_file)

if __name__ == "__main__":
    controller = SegregationSystemController()
    controller.run()
