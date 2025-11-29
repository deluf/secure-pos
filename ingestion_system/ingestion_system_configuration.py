import json
from shared.address import Address

class IngestionSystemConfiguration:
    def __init__(self, config_path: str = 'ingestion_system/ingestion_system_configuration.json'):
        with open(config_path, encoding='utf-8') as f:
            self.data = json.load(f)
            self._apply_config()

    def _apply_config(self):
        """Map dictionary values to class attributes."""
        self.minimum_records = self.data.get('minimumRecords', 3)
        self.missing_samples_threshold = self.data.get('missingSamplesThreshold', 2)

        eval_addr = self.data.get('evaluationSystemAddress', {})
        self.evaluation_system_address = Address(eval_addr.get('ip'), eval_addr.get('port'))

        prep_addr = self.data.get('preparationSystemAddress', {})
        self.preparation_system_address = Address(prep_addr.get('ip'), prep_addr.get('port'))

        self.evaluation_phase_limit = self.data.get('evaluationPhaseWindow', 10)
        self.production_phase_limit = self.data.get('productionPhaseWindow', 100)

    def update(self, new_values: dict):
        """Updates config at runtime."""
        self.data.update(new_values)
        self._apply_config()
        print(f"[Config] Configuration updated. New Threshold: {self.missing_samples_threshold}")