from development_system.calibration_view import CalibrationView
from development_system.development_system_controller import DevelopmentSystemController


class TrainingController(DevelopmentSystemController):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.view = CalibrationView()

    def set_average_params(self):
        self.parent.neural_network.set_avg_hyper_params(self.parent.config.hidden_layer_size_range,
                                                        self.parent.config.hidden_neuron_per_layer_range)

    def run(self):

        number_iterations = self.parent.neural_network.number_iterations
        # Wait iterations
        if number_iterations <= 0:
            self.set_average_params()
        else:
            # Calibrate
            calibration_data = self.parent.neural_network.calibrate()

            # Build Report
            self.view.build_report(calibration_data)
            # Read User Input (iterations decision)
            self.parent.number_iterations_fine = self.view.read_user_input()
