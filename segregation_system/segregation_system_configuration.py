
import json

class Address:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port

class SegregationSystemConfiguration:
    def __init__(self):
        with open('segregation_system_configuration.json', encoding='utf-8') as configuration_file:
            configuration = json.load(configuration_file)
        self.port = configuration['port']
        self.minimum_number_of_sessions = configuration['minimumNumberOfSessions']
        self.messaging_system_address = configuration['messagingSystemAddress']
        self.development_system_address = configuration['developmentSystemAddress']
        self.train_split_percentage = configuration['trainSplitPercentage']
        self.validation_split_percentage = configuration['validationSplitPercentage']
        self.test_split_percentage = configuration['testSplitPercentage']
        self.target_sessions_per_class = configuration['targetSessionsPerClass']
        self.balancing_tolerance = configuration['balancingTolerance']

    def get_port(self) -> int:
        return self.port

    def get_minimum_number_of_sessions(self) -> int:
        return self.minimum_number_of_sessions

    def get_messaging_system_address(self) -> Address:
        return self.messaging_system_address

    def get_development_system_address(self) -> Address:
        return self.development_system_address

    def get_train_split_percentage(self) -> float:
        return self.train_split_percentage

    def get_validation_split_percentage(self) -> float:
        return self.validation_split_percentage

    def get_test_split_percentage(self) -> float:
        return self.test_split_percentage

    def get_target_sessions_per_class(self) -> int:
        return self.target_sessions_per_class

    def get_balancing_tolerance(self) -> float:
        return self.balancing_tolerance
