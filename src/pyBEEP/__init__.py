"""
Package for controlling BEEP (Basic Electrochemical Experimentation Potentiostat).
Run common electrochemical experiments (chronoamperometry, chronopotentiometry, cyclic voltammetry, and more)
with robust data logging, data processing and plotting.

Sub-package:

    datapipeline : Sub-package focused on data processing, analysis and visualization of the potentiostat data

        Modules:
            cli
            data_processing
            signal_processing
            types
            visualization

    driver : Sub-package focused on controlling, communicating and visualization the current state of the potentiostat

        Modules:
"""

__version__ = "0.1.1"

from pyBEEP.datapipeline import (
    process_raw_cli,
    peak_detection_proc_cli,
    process_raw,
    peak_detection_proc,
    peak_detection,
    slicing_ramp,
    ParametersPeakDetection,
    plot_potentiostat_raw,
    plot_potentiostat_proc,
)

from pyBEEP.driver import (
    PotentiostatController,
    PotentiostatDevice,
    plot_time_series,
    plot_cv_cycles,
    setup_logging,
    plot_iv_curve,
)

__all__ = [
    "process_raw_cli",
    "peak_detection_proc_cli",
    "process_raw",
    "peak_detection_proc",
    "peak_detection",
    "slicing_ramp",
    "ParametersPeakDetection",
    "plot_potentiostat_raw",
    "plot_potentiostat_proc",
    "PotentiostatController",
    "PotentiostatDevice",
    "plot_time_series",
    "plot_cv_cycles",
    "plot_iv_curve",
    "setup_logging",
]
