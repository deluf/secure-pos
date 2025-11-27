
import time
import requests
from dataclasses import asdict

from segregation_system.data_balancing_model import DataBalancingModel
from segregation_system.data_balancing_view import DataBalancingView
from segregation_system.data_coverage_model import FeatureSamples, DataCoverageModel
from segregation_system.data_coverage_view import DataCoverageView
from segregation_system.feature import Feature
from segregation_system.prepared_sessions_db import PreparedSessionsDB, PreparedSession
from segregation_system.segregation_system_configuration import SegregationSystemConfiguration
from segregation_system.segregation_system_io import SegregationSystemIO

class SegregationSystemController:

    def __init__(self):
        self.configuration = SegregationSystemConfiguration()
        self.io = SegregationSystemIO(
            self.configuration.get_port(),
            self.configuration.get_messaging_system_address(),
            self.configuration.get_development_system_address()
        )
        self.db = PreparedSessionsDB()

    def run(self):

        received_records = 0
        while received_records < self.configuration.get_minimum_number_of_sessions():

            dummy_session = PreparedSession(f"{received_records}", 1.5, 100.50, 40.7128, "192.168.1.1", "10.0.0.1")
            requests.post(
                'http://127.0.0.1:3000/api/prepared-session',
                json=asdict(dummy_session)
            )

            time.sleep(1)

            received_record = self.io.receive_prepared_session()
            if received_record is None:
                print("Queue is empty...")
                return
            print(f"Main Thread Processed Record: {received_record}")

            self.db.store(received_record)
            received_records += 1

        print("Enough records")

        model = DataBalancingModel(
            balancing_tolerance=self.configuration.get_balancing_tolerance(),
            target_sessions_per_class=self.configuration.get_target_sessions_per_class(),
            normal_risk_sessions=50,
            moderate_risk_sessions=30,
            high_risk_sessions=10
        )
        DataBalancingView().build_chart(model)

        print(" Data balancing report generated")
        print(" Decision (accept/refuse)")
        input(" > ")

        features_samples = [
            FeatureSamples(Feature.MEDIAN_LOCATION, [0.347, 0.829, 0.512, 0.694, 0.271]),
            FeatureSamples(Feature.MEDIAN_DEST_IP, [0.903, 0.127, 0.658, 0.774, 0.492]),
            FeatureSamples(Feature.MEDIAN_TARGET_IP, [0.385, 0.944, 0.261, 0.719, 0.503])
        ]
        model = DataCoverageModel(features_samples)
        DataCoverageView().build_chart(model)

        print(" Data coverage report generated")
        print(" Decision (accept/refuse)")
        input(" > ")

if __name__ == "__main__":
    controller = SegregationSystemController()
    controller.run()
