class CalibrationView:
    @staticmethod
    def build_report(model_data):
        print("\n--- CALIBRATION REPORT ---")
        print(f"Training Accuracy: {model_data.get('training_accuracy', 0):.4f}")
        print(f"Iterations run: {model_data.get('iterations', 0)}")
        print("--------------------------")

    @staticmethod
    def read_user_input():
        # Check calibration plot and get number iterations decision
        res = input(">> Data Scientist: Number iterations fine? (y/n): ")
        return res.lower() == 'y'
