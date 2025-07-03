import os
from pyBEEP import PotentiostatDevice, PotentiostatController
from pyBEEP.plotter import plot_time_series
from pyBEEP.utils import setup_logging

setup_logging(level="INFO")

device = PotentiostatDevice(port='COM5', address=1)
controller = PotentiostatController(device=device)

folder = r"C:\Users\pinillas\OneDrive - ICFO\Desktop"

# --- 1. Constant Amperometry (CA) ---
ca_file = os.path.join(folder, "test_CA.csv")
for time in [1.05,]:
    ca_params = {"potential": 0.5, "duration": time}
    controller.apply_measurement(mode="CA", params=ca_params, tia_gain=0, filename="test_CA.csv", sampling_interval=0.2, folder=folder)
plot_time_series(ca_file, figpath=ca_file.replace('.csv', '.png'), show=True)