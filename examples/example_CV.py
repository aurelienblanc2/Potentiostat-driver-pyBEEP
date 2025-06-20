import os
from pyBEEP import PotentiostatDevice, PotentiostatController
from pyBEEP.plotter import plot_cv_cycles
from pyBEEP.utils import setup_logging

setup_logging(level="INFO")

device = PotentiostatDevice(port='COM5', address=1)
controller = PotentiostatController(device=device)

folder = r"C:\Users\pinillas\OneDrive - ICFO\Desktop"

# --- 3. Cyclic Voltammetry (CV) ---
cv_file = os.path.join(folder, "test_CV.csv")
cv_params = {"start": -0.5, "vertex1": 0.5, "vertex2": -0.5, "end": -0.5, "scan_rate": 1, "cycles": 4}
controller.apply_measurement(mode="CV", params=cv_params, tia_gain=0, filename="test_CV.csv", folder=folder)
# If you know scan_points per cycle, set it below:
plot_cv_cycles(cv_file, figpath=cv_file.replace('.csv', '.png'), show=True, cycles=4)