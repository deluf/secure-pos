class TestView:
    @staticmethod
    def build_report(score):
        print("\n--- TEST REPORT ---")
        print(f"Test result: {score}")
        print("--------------------")

    @staticmethod
    def read_user_input():
        # Data Scientist: Test passed
        res = input(">> Data Scientist: Test passed and send classifier? (y/n): ")
        hidden_layer_size = None
        hidden_neuron_per_layer = None
        if res == "n":
            hidden_layer_size = input(">> Select new range of hiddel layer size [min, max, step]")
            hidden_neuron_per_layer = input(">> Select new range of neurons per hidden layer [min, max, step]")
        return res.lower() == 'y', hidden_layer_size, hidden_neuron_per_layer
