# pyBEEP

**pyBEEP** is a Python library for controlling and acquiring data from a custom potentiostat or similar electrochemical measurement hardware. It provides an interface for sending commands, running experiments (chronoamperometry, chronopotentiometry), and logging and plotting data for battery or electrochemical research.

## Features

- **Control a potentiostat** via minimalmodbus (serial communication)
- **Apply chronoamperometry (CA)** and **chronopotentiometry (CP)** experiments
- **Threaded data acquisition and saving** for reliable logging
- **Automatic CSV file generation** for experiment data
- **Data reduction options** for efficient memory use
- **Support for different TIA (transimpedance amplifier) gains**
- **Optional plotting** of acquired data

## Installation

Clone this repository and install using pip:

```bash
git clone https://github.com/adpisa/pyBEEP.git
cd pyBEEP
pip install .
```

## Usage

```python
from pyBEEP.controller import PotentiostatController

# Initialize the controller (adjust parameters as needed)
controller = PotentiostatController(port='COM3', address=1)

# Run a chronoamperometry experiment
controller.apply_ca(
    potential=0.5,   # Volts
    duration=10.0,   # Seconds
    tia_gain=1,      # Gain index (0=kOhm, 4=10MOhm)
    filepath="result.csv",
    plot=True
)

# Run a chronopotentiometry experiment
controller.apply_cp(
    current=0.001,   # Amps
    duration=10.0,   # Seconds
    tia_gain=1,      # Gain index
    filepath="result_cp.csv",
    plot=True
)
```

## Main Classes

- `PotentiostatController`: Main interface for running experiments and managing data.
- `PotentiostatDevice`: Low-level device communication (Modbus).

## Requirements

- Python 3.7+
- `minimalmodbus`
- `numpy`
- `threading` (standard library)
- `matplotlib` (if plotting)
- `pandas` (optional, for advanced data analysis)

Install dependencies with:

```bash
pip install minimalmodbus numpy matplotlib pandas
```

## File Structure

```
src/
  controller.py  # High-level control and experiment logic
  device.py      # Low-level Modbus device communication
  ...
```

## Notes

- Select the TIA gain (`tia_gain`) carefully to match your experimental current/potential range.
- The library creates CSV files with timestamp, experiment type, and parameters in the filename.
- Data is logged as a numpy array with potential (V) and current (A) pairs.

## License

MIT License

## Author

Adrián Pinilla-Sánchez - adpisa@gmail.com

---