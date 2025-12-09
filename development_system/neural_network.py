from sklearn.neural_network import MLPClassifier
import pandas as pd
from sklearn.preprocessing import LabelEncoder


class NeuralNetwork:
    def __init__(self, hidden_layer_size_range, hidden_neuron_per_layer_range):
        self.number_iterations = 0  # default value
        self.hidden_layer_size_range = hidden_layer_size_range  # default value
        self.hidden_neuron_per_layer_range = hidden_neuron_per_layer_range  # default value
        self.hidden_layer_size = 5  # default value
        self.hidden_neuron_per_layer = 100  # default value
        self.current_layer = None
        self.current_neuron_per_layer = None
        self.models = []
        self.models_info = []
        self.x_train, self.x_val, self.x_test = None, None, None
        self.y_train, self.y_val, self.y_test = None, None, None

    @staticmethod
    def load_data_from_csv(csv):
        print(f"[NeuralNetwork] Load data from {csv}")
        df = pd.read_csv(csv)
        le = LabelEncoder()
        df["label"] = le.fit_transform(df["label"])
        print(f"[NeuralNetwork] Data loaded correctly and labeled encoded.")
        return df.drop(columns=["label", "uuid"]), df["label"]

    def set_avg_hyper_params(self):
        self.hidden_layer_size = (self.hidden_layer_size_range['min'] + self.hidden_layer_size_range['max']) // 2
        self.hidden_neuron_per_layer = (self.hidden_neuron_per_layer_range['min'] + self.hidden_neuron_per_layer_range['max']) // 2
        print("[NeuralNetwork] Average hyper parameters set.")

    def set_number_iterations(self, iterations):
        self.number_iterations = int(iterations)
        print("[NeuralNetwork] Number of iterations set.")

    def set_hyper_params(self):
        min_n = self.hidden_neuron_per_layer_range['min']
        max_n = self.hidden_neuron_per_layer_range['max']
        step_n = self.hidden_neuron_per_layer_range['step']
        min_l = self.hidden_layer_size_range['min']
        max_l = self.hidden_layer_size_range['max']
        step_l = self.hidden_layer_size_range['step']

        # 1st case) First Iteration (Initialization)
        if self.current_layer is None:
            self.current_layer = min_l
            self.current_neuron_per_layer = min_n
            self._apply_params()
            return True

        # 2nd case) Increment Neurons (Inner Loop)
        next_neuron = self.current_neuron_per_layer + step_n
        if next_neuron <= max_n:
            self.current_neuron_per_layer = next_neuron
            self._apply_params()
            return True

        # 3rd case) Increment Layers (Outer Loop)
        next_layer = self.current_layer + step_l
        if next_layer <= max_l:
            self.current_layer = next_layer
            self.current_neuron_per_layer = min_n  # Reset inner loop
            self._apply_params()
            return True

        # End of Grid Search
        return False

    def _apply_params(self):
        self.hidden_layer_size = self.current_layer
        self.hidden_neuron_per_layer = self.current_neuron_per_layer
        print(f"[NeuralNetwork] New HyperParams: Layers={self.current_layer}, Neurons={self.current_neuron_per_layer}")

    def calibrate(self, path):
        print(f"[NeuralNetwork] Training ({self.number_iterations} iterations)...")
        layers = (self.hidden_neuron_per_layer,) * self.hidden_layer_size
        model = MLPClassifier(
                              max_iter=self.number_iterations,
                              random_state=42,
                              hidden_layer_sizes=layers,
                              early_stopping=False,
                              tol=0.0,  # prevents early stop due to tolerance threshold
                              n_iter_no_change=self.number_iterations  # prevents early stop due to loss function
                              )
        self.x_train, self.y_train = self.load_data_from_csv(path)
        model.fit(self.x_train, self.y_train)
        self.models.append(model)
        self.models_info.append(
                                {
                                    "id": len(self.models) - 1,
                                    "validation_error": None,
                                    "training_error": 1 - model.score(self.x_train, self.y_train),
                                    "difference": None,
                                    "hidden_neuron_per_layer": self.hidden_neuron_per_layer,
                                    "hidden_layer_size": self.hidden_layer_size,
                                    "network_complexity": self.hidden_neuron_per_layer * self.hidden_layer_size
                                }
        )
        return model.loss_curve_

    def validate(self, path):
        self.x_val, self.y_val = self.load_data_from_csv(path)
        for c_id, model in enumerate(self.models):
            self.models_info[c_id]["validation_error"] = 1 - model.score(self.x_val, self.y_val)
            val_err, train_err = self.models_info[c_id]["validation_error"], self.models_info[c_id]["training_error"]
            if val_err is None or val_err == 0:
                print(f"[NeuralNetwork] Validation error: {val_err} critical error")
                return False
            if train_err is None or train_err == 0:
                print(f"[NeuralNetwork] Training error: {train_err} critical error")
                return False
            difference = (val_err - train_err) / val_err if val_err > train_err \
                else (train_err - val_err) / train_err
            self.models_info[c_id]["difference"] = difference
        return True

    def test(self, classifier_id, path):
        self.x_test, self.y_test = self.load_data_from_csv(path)
        model = self.models[classifier_id]
        return 1 - model.score(self.x_test, self.y_test), self.models_info[classifier_id]
