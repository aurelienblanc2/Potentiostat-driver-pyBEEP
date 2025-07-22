import os
import logging
from pyBEEP import (
    plot_time_series,
    setup_logging,
    connect_to_potentiostat,
)

setup_logging(level=logging.INFO)

controller = connect_to_potentiostat()

folder = os.path.join("results", "example_CA_TIA")
os.makedirs(folder, exist_ok=True)
paths = []

# --- 1. Constant Amperometry (CA) ---
for tia in [0, 1, 2, 3]:
    ca_params = {"potential": 0.5, "duration": 5}
    filename = f"test_CA_tia{tia}.csv"
    ca_file = os.path.join(folder, filename)
    controller.apply_measurement(
        mode="CA", params=ca_params, tia_gain=tia, filename=filename, folder=folder
    )
    paths.append(ca_file)
plot_time_series(paths, figpath=os.path.join(folder, "tia_gain_test_CA.png"), show=True)
