from random import randint
from development_system.calibration_view import CalibrationView


class TrainingController:
    ITERATION_PATH = "development_system/input/number_iterations.json"
    ITERATION_DECISION_PATH = "development_system/input/iterations_decision.json"

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.view = CalibrationView()

    def set_average_params(self):
        self.parent.neural_network.set_avg_hyper_params(self.parent.config.hidden_layer_size_range,
                                                        self.parent.config.hidden_neuron_per_layer_range)

    def run(self, test_set):
        iterations = self.parent.neural_network.number_iterations
        # Set average hyper params
        if iterations is None or iterations == 0:
            self.set_average_params()
        # Read number of iterations
        if self.parent.service_flag:
            iterations = input(">> Insert number of iterations (eg. 100): ")
        else:
            iterations = 50 + randint(0, 250)
        self.parent.neural_network.set_number_iterations(iterations)
        # Calibrate
        loss_curve = self.parent.neural_network.calibrate(test_set)
        # Build Report
        self.view.build_report(loss_curve)
        # Read User Input (iterations decision)
        self.parent.iterations_fine = self.view.read_user_input(self.parent.service_flag)
