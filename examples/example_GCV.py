import os
import logging
from pyBEEP import (
    PotentiostatDevice,
    PotentiostatController,
    plot_cv_cycles,
    setup_logging,
)

setup_logging(level=logging.INFO)

device = PotentiostatDevice(port="COM5", address=1)
controller = PotentiostatController(device=device)

folder = r"C:\Users\pinillas\OneDrive - ICFO\Desktop"

# --- 7. Cyclic Galvanostatic Voltammetry (GCV) ---
gcv_file = os.path.join(folder, "test_GCV.csv")
gcv_params = {
    "start": -1e-3,
    "vertex1": 1e-3,
    "vertex2": -1e-3,
    "end": -1e-3,
    "num_steps": 40,
    "step_duration": 0.1,
    "cycles": 2,
}
controller.apply_measurement(
    mode="GCV", params=gcv_params, tia_gain=0, filename="test_GCV.csv", folder=folder
)
# If you know scan_points per cycle, set it below:
plot_cv_cycles(gcv_file, figpath=gcv_file.replace(".csv", ".png"), show=True, cycles=2)
