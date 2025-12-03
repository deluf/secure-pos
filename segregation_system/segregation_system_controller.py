"""
The controller module for the segregation system.
"""
import random
import time
from random import randint
from dataclasses import asdict

from shared.loader import load_and_validate_json_file
from shared.systemsio import SystemsIO, Endpoint
from shared.address import Address
from shared.attack_risk_level import AttackRiskLevel

from segregation_system.data_balancing_model import DataBalancingModel
from segregation_system.data_balancing_view import DataBalancingView
from segregation_system.data_coverage_model import DataCoverageModel
from segregation_system.data_coverage_view import DataCoverageView
from segregation_system.data_splitter import DataSplitter
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
        self.configuration = load_and_validate_json_file(
            "configuration.json", "schemas/configuration.schema.json")
        self.io = SystemsIO(
            # FIXME: Remove the /calibration-sets test endpoint
            [Endpoint("/prepared-session", "schemas/prepared_session.schema.json"), Endpoint("/calibration-sets")],
            self.configuration["port"]
        )
        self.sessions_db = PreparedSessionsDB()
        self.splitter = DataSplitter(
            self.configuration["trainSplitPercentage"],
            self.configuration["testSplitPercentage"],
            self.configuration["validationSplitPercentage"]
        )
        self.service_flag = bool(self.configuration["serviceFlag"])
        self.development_system_address = Address(
            self.configuration["developmentSystemAddress"]["ip"],
            self.configuration["developmentSystemAddress"]["port"]
        )
        # FIXME: Sync the configuration (+ schema) with the actual used parameters

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

            self.sessions_db.store(PreparedSession(**prepared_session_data))
            received_sessions += 1

        sessions = self.sessions_db.get_all()

        model = DataBalancingModel(
            balancing_tolerance=self.configuration["balancingTolerance"],
            target_sessions_per_class=self.configuration["targetSessionsPerClass"],
            sessions=sessions
        )
        DataBalancingView().build_chart(model)

        # Is data balanced?
        if not self.service_flag:
            result = input("[Controller] Is data balanced? (Y/n): \n > ")
            data_balanced = result.lower() == "y"
        else:
            data_balanced = random.choice([True, False])
            print(f"[Controller] Simulated user decision: data {"not " if not data_balanced else " "}balanced")

        # If data is not balanced, how many additional sessions do we need?
        if not data_balanced:
            if not self.service_flag:
                pass
            else:
                pass
            self.run()

        model = DataCoverageModel(sessions)
        DataCoverageView().build_chart(model)

        # Are features well distributed?
        if not self.service_flag:
            result = input("[Controller] Are features well distributed? (Y/n): \n > ")
            features_well_distributed = result.lower() == "y"
        else:
            features_well_distributed = random.choice([True, False])
            print(f"[Controller] Simulated user decision: features {"not " if not features_well_distributed else " "}distributed")

        # If features are not well distributed, how many additional sessions do we need?
        if not features_well_distributed:
            if not self.service_flag:
                pass
            else:
                pass
            self.run()

        splits = self.splitter.split(sessions)
        # FIXME: Actually use the dev system address
        self.io.send_files(Address("127.0.0.1", 3000), "/calibration-sets", splits)
        self.sessions_db.delete_all()
        self.splitter.delete(splits)

if __name__ == "__main__":
    controller = SegregationSystemController()
    controller.run()
