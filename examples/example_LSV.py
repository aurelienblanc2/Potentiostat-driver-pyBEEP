import os
import logging
from pyBEEP import (
    PotentiostatDevice,
    PotentiostatController,
    plot_iv_curve,
    setup_logging,
)

setup_logging(level=logging.INFO)

device = PotentiostatDevice(port="COM4", address=1)
controller = PotentiostatController(device=device)

folder = os.path.join("results", "example_LSV")
os.makedirs(folder, exist_ok=True)

# --- 2. Linear Sweep Voltammetry (LSV) ---
lsv_file = os.path.join(folder, "test_LSV.csv")
lsv_params = {"start": -0.5, "end": 0.5, "scan_rate": 0.05}
controller.apply_measurement(
    mode="LSV", params=lsv_params, tia_gain=0, filename="test_LSV.csv", folder=folder
)
plot_iv_curve(lsv_file, figpath=lsv_file.replace(".csv", ".png"), show=True)
