import os
import logging
from pyBEEP import (
    plot_iv_curve,
    setup_logging,
    connect_to_potentiostat,
)

setup_logging(level=logging.INFO)

controller = connect_to_potentiostat()

folder = os.path.join("results", "example_LSV")
os.makedirs(folder, exist_ok=True)

# --- 2. Linear Sweep Voltammetry (LSV) ---
lsv_file = os.path.join(folder, "test_LSV.csv")
lsv_params = {"start": -0.5, "end": 0.5, "scan_rate": 0.05}
controller.apply_measurement(
    mode="LSV", params=lsv_params, tia_gain=0, filename="test_LSV.csv", folder=folder
)
plot_iv_curve(lsv_file, figpath=lsv_file.replace(".csv", ".png"), show=True)
