from development_system.development_system_controller import DevelopmentSystemController
from development_system.validation_view import ValidationView


class ValidationController:
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.view = ValidationView()
        self.ongoing_validation = False

    def run(self, test_set, validation_set):
        # Set HyperParams
        self.ongoing_validation = self.parent.neural_network.set_hyper_params()
        print("[Validation] Initial HyperParams set (Grid Search).")

        while self.ongoing_validation:
            # Calibrate
            self.parent.neural_network.calibrate(test_set)
            # Set HyperParams
            self.ongoing_validation = self.parent.neural_network.set_hyper_params()

        # Validation score
        self.parent.neural_network.validate(validation_set)
        # Build Report
        top_five = self.view.build_report(self.parent.neural_network.models_info)

        # Read User Input (Classifier decision)
        res = self.view.read_user_input(self.parent.service_flag, top_five, self.parent.config["overfitting_tolerance"])
        if res != "n" and 0 <= int(res) <= len(self.parent.neural_network.models):
            self.parent.valid_classifier_id = int(res)
            self.parent.valid_classifier_exists = True
