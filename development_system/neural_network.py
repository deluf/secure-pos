from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from shared.range import Range


class NeuralNetwork:
    def __init__(self, hidden_layer_size_range, hidden_neuron_per_layer_range):
        self.number_iterations = 100  # default value
        self.hidden_layer_size_range = hidden_layer_size_range  # default value
        self.hidden_neuron_per_layer_range = hidden_neuron_per_layer_range  # default value
        self.hidden_layer_size = 5  # default value
        self.hidden_neuron_per_layer = 100  # default value
        self.current_layer = hidden_layer_size_range.min
        self.current_neuron_per_layer = hidden_neuron_per_layer_range.min
        self.models = []
        self.models_info = []
        self.x_train, self.x_val, self.x_test = None, None, None
        self.y_train, self.y_val, self.y_test = None, None, None
        self.features, self.labels = None, None

    @staticmethod
    def load_data_from_csv(csv):
        print(f"[NeuralNetwork] Load data from {csv}")
        df = pd.read_csv(csv)
        #self.features, self.labels = df.drop(columns="label"), df["label"]
        le = LabelEncoder()
        df["label"] = le.fit_transform(df["label"])
        print(f"[NeuralNetwork] Data loaded correctly and labeled encoded.")
        return df.drop(columns=["label", "id"]), df["label"]
        #x_temp, self.x_test, y_temp, self.y_test = train_test_split(x, y, test_size=0.2, random_state=42)
        #self.x_train, self.x_val, self.y_train, self.y_val = train_test_split(x_temp, y_temp, test_size=0.25, random_state=42)

    def set_avg_hyper_params(self, hidden_layer_size_range, hidden_neuron_per_layer_range):
        self.hidden_layer_size = (hidden_layer_size_range.min + hidden_layer_size_range.max) / 2
        self.hidden_neuron_per_layer = (hidden_neuron_per_layer_range.min + hidden_neuron_per_layer_range.max) / 2
        print("[NeuralNetwork] Average hyper parameters set.")

    def set_number_iterations(self, iterations):
        self.number_iterations = int(iterations)
        print("[NeuralNetwork] Number of iterations set.")

    def set_hyper_params(self):
        ongoing_validation = False
        new_neuron_per_layer = self.current_neuron_per_layer + self.hidden_neuron_per_layer_range.step
        if new_neuron_per_layer <= self.hidden_neuron_per_layer_range.max:
            self.current_neuron_per_layer = new_neuron_per_layer
            ongoing_validation = True
        else:
            self.current_neuron_per_layer = self.hidden_neuron_per_layer_range.min
            if self.current_layer + self.hidden_layer_size_range.step <= self.hidden_layer_size_range.max:
                self.current_layer += self.hidden_layer_size_range.step
                ongoing_validation = True
        print("[NeuralNetwork] HyperParams checked and updated if necessary.")
        return ongoing_validation

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
            self.models_info[c_id]["difference"] = (val_err - train_err) / val_err

    def test(self, classifier_id, path):
        self.x_test, self.y_test = self.load_data_from_csv(path)
        model = self.models[classifier_id]
        #return accuracy_score(self.y_test, model.predict(self.x_test))
        return 1 - model.score(self.x_test, self.y_test), self.models_info[classifier_id]
