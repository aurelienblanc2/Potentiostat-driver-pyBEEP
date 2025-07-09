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

folder = os.path.join(os.getcwd(), "examples_results")
os.makedirs(folder, exist_ok=True)

# --- 3. Cyclic Voltammetry (CV) ---
cv_file = os.path.join(folder, "test_CV.csv")
cv_params = {
    "start": -0.5,
    "vertex1": 0.5,
    "vertex2": -0.5,
    "end": 0.5,
    "scan_rate": 0.5,
    "cycles": 2,
}
controller.apply_measurement(
    mode="CV", params=cv_params, tia_gain=0, filename="test_CV.csv", folder=folder
)
# If you know scan_points per cycle, set it below:
plot_cv_cycles(cv_file, figpath=cv_file.replace(".csv", ".png"), show=True, cycles=2)
