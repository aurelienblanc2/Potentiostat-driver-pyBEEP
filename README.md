# pyBEEP


Welcome to **pyBEEP** – a Python library for controlling BEEP (Basic Electrochemical Experimentation Potentiostat).  
Run common electrochemical experiments (chronoamperometry, chronopotentiometry, cyclic voltammetry, and more) with robust data logging and plotting.

---

## Overview

pyBEEP provides:
- An easy interface for running standard electrochemical experiments over serial (Modbus).
- Flexible parameterization for experiment setup.
- Threaded data acquisition and automatic CSV logging.
- Optional plotting and data reduction.

---

## Main Functionalities

- **Easy experiment setup and execution:**  
  Use `PotentiostatController.apply_measurement()` to run a wide range of electrochemical experiments.
  - **Supported modes:**  
    - Discover all available experiment types with `get_available_modes()`.
    - For each mode, list all required and optional parameters with `get_mode_params(mode)`.
  - **Configurable parameters include:**  
    - `mode` (`str`): Type of experiment (e.g., `'CA'`, `'CP'`, `'CV'`, `'STEPSEQ'`, etc.)
    - *Mode-specific parameters*: (e.g., `start`, `vertex`, `scan_rate`, `currents`, etc.)
    - `tia_gain` (`int`): Sets current range by selecting the transimpedance amplifier gain.
    - `filename`, `folder` (`str`): Output file name and results directory.
    - `plot` (`bool`): Automatically show a plot after data acquisition.
- **Default results folder management:**  
  - Set a default output folder using `set_default_folder()`.
  - Retrieve or prompt for the default folder with `get_default_folder()`.

- **Low-level device control:**  
  - Access and manage the underlying potentiostat hardware via the `PotentiostatDevice` class (Modbus serial communication).

- **Automated data logging and visualization:**  
  - All experiment data is saved automatically as CSV files.
  - Optional plotting after measurement using matplotlib.

---

## Installation

Clone this repository and install using pip:

```bash
git clone https://github.com/adpisa/pyBEEP.git
cd pyBEEP
pip install .
```

---

## Usage

```python
from pyBEEP import PotentiostatDevice, PotentiostatController

device = PotentiostatDevice(port='COM3', address=1)  # Adjust port and address as needed
controller = PotentiostatController(device=device)

# Run a cyclic voltametry experiment
controller.apply_measurement(
     mode= "CV",
     params= {
         'start': -0.25,
         'vertex': 1.8,
         'end': 0,
         'scan_rate': 0.1,
         'cycles': 3
     },
     tia_gain=0,
     filename= "result_ca.csv",
     folder= 'C:/experiments',
)
        

# Run a stepped chronopotentiometry experiment
controller.apply_measurement(
     mode = "STEPSEQ",
     params= {
       'currents': [0.002, 0.01, 0.05],
       'duration': 5
     },
     tia_gain=0,
     filename= "result_ca.csv",
     folder= 'C:/experiments',
)
```

---

## Requirements

- Python 3.10+
- `minimalmodbus`
- `numpy`
- `pydantic`
- `matplotlib`
- `pandas`


Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## File Structure

```
pyBEEP/
├── project.toml                 # Project configuration (if used)
├── pyBEEP.toml                  # Package configuration (if used)
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── ruff.py                      # Linter/formatter config (if used)
├── setup.py                     # Install script
│
├── examples/                    # Example scripts for running experiments
│   ├── example_CA.py
│   ├── example_CA_TIA_test.py
│   ├── example_CV.py
│   ├── example_CV_TIA_test.py
│   ├── example_LSV.py
│   ├── example_PSTEP.py
│   └── methods_examples.py
│
└── src/
    └── pyBEEP/
        ├── constants.py         # Hardware and experiment constants
        ├── controller.py        # High-level control and experiment logic
        ├── device.py            # Low-level Modbus device communication
        ├── logger.py            # Threaded data logging to file
        ├── plotter.py           # Data plotting utilities
        ├── utils.py             # Utility functions (e.g. file/folder selection)
        ├── waveform_params.py   # Parameter validation for experiments
        ├── waveforms_gal.py     # Potential-controlled waveform definitions
        ├── waveforms_pot.py     # Current-controlled waveform definitions
        └── __init__.py
```

- **examples/** contains working scripts that demonstrate how to use pyBEEP for different types of experiments.  
- **src/pyBEEP/** is the main package source code.

---

## Notes

- Select the TIA gain (`tia_gain`) carefully to match your experimental current/potential range.
- The library creates CSV files with timestamp, experiment type, and parameters in the filename.
- Data is logged as a numpy array with potential (V) and current (A) pairs.

---

## Roadmap & Planned Features

- Support for Electrochemical Impedance Spectroscopy (EIS)
- Graphical user interface (GUI) for experiment management
- Extended data analysis and export options

See the [pending_to_add] for the latest roadmap and bug tracker.

---

## Bugs & Support

If you encounter a bug, have a feature request, or need help:
- Please open an  [pending_to_add]
- Or contact: adpisa@gmail.com

---

## Contributing

Contributions are very welcome!  
If you’d like to add features, fix bugs, or improve documentation, please submit a merge request or open an issue to discuss your ideas.

---
## License

MIT License

## Author

Adrián Pinilla-Sánchez - adpisa@gmail.com

---