from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
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
        self.x_train, self.x_val, self.x_test = None, None, None
        self.y_train, self.y_val, self.y_test = None, None, None

    def load_data_from_json(self, json_data): #CHIEDERE A FDL
        print("[NeuralNetwork] Caricamento dati ricevuti via API...")
        # Per semplicità, se il JSON è vuoto o mock, carichiamo Iris come fallback
        data = load_iris()
        x, y = data.data, data.target
        x_temp, self.x_test, y_temp, self.y_test = train_test_split(x, y, test_size=0.2, random_state=42)
        self.x_train, self.x_val, self.y_train, self.y_val = train_test_split(x_temp, y_temp, test_size=0.25, random_state=42)

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

    def calibrate(self):
        print(f"[NeuralNetwork] Training ({self.number_iterations} iterations)...")
        layers = (self.hidden_neuron_per_layer,) * self.hidden_layer_size
        model = MLPClassifier(max_iter=self.number_iterations, random_state=42,  hidden_layer_sizes=layers)
        model.fit(self.x_train, self.y_train)
        self.models.append(model)
        return {'training_accuracy': model.score(self.x_train, self.y_train)}

    def validate(self):
        scores = []
        for model in self.models:
            scores.append(model.score(self.x_val, self.y_val))
        return scores

    def test(self, id):
        model = self.models[id]
        return accuracy_score(self.y_test, model.predict(self.x_test))
