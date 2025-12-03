from typing import List

from sklearn.neural_network import MLPClassifier
import joblib

from shared.attack_risk_level import AttackRiskLevel


class FlowClassification:

    @staticmethod
    def deploy(filename: str) -> MLPClassifier:
        model = joblib.load(filename)
        if not isinstance(model, MLPClassifier):
            raise TypeError("Loaded object is not an MLPClassifier")
        joblib.dump(model, "state/saved_model.joblib")
        return model

    @staticmethod
    def classify(model: MLPClassifier, prepared_session: dict) -> AttackRiskLevel:
        """
        Classifies the given features using the provided MLP model.

        :param model: The trained MLPClassifier.
        :param prepared_session: A PreparedSession dict.
        :return: The corresponding AttackRiskLevel.
        """
        features = [
            value for key, value in prepared_session.items()
            if key != "uuid" and key != "label"
        ]
        raw_result = model.predict([features])[0]

        try:
            return AttackRiskLevel(raw_result)
        except ValueError:
            print(f"Warning: Unknown classification label '{raw_result}'")
            return AttackRiskLevel.NORMAL
