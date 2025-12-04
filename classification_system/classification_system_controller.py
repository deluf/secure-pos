from classification_system.flow_classification import FlowClassification
from shared.message_counter import PhaseMessageCounter
from shared.systemsio import SystemsIO, Endpoint
from shared.loader import load_and_validate_json_file
from shared.address import Address
import joblib


class ClassificationSystemController:
    SHARED_CONFIG_PATH = "shared/json/shared_config.json"
    SHARED_CONFIG_SCHEMA = "shared/json/shared_config.schema.json"
    PREPARED_SESSION_SCHEMA = "classification_system/prepared_session.schema.json"

    def __init__(self):
        self.shared_config = load_and_validate_json_file(self.SHARED_CONFIG_PATH, self.SHARED_CONFIG_SCHEMA)
        self.classification_system_address = Address(**self.shared_config['addresses']['classificationSystem'])
        self.development_system_address = Address(**self.shared_config['addresses']['developmentSystem'])
        self.preparation_system_address = Address(**self.shared_config['addresses']['preparationSystem'])
        self.evaluation_system_address = Address(**self.shared_config['addresses']['evaluationSystem'])
        self.io = SystemsIO(
            [Endpoint("/api/classifier"), Endpoint("/api/prepared-session", self.PREPARED_SESSION_SCHEMA)],
            port=self.classification_system_address.port
        )
        self.is_production = self.shared_config['systemPhase']['productionPhase']
        self.flow = FlowClassification()
        self.service_flag = self.shared_config['serviceFlag']
        evaluation_window = self.shared_config['systemPhase']['evaluationPhaseWindow']
        production_window = self.shared_config['systemPhase']['productionPhaseWindow']
        self.counter = PhaseMessageCounter("state/classification_counter.json", evaluation_window, production_window)

    def run(self):
        model = None
        if not self.is_production:
            filename = self.io.receive("/api/classifier")[0]
            model = self.flow.deploy(filename)
            print(f"Model loaded from: {filename}")
            print(f"Model type: {type(model).__name__}")
            print(f"Hidden layer sizes: {model.hidden_layer_sizes}")
            print(f"Number of iterations trained: {model.n_iter_}")
            return

        if not self.service_flag:
            model = joblib.load("classification_system/state/saved_model.joblib")

        prepared_session = self.io.receive("/api/prepared-session")
        out_label = self.flow.classify(model, prepared_session)

        if self.counter.register_message():
            data = {
                'uuid': prepared_session['uuid'],
                'label': out_label.__str__()
            }
            self.io.send_json(self.evaluation_system_address, "/api/label", data)

        print(f"CLIENT_SIDE SYSTEM: {out_label}")


if __name__ == "__main__":
    controller = ClassificationSystemController()
    controller.run()
