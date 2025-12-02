from development_system.neural_network import NeuralNetwork
from development_system.test_controller import TestController
from development_system.training_controller import TrainingController
from development_system.validation_controller import ValidationController
from shared.systemsio import SystemsIO, Endpoint
from shared.loader import load_and_validate_json_file


class DevelopmentSystemController:
    CONFIG_PATH = "development_system/input/development_system_configuration.json"
    TRAIN_PATH = "files/train_set.csv"
    VALIDATION_PATH = "files/validation_set.csv"
    TEST_PATH = "files/test_set.csv"

    def __init__(self):
        self.config = self.load_and_validate_json_file(self.CONFIG_PATH,
                                                       "development_system/schema/configuration.schema.json")
        self.io = SystemsIO([Endpoint("/calibration-sets")], port=self.config["port"])
        self.neural_network = NeuralNetwork(self.config.hidden_layer_size_range,
                                            self.config.hidden_neuron_per_layer_range)
        self.neural_network.number_iterations = 0
        self.service_flag = True #?
        self.valid_classifier_exists = False
        self.number_iterations_fine = False
        self.valid_classifier_id = None
        # Init controllers
        self.training_ctrl = TrainingController(self)
        self.validation_ctrl = ValidationController(self)
        self.test_ctrl = TestController(self)

    def run(self):
        # Receive Calibration Set
        files_to_receive = ["train_set.csv", "validation_set.csv", "test_set.csv"]
        while files_to_receive:
            received_file = self.io.receive("/calibration-sets")
            if received_file not in files_to_receive:
                continue
            files_to_receive.remove(received_file)
        print("[System] Calibration Sets received.")

        print("\n[System] --- DEVELOPMENT FLOW START ---")
        # Loop: while no valid classifier
        while not self.valid_classifier_exists:
            self.number_iterations_fine = False
            self.neural_network.number_iterations = 0

            # 1. Training Phase
            print("\n[System] --- TRAINING PHASE START ---")
            self.training_ctrl.run()
            # Loop: while number of iterations not fine
            while not self.number_iterations_fine:
                try:
                    iterations = input(">> Insert number of iterations (eg. 100): ")
                    self.neural_network.set_number_iterations(iterations)
                    self.training_ctrl.run()
                except ValueError:
                    print("Insert a valid number.")
            print("\n[System] --- TRAINING PHASE END ---")

            # 2. Validation Phase
            print("\n[System] --- VALIDATION PHASE START ---")
            self.validation_ctrl.run()
            print("\n[System] --- VALIDATION PHASE END ---")

        # 3. Test Phase
        print("\n[System] --- TEST PHASE START ---")
        self.test_ctrl.run()
        print("\n[System] --- TEST PHASE END ---")


if __name__ == "__main__":
    controller = DevelopmentSystemController()
    controller.run()

"""
class DevelopmentSystemController:

    def start_process(self, input_data):
        # Avviamo il flusso in un thread per non bloccare Flask
        thread = threading.Thread(target=self.run)
        thread.start()

    def run(self):
        # Fase Training
        self.neural_network.setAvgHyperParams()
        # Mocking input utente per demo automatica (o usare input() su console server)
        print(">> [Auto] Iterazioni impostate a 200")
        self.neural_network.setNumberIterations(200)
        cal_res = self.neural_network.calibrate()
        print(f"[Report] Calibration Accuracy: {cal_res['training_accuracy']:.4f}")

        # Fase Validazione
        print(">> [Auto] Validazione in corso...")
        val_score = self.neural_network.validate()
        print(f"[Report] Validation Accuracy: {val_score:.4f}")
        
        # Fase Test
        print(">> [Auto] Esecuzione Test...")
        test_score = self.neural_network.test()
        print(f"[Report] Test Accuracy: {test_score:.4f}")

        # Decisione Finale (BPMN Gateway)
        # Simuliamo una soglia di accettazione
        if test_score > 0.80:
            print("[Decision] Test SUPERATO.")
            # Salva modello
            model_filename = 'final_classifier.sav'
            joblib.dump(self.neural_network.model, model_filename)
            
            # BPMN End Message: Classifier Sent
            self.io.sendClassifier(model_filename)
        else:
            print("[Decision] Test FALLITO.")
            # BPMN End Message: Configuration Sent
            error_report = {"error": "Test accuracy too low", "score": test_score}
            self.io.sendNewParameters(error_report)
"""