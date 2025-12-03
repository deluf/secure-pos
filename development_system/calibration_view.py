from random import random
import matplotlib.pyplot as plt


class CalibrationView:
    @staticmethod
    def build_report(flag, loss_curve):
        print("\n--- CALIBRATION REPORT ---")
        if not flag:
            plt.plot(range(1, len(loss_curve) + 1), loss_curve, label='Calibration plot')
            plt.xlabel('Training Iteration')
            plt.ylabel('Validation Loss')
            plt.title('Training Loss Curve')
            plt.legend()
            plt.show()
        print("--------------------------")

    @staticmethod
    def read_user_input(flag):
        # Check calibration plot and get number iterations decision
        if not flag:
            res = input(">> Data Scientist: Number iterations fine? (y/n): ")
        else:
            res = "y" if random() <= 0.3 else "n"
        return res.lower() == 'y'
