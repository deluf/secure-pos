from random import random
import matplotlib.pyplot as plt
import os


class CalibrationView:
    @staticmethod
    def build_report(loss_curve):
        print("\n--- CALIBRATION REPORT ---")
        plt.figure()
        plt.plot(range(1, len(loss_curve) + 1), loss_curve, label='Calibration plot')
        plt.xlabel('Training Iteration')
        plt.ylabel('Validation Loss')
        plt.title('Training Loss Curve')
        plt.legend()
        os.makedirs("plot", exist_ok=True)
        plt.savefig("plot/calibration_plot.png")
        plt.close()
        print("--------------------------")

    @staticmethod
    def read_user_input(flag):
        # Check calibration plot and get number iterations decision
        if not flag:
            res = input(">> Data Scientist: Number iterations fine? (y/n): ")
        else:
            res = "y" if random() <= 0.3 else "n"
        return res.lower() == 'y'
