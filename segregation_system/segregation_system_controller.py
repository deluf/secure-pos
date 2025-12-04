"""
The controller module for the segregation system
"""

import random
import time
from random import randint
from dataclasses import asdict
from typing import Final

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
import uuid
def SIMULATE_INCOMING_PREPARED_SESSIONS(self):
    dummy_session = PreparedSession(
        uuid.uuid4().hex,
        round(random.uniform(1, 60), 2),
        round(random.uniform(50, 500), 2),
        float(fake.longitude()),
        float(fake.latitude()),
        randint(0, 2 ** 32 - 1),
        randint(0, 2 ** 32 - 1),
        random.choice(list(AttackRiskLevel))
    )
    self.io.send_json(
        Address("127.0.0.1", 8003),
        "/prepared-session",
        asdict(dummy_session)
    )
    time.sleep(1)
# End simulation #

class SegregationSystemController:
    """
    ...
    """

    OUTPUT_DIR: Final[str] = "output"

    def __init__(self) -> None:
        """
        ...
        """
        self.configuration = load_and_validate_json_file(
            "configuration.json",
            "schemas/configuration.schema.json"
        )
        self.configuration |= load_and_validate_json_file(
            "../shared/json/shared_config.json",
            "../shared/json/shared_config.schema.json"
        )

        self.service_flag = bool(self.configuration["serviceFlag"])
        self.development_system_address = Address(
            self.configuration["addresses"]["developmentSystem"]["ip"],
            self.configuration["addresses"]["developmentSystem"]["port"]
        )

        self.io = SystemsIO(
            # FIXME: Remove the /calibration-sets test endpoint
            [Endpoint("/prepared-session", "schemas/prepared_session.schema.json"), Endpoint("/calibration-sets")],
            self.configuration["addresses"]["segregationSystem"]["port"],
        )
        self.sessions_db = PreparedSessionsDB()
        self.splitter = DataSplitter(
            self.configuration["trainSplitPercentage"],
            self.configuration["testSplitPercentage"],
            self.configuration["validationSplitPercentage"],
            self.OUTPUT_DIR
        )
        self.data_balancing_view = DataBalancingView(self.OUTPUT_DIR)
        self.data_coverage_view = DataCoverageView(self.OUTPUT_DIR)

    def run(self, requested_sessions: dict[AttackRiskLevel, int] = None) -> None:
        """
        ...
        """
        received_sessions = self.sessions_db.count()
        print(f"[Controller] Initially loaded {received_sessions} sessions from the database")
        minimum_number_of_sessions = int(self.configuration["minimumNumberOfSessions"])
        while True:
            # Exit conditions check
            if requested_sessions:
                if sum(requested_sessions.values()) <= 0:
                    break
            else:
                if received_sessions >= minimum_number_of_sessions:
                    break

            print(f"[DEBUG] Requested sessions: {requested_sessions}")
            print(f"[DEBUG] Received sessions: {received_sessions}")

            # Simulate the preparation system sending prepared sessions #
            SIMULATE_INCOMING_PREPARED_SESSIONS(self)
            # End simulation #

            prepared_session_data = self.io.receive("/prepared-session")
            prepared_session = PreparedSession(**prepared_session_data)

            if requested_sessions:
                if requested_sessions.get(prepared_session.label, 0) <= 0:
                    # Ignore the session, the user does not need it
                    continue
                requested_sessions[prepared_session.label] -= 1
            else:
                received_sessions += 1
            self.sessions_db.store(prepared_session)

        sessions = self.sessions_db.get_all()

        model = DataBalancingModel(
            balancing_tolerance=self.configuration["balancingTolerance"],
            target_sessions_per_class=self.configuration["targetSessionsPerClass"],
            sessions=sessions
        )
        self.data_balancing_view.build_report(model)
        requested_sessions = self.data_balancing_view.read_user_input(self.service_flag)
        if requested_sessions:
            self.run(requested_sessions)
            return

        model = DataCoverageModel(sessions)
        self.data_coverage_view.build_report(model)
        requested_sessions = self.data_coverage_view.read_user_input(self.service_flag)
        if requested_sessions:
            self.run(requested_sessions)
            return

        splits = self.splitter.split(sessions)
        # FIXME: Actually use the dev system address
        self.io.send_files(Address("127.0.0.1", 8003), "/calibration-sets", splits)
        self.sessions_db.delete_all()
        self.splitter.delete(splits)

if __name__ == "__main__":
    controller = SegregationSystemController()
    controller.run()
