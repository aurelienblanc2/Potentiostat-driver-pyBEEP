import os
from pyBEEP import (
    plot_time_series,
    plot_iv_curve,
    plot_cv_cycles,
    connect_to_potentiostat,
)

controller = connect_to_potentiostat()

folder = os.path.join("results", "examples_methods")
os.makedirs(folder, exist_ok=True)

# --- 1. Constant Amperometry (CA) ---
ca_file = os.path.join(folder, "test_CA.csv")
ca_params = {"potential": 0.5, "duration": 2}
controller.apply_measurement(
    mode="CA", params=ca_params, tia_gain=0, filename="test_CA.csv", folder=folder
)
plot_time_series(ca_file, figpath=ca_file.replace(".csv", ".png"), show=True)

# --- 2. Linear Sweep Voltammetry (LSV) ---
lsv_file = os.path.join(folder, "test_LSV.csv")
lsv_params = {"start": -0.5, "end": 0.5, "scan_rate": 0.1}
controller.apply_measurement(
    mode="LSV", params=lsv_params, tia_gain=0, filename="test_LSV.csv", folder=folder
)
plot_iv_curve(lsv_file, figpath=lsv_file.replace(".csv", ".png"), show=True)

# --- 3. Cyclic Voltammetry (CV) ---
cv_file = os.path.join(folder, "test_CV.csv")
cv_params = {
    "start": -0.5,
    "vertex1": 0.5,
    "vertex2": -0.5,
    "end": -0.5,
    "scan_rate": 1,
    "cycles": 2,
}
controller.apply_measurement(
    mode="CV", params=cv_params, tia_gain=0, filename="test_CV.csv", folder=folder
)
# If you know scan_points per cycle, set it below:
plot_cv_cycles(cv_file, figpath=cv_file.replace(".csv", ".png"), show=True, cycles=2)

# --- 4. Potential Steps (PSTEP) ---
pstep_file = os.path.join(folder, "test_PSTEP.csv")
pstep_params = {"potentials": [0.1, -0.2, 0.3, 0.0], "step_duration": 1}
controller.apply_measurement(
    mode="PSTEP",
    params=pstep_params,
    tia_gain=0,
    filename="test_PSTEP.csv",
    folder=folder,
)
plot_time_series(pstep_file, figpath=pstep_file.replace(".csv", ".png"), show=True)

# --- 5. Chronopotentiometry (CP) ---
cp_file = os.path.join(folder, "test_CP.csv")
cp_params = {"current": 1e-3, "duration": 2}
controller.apply_measurement(
    mode="CP", params=cp_params, tia_gain=0, filename="test_CP.csv", folder=folder
)
plot_time_series(cp_file, figpath=cp_file.replace(".csv", ".png"), show=True)

# --- 6. Linear Galvanostatic Sweep (GS) ---
gs_file = os.path.join(folder, "test_GS.csv")
gs_params = {"start": -1e-3, "end": 1e-3, "num_steps": 50, "step_duration": 0.1}
controller.apply_measurement(
    mode="GS", params=gs_params, tia_gain=0, filename="test_GS.csv", folder=folder
)
plot_time_series(gs_file, figpath=gs_file.replace(".csv", ".png"), show=True)

# --- 7. Cyclic Galvanostatic Voltammetry (GCV) ---
gcv_file = os.path.join(folder, "test_GCV.csv")
gcv_params = {
    "start": -1e-3,
    "vertex1": 1e-3,
    "vertex2": -1e-3,
    "end": -1e-3,
    "num_steps": 40,
    "step_duration": 0.05,
    "cycles": 2,
}
controller.apply_measurement(
    mode="GCV", params=gcv_params, tia_gain=0, filename="test_GCV.csv", folder=folder
)
# If you know scan_points per cycle, set it below:
plot_cv_cycles(gcv_file, figpath=gcv_file.replace(".csv", ".png"), show=True, cycles=2)

# --- 8. Current Steps (STEPSEQ) ---
stepseq_file = os.path.join(folder, "test_STEPSEQ.csv")
stepseq_params = {"currents": [-1e-3, 0, 1e-3, 0], "step_duration": 1}
controller.apply_measurement(
    mode="STEPSEQ",
    params=stepseq_params,
    tia_gain=0,
    filename="test_STEPSEQ.csv",
    folder=folder,
)
plot_time_series(stepseq_file, figpath=stepseq_file.replace(".csv", ".png"), show=True)
