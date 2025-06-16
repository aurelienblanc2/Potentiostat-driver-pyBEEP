import os
from pyBEEP import PotentiostatDevice, PotentiostatController
from pyBEEP.plotter import plot_cv_cycles
from pyBEEP.utils import setup_logging

setup_logging(level="INFO")

device = PotentiostatDevice(port='COM4', address=1)
controller = PotentiostatController(device=device)

folder = r"C:\Users\pinillas\OneDrive - ICFO\Desktop"

# --- 3. Cyclic Voltammetry (CV) ---
cv_file = os.path.join(folder, "test_CV.csv")
cv_params = {"start": -0.5, "vertex": 0.5, "end": -0.5, "scan_rate": 0.2, "cycles": 2}
controller.apply_measurement(mode="CV", params=cv_params, tia_gain=0, filename="test_CV.csv", folder=folder)
# If you know scan_points per cycle, set it below:
scan_points = None  # e.g., 1000
plot_cv_cycles(cv_file, figpath=cv_file.replace('.csv', '.png'), show=True, scan_points=scan_points, cycles=2)