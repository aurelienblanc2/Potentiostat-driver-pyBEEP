import numpy as np

from .constants import POINT_INTERVAL_POT, POINT_INTERVAL_GAL


def constant_waveform(mode: str, value: float, duration: float) -> np.ndarray:
    point_interval = POINT_INTERVAL_POT if mode == 'pid_inactive' else POINT_INTERVAL_GAL
    length = int(duration / point_interval)
    return np.full(length, value, dtype=np.float32)

def linear_sweep(mode: str, start: float, end: float, scan_rate: float) -> np.ndarray:
    point_interval = POINT_INTERVAL_POT if mode == 'pid_inactive' else POINT_INTERVAL_GAL
    duration = abs(end - start) / scan_rate
    length = int(duration / point_interval)
    return np.linspace(start, end, length, dtype=np.float32)

def cyclic_voltammetry(mode: str, start: float, vertex: float, end: float, scan_rate: float, cycles: int) -> np.ndarray:
    segments = []
    for _ in range(cycles):
        segments.append(linear_sweep(mode, start, vertex, scan_rate))
        segments.append(linear_sweep(mode, vertex, end, scan_rate))
    return np.concatenate(segments)