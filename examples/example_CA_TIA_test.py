import os
from pyBEEP import PotentiostatDevice, PotentiostatController
from pyBEEP.plotter import plot_time_series
from pyBEEP.utils import setup_logging

setup_logging(level="INFO")

device = PotentiostatDevice(port='COM5', address=1)
controller = PotentiostatController(device=device)

folder = r"C:\Users\pinillas\OneDrive - ICFO\Desktop"
paths = []

# --- 1. Constant Amperometry (CA) ---
for tia in [0,1,2,3]:
    ca_params = {"potential": 0.5, "duration": 5}
    filename = f"test_CA_tia{tia}.csv"
    ca_file = os.path.join(folder, filename)
    controller.apply_measurement(mode="CA", params=ca_params, tia_gain=tia, filename=filename, folder=folder)
    paths.append(ca_file)
plot_time_series(paths, figpath=os.path.join(folder, 'tia_gain_test_CA.png'), show=True)