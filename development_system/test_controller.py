from development_system.test_view import TestView
import json
from joblib import dump
from shared.systemsio import SystemsIO
import os


class TestController:
    def __init__(self, parent):
        self.parent = parent
        self.view = TestView()

    def run(self, test_set):
        # Run Test
        print(f"[Test] Final test execution on classifier {self.parent.valid_classifier_id}...")
        test_error, model_info = self.parent.neural_network.test(self.parent.valid_classifier_id, test_set)
        # Build Report
        difference = self.view.build_report(test_error, model_info, self.parent.config["generalizationTolerance"])
        # Read User Input (Test passed)
        test_passed, hidden_layer_size, hidden_neuron_per_layer = self.view.read_user_input(
            self.parent.service_flag, difference, self.parent.config["generalizationTolerance"])

        if test_passed:
            # Create and Send Classifier
            model = self.parent.neural_network.models[self.parent.valid_classifier_id]
            os.makedirs("development_system/classifier", exist_ok=True)
            customer = test_set.split(".")[1]
            dump(model, f"development_system/classifier/classifier.{customer}.joblib")
            address = self.parent.classification_address
            SystemsIO.send_files(address, "/classifier", ["development_system/classifier/classifier.joblib"])
            print("[Test] Classifier sent")
        else:
            # Reconfigure hyper params ranges
            print(f"[Test] New range hidden layers size: {hidden_layer_size}")
            print(f"[Test] New range neurons per hidden layer: {hidden_neuron_per_layer}")
            path = self.parent.CONFIG_PATH
            with open(path, "r") as f:
                data = json.load(f)
            data["hiddenNeuronPerLayerRange"] = hidden_layer_size
            data["hiddenNeuronPerLayerRange"] = hidden_neuron_per_layer
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        return test_passed
