import random
import sys
import time
from random import randint

import json
import jsonschema
from jsonschema import validate
from dataclasses import asdict
from faker import Faker

from shared.address import Address
from shared.attack_risk_level import AttackRiskLevel
from shared.jsonio import JsonIO

fake = Faker()

from segregation_system.data_balancing_model import DataBalancingModel
from segregation_system.data_balancing_view import DataBalancingView
from segregation_system.data_coverage_model import DataCoverageModel
from segregation_system.data_coverage_view import DataCoverageView
from segregation_system.data_splitter import DataSplitter
from shared.feature import Feature
from segregation_system.prepared_sessions_db import PreparedSessionsDB, PreparedSession

class SegregationSystemController:

    def __init__(self):
        self.configuration = self._json_load_and_validate("configuration")
        with open("prepared_session.schema.json", encoding="utf-8") as schema_file:
            schema = json.load(schema_file)
        self.io = JsonIO(
            {"/prepared-session": schema},
            self.configuration["port"]
        )
        self.db = PreparedSessionsDB()
        self.splitter = DataSplitter(
            self.configuration["trainSplitPercentage"],
            self.configuration["testSplitPercentage"],
            self.configuration["validationSplitPercentage"]
        )

    def _json_load_and_validate(self, filename):
        try:
            with open(f"{filename}.json", encoding="utf-8") as configuration_file:
                data = json.load(configuration_file)
            with open(f"{filename}.schema.json", encoding="utf-8") as schema_file:
                schema = json.load(schema_file)
            validate(instance=data, schema=schema)
            return data

        except FileNotFoundError:
            print(f"File not found: {filename}.json or {filename}.schema.json")
        except jsonschema.exceptions.ValidationError as e:
            print(f"{filename}.json does not follow {filename}.json.schema specifications: {e.message}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON syntax in {filename}.json: {e}")
        sys.exit(-1)

    def run(self):
        time.sleep(3)
        received_records = 0
        minimum_number_of_records = int(self.configuration["minimumNumberOfSessions"])
        while received_records < minimum_number_of_records:
            # Simulate the preparation system sending prepared sessions #
            dummy_session = PreparedSession(
                f"{received_records}",
                round(random.uniform(1, 60), 2),
                round(random.uniform(50, 500), 2),
                float(fake.longitude()),
                float(fake.latitude()),
                randint(0, 2**32-1),
                randint(0, 2**32-1),
                random.choice(list(AttackRiskLevel))
            )
            self.io.send(
                asdict(dummy_session),
                Address("127.0.0.1", 3000),
                "/prepared-session"
            )
            time.sleep(1)
            # End simulation #

            received_prepared_session_json = self.io.receive("/prepared-session")
            if received_prepared_session_json is None:
                print("Queue is empty or timed-out...")
                return
            print(f"Received prepared session: {received_prepared_session_json}")

            try:
                self.db.store(PreparedSession(**received_prepared_session_json))
                received_records += 1
            except Exception as e:
                print(f"Error storing record in database: {e}")

        sessions = self.db.getAll()
        print(f"Loaded {len(sessions)} sessions from database")

        session_counts = {}
        for session in sessions:
            session_counts[session.label] = session_counts.get(session.label, 0) + 1

        model = DataBalancingModel(
            balancing_tolerance=self.configuration["balancingTolerance"],
            target_sessions_per_class=self.configuration["targetSessionsPerClass"],
            session_counts=session_counts
        )
        DataBalancingView().build_chart(model)

        print("\n Data balancing report saved to 'data_balancing_report.png'")
        print(" Write the decision to 'data_balancing_result.json', then press <ENTER>")
        input()

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

        print("\n Data coverage report saved to 'data_coverage_report.png'")
        print(" Write the decision to 'data_coverage_result.json', then press <ENTER>")
        input()

        self.splitter.split(sessions)

        print(" Data splitting complete")

        # FIXME: SEND

if __name__ == "__main__":
    controller = SegregationSystemController()
    controller.run()
