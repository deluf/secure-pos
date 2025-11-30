from development_system.neural_network import NeuralNetwork
from development_system.test_controller import TestController
from development_system.training_controller import TrainingController
from development_system.validation_controller import ValidationController
from development_system.development_system_configuration import DevelopmentSystemConfiguration
from shared.jsonio import JsonIO


class DevelopmentSystemController:
    LISTENING_PORT = 6969

    def __init__(self):
        self.config = DevelopmentSystemConfiguration()
        self.neural_network = NeuralNetwork(self.config.hidden_layer_size_range, self.config.hidden_neuron_per_layer_range)
        self.service_flag = True #?
        self.io = JsonIO(listening_port=self.LISTENING_PORT)
        self.ongoing_validation = False
        self.valid_classifier_exists = False
        self.number_iterations_fine = False
        self.valid_classifier_id = None
        # Init controllers
        self.training_ctrl = TrainingController(self)
        self.validation_ctrl = ValidationController(self)
        self.test_ctrl = TestController(self)

    def run(self):
        # Receive Calibration Set
        calibration_set = self.io.receive(CalibrationSet)() #???
        self.neural_network.load_data(calibration_set) #???
        print("[System] Calibration Set received")

        print("\n[System] --- DEVELOPMENT FLOW START ---")

        # Loop: while no valid classifier
        while not self.valid_classifier_exists:
            self.ongoing_validation = False
            self.number_iterations_fine = False

            # 1. Training Phase
            print("\n[System] --- TRAINING PHASE START ---")
            self.training_ctrl.run()
            while not self.number_iterations_fine:
                try:
                    iterations = input(">> Insert number of iterations (eg. 100): ")
                    self.neural_network.set_number_iterations(iterations)
                except ValueError:
                    print("Insert a valid number.")
                self.training_ctrl.run()
            print("\n[System] --- TRAINING PHASE END ---")

            # 2. Validation Phase
            print("\n[System] --- VALIDATION PHASE START ---")
            self.validation_ctrl.run()
            print("\n[System] --- VALIDATION PHASE END ---")

        # 3. Test Phase
        print("\n[System] --- TEST PHASE START ---")
        self.test_ctrl.run()
        print("\n[System] --- TESTPHASE END ---")


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