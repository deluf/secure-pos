class ValidationView:
    @staticmethod
    def build_report(scores):
        print("\n--- VALIDATION REPORT ---")
        for i, score in enumerate(scores):
            print(f"Classifier number {i}: {score}")
        print("-------------------------")

    @staticmethod
    def read_user_input(self):
        # Data Scientist: Valid classifier decision
        return input(">> Data Scientist: Is there a valid classifier? (id/n): ")
