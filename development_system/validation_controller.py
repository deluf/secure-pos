from development_system.development_system_controller import DevelopmentSystemController
from development_system.validation_view import ValidationView


class ValidationController(DevelopmentSystemController):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.view = ValidationView()

    def run(self):
        # Set HyperParams
        self.parent.ongoing_validation = self.parent.neural_network.set_hyper_params()
        print("[Validation] Initial HyperParams set (Grid Search).")

        while self.parent.ongoing_validation:
            # Calibrate
            self.parent.neural_network.calibrate()
            # Set HyperParams
            self.parent.ongoing_validation = self.parent.neural_network.set_hyper_params()

        # Validation score
        val_score = self.parent.neural_network.validate()
        # Build Report
        self.view.build_report(val_score)

        # Read User Input (Classifier decision)
        res = self.view.read_user_input()
        if res != "n" and 0 <= int(res) <= len(self.parent.neural_network.models):
            self.parent.valid_classifier_id = int(res)
            self.parent.valid_classifier_exists = True
