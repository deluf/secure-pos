from development_system.classifier import Classifier
from development_system.development_system_controller import DevelopmentSystemController
from development_system.test_view import TestView
import joblib
import io
from shared.systemsio import SystemsIO


class TestController(DevelopmentSystemController):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.view = TestView()

    def run(self):
        # Run Test
        print("[Test] Final test execution...")
        test_score = self.parent.neural_network.test(self.parent.valid_classifier_id)
        # Build Report
        self.view.build_report(test_score)
        # Read User Input (Test passed)
        test_passed, hidden_layer_size, hidden_neuron_per_layer = self.view.read_user_input()

        if test_passed:
            # Create Classifier
            # Send Classifier
            model = self.parent.neural_network.models[self.parent.valid_classifier_id]
            pickled = pickle.dumps(model, protocol=pickle.HIGHEST_PROTOCOL)
            b64 = base64.b64encode(pickled).decode('ascii')
        else:
            # Send TestResults
            print(f"New range hidden layers size: {hidden_layer_size}")
            print(f"New range neurons per hidden layer: {hidden_neuron_per_layer}")
        return test_passed