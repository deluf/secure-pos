from development_system.neural_network import NeuralNetwork
from development_system.test_controller import TestController
from development_system.training_controller import TrainingController
from development_system.validation_controller import ValidationController
from shared.systemsio import SystemsIO, Endpoint
from shared.loader import load_and_validate_json_file
from shared.address import Address


class DevelopmentSystemController:
    CONFIG_PATH = "development_system/input/development_system_configuration.json"
    CONFIG_SCHEMA_PATH = "development_system/schema/configuration.schema.json"
    SHARED_CONFIG_PATH = "shared/json/shared_config.json"
    SHARED_CONFIG_SCHEMA_PATH = "shared/json/shared_config.schema.json"
    PROCESS_ENDPOINT = "/calibration-sets"

    def __init__(self):
        self.config = load_and_validate_json_file(self.CONFIG_PATH,
                                                  self.CONFIG_SCHEMA_PATH)
        self.shared_config = load_and_validate_json_file(self.SHARED_CONFIG_PATH,
                                                         self.SHARED_CONFIG_SCHEMA_PATH)
        self.service_flag = self.shared_config["serviceFlag"]
        prep_cfg = self.shared_config["addresses"]["developmentSystem"]
        self.io = SystemsIO([Endpoint(self.PROCESS_ENDPOINT)],
                            port=int(prep_cfg["port"])
                            )
        self.classification_address = Address(
            self.shared_config["addresses"]["classificationSystem"]["ip"],
            int(self.shared_config["addresses"]["classificationSystem"]["port"])
        )
        self.neural_network = NeuralNetwork(self.config["hiddenLayerSizeRange"],
                                            self.config["hiddenNeuronPerLayerRange"])
        self.neural_network.number_iterations = 0
        self.valid_classifier_exists = False
        self.iterations_fine = False
        self.valid_classifier_id = None
        # Init controllers
        self.training_ctrl = TrainingController(self)
        self.validation_ctrl = ValidationController(self)
        self.test_ctrl = TestController(self)

    def run(self):
        while True:
            # Receive Calibration Set
            files = self.io.receive(self.PROCESS_ENDPOINT)
            train_set = next((f for f in files if "train_set" in f), None)
            validation_set = next((f for f in files if "validation_set" in f), None)
            test_set = next((f for f in files if "test_set" in f), None)
            print("[System] Calibration Sets received.")

            print("\n[System] --- DEVELOPMENT FLOW START ---")
            # Loop: while no valid classifier
            while not self.valid_classifier_exists:
                self.iterations_fine = False
                self.neural_network.number_iterations = 0

                # 1. Training Phase
                print("\n[System] --- TRAINING PHASE START ---")
                # Loop: while number of iterations not fine
                while not self.iterations_fine:
                    self.training_ctrl.run(train_set)
                print("\n[System] --- TRAINING PHASE END ---")

                # 2. Validation Phase
                print("\n[System] --- VALIDATION PHASE START ---")
                self.validation_ctrl.run(train_set, validation_set)
                print("\n[System] --- VALIDATION PHASE END ---")

            # 3. Test Phase
            print("\n[System] --- TEST PHASE START ---")
            test_passed = self.test_ctrl.run(test_set)
            print("\n[System] --- TEST PHASE END ---")
            # Reset for possible re-executions
            self.valid_classifier_exists = False
            self.iterations_fine = False
            self.valid_classifier_id = None
            self.validation_ctrl.ongoing_validation = False
            if not self.service_flag and test_passed:
                break
            if not test_passed:
                self.config = load_and_validate_json_file(self.CONFIG_PATH,
                                                          self.CONFIG_SCHEMA_PATH)
            self.neural_network.__init__(self.config["hiddenLayerSizeRange"],
                                         self.config["hiddenNeuronPerLayerRange"])
            self.neural_network.number_iterations = 0

if __name__ == "__main__":
    controller = DevelopmentSystemController()
    controller.run()
