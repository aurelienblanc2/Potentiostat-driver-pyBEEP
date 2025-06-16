import os
from pyBEEP import PotentiostatDevice, PotentiostatController
from pyBEEP.plotter import plot_time_series
from pyBEEP.utils import setup_logging

setup_logging(level="INFO")

device = PotentiostatDevice(port='COM4', address=1)
controller = PotentiostatController(device=device)

folder = r"C:\Users\pinillas\OneDrive - ICFO\Desktop"

# --- 4. Potential Steps (PSTEP) ---
pstep_file = os.path.join(folder, "test_PSTEP.csv")
pstep_params = {"potentials": [0.1, -0.2, 0.3, 0.0], "step_duration": 2}
controller.apply_measurement(mode="PSTEP", params=pstep_params, tia_gain=0, filename="test_PSTEP.csv", folder=folder)
plot_time_series(pstep_file, figpath=pstep_file.replace('.csv', '.png'), show=True)