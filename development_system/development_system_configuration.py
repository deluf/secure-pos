import json
from shared.address import Address
from shared.range import Range


class DevelopmentSystemConfiguration:
    def __init__(self, config_path: str = 'development_system/development_system_configuration.json'):
        with open(config_path, encoding='utf-8') as f:
            self.data = json.load(f)
            self._apply_config()

    def _apply_config(self):
        """Map dictionary values to class attributes."""
        self.overfitting_tolerance = self.data.get('overfittingTolerance', 0.05)
        self.generalization_tolerance = self.data.get('generalizationTolerance', 0.25)

        mess_addr = self.data.get('messagingSystemAddress', {})
        self.messaging_system_address = Address(mess_addr.get('ip'), mess_addr.get('port'))

        clas_addr = self.data.get('classificationSystemAddress', {})
        self.classification_system_address = Address(clas_addr.get('ip'), clas_addr.get('port'))

        rng = self.data.get("hiddenLayerSizeRange")
        if not isinstance(rng, list) or len(rng) != 3:
            raise ValueError("hiddenLayerSizeRange must contain 3 elements")
        self.hidden_layer_size_range = Range(*rng)

        rng = self.data.get("hiddenNeuronPerLayerRange")
        if not isinstance(rng, list) or len(rng) != 3:
            raise ValueError("hiddenNeuronPerLayerRange must contain 3 elements")
        self.hidden_neuron_per_layer_range = Range(*rng)

    def update(self, new_values: dict):
        """Updates config at runtime."""
        self.data.update(new_values)
        self._apply_config()
