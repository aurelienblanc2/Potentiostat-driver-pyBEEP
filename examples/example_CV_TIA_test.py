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
paths = []

# --- 1. Constant Amperometry (CA) ---
for tia in [0, 1, 2, 3]:
    cv_params = {
        "start": -0.5,
        "vertex": 0.5,
        "end": -0.5,
        "scan_rate": 0.25,
        "cycles": 2,
    }
    filename = f"test_CV_tia{tia}.csv"
    ca_file = os.path.join(folder, filename)
    controller.apply_measurement(
        mode="CV", params=cv_params, tia_gain=tia, filename=filename, folder=folder
    )
    paths.append(ca_file)
plot_cv_cycles(paths, figpath=os.path.join(folder, "tia_gain_test_CV.png"), show=True)
