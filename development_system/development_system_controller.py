from development_system.neural_network import NeuralNetwork
from development_system.test_controller import TestController
from development_system.training_controller import TrainingController
from development_system.validation_controller import ValidationController
from shared.systemsio import SystemsIO, Endpoint
from shared.loader import load_and_validate_json_file


class DevelopmentSystemController:
    CONFIG_PATH = "development_system/input/development_system_configuration.json"
    #TRAIN_PATH = "files/train_set.csv"
    #VALIDATION_PATH = "files/validation_set.csv"
    #TEST_PATH = "files/test_set.csv"

    def __init__(self):
        self.config = load_and_validate_json_file(self.CONFIG_PATH,
                                                  "development_system/schema/configuration.schema.json")
        self.io = SystemsIO([Endpoint("/calibration-sets")], port=self.config["port"])
        self.neural_network = NeuralNetwork(self.config["hidden_layer_size_range"],
                                            self.config["hidden_neuron_per_layer_range"])
        self.neural_network.number_iterations = 0
        self.service_flag = False
        self.valid_classifier_exists = False
        self.iterations_fine = False
        self.valid_classifier_id = None
        # Init controllers
        self.training_ctrl = TrainingController(self)
        self.validation_ctrl = ValidationController(self)
        self.test_ctrl = TestController(self)

    def run(self, flag=False):
        self.service_flag = flag
        # Receive Calibration Set
        files = self.io.receive("/calibration-sets")
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
        self.test_ctrl.run(test_set)
        print("\n[System] --- TEST PHASE END ---")

    def reset(self):
        self.__init__()
        self.run(self.service_flag)


if __name__ == "__main__":
    controller = DevelopmentSystemController()
    controller.run()
