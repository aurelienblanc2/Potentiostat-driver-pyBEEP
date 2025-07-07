"""
Package for controlling BEEP (Basic Electrochemical Experimentation Potentiostat).
Run common electrochemical experiments (chronoamperometry, chronopotentiometry, cyclic voltammetry, and more)
with robust data logging and plotting

Sub-package:

    Sub-package:
        gui
        measurement_modes
        utils

    Modules:
        controller
        device
        logger
        plotter
"""

__version__ = "0.1.1"

from pyBEEP.controller import PotentiostatController
from pyBEEP.device import PotentiostatDevice
from pyBEEP.plotter import plot_time_series, plot_cv_cycles, plot_iv_curve
from pyBEEP.utils import setup_logging

__all__ = [
    "PotentiostatController",
    "PotentiostatDevice",
    "plot_time_series",
    "plot_cv_cycles",
    "plot_iv_curve",
    "setup_logging",
]
