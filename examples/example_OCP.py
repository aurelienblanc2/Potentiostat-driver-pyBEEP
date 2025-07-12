import os
import logging
from pyBEEP import (
    PotentiostatDevice,
    PotentiostatController,
    plot_time_series,
    setup_logging,
)

setup_logging(level=logging.INFO)

device = PotentiostatDevice(port="COM5", address=1)
controller = PotentiostatController(device=device)

folder = os.path.join("results", "example_OCP")
os.makedirs(folder, exist_ok=True)

# --- 1. Constant Amperometry (CA) ---
ca_file = os.path.join(folder, "test_OCP.csv")
for time in [
    1.05,
]:
    ocp_params = {"duration": time}
    controller.apply_measurement(
        mode="OCP",
        params=ocp_params,
        tia_gain=0,
        filename="test_OCP.csv",
        sampling_interval=0.05,
        folder=folder,
    )
plot_time_series(ca_file, figpath=ca_file.replace(".csv", ".png"), show=True)
