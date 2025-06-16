import numpy as np

from .constants import POINT_INTERVAL_POT

def constant_waveform(potential: float, duration: float) -> np.ndarray:
    """
    Generates a constant waveform for a specified duration.

    Args:
        value (float): The constant value (e.g., voltage or current) to apply.
        duration (float): Total time (in seconds) for which the value is held.

    Returns:
        np.ndarray: 1D array of length `int(duration / POINT_INTERVAL_POT)`, 
                    filled with `value`, sampled at intervals of POINT_INTERVAL_POT seconds.
    """
    length = int(duration / POINT_INTERVAL_POT)
    return np.full(length, potential, dtype=np.float32)

def potential_steps(potentials: list[float], step_duration: float) -> np.ndarray:
    """
    Generates a potentiostatic waveform consisting of consecutive potential steps,
    each held for the specified duration.

    Args:
        potentials (list[float]): List of potential values (e.g., in Volts) to apply sequentially.
        step_duration (float): Duration (in seconds) for which each potential is held.

    Returns:
        np.ndarray: 1D array of potentials, sampled at POINT_INTERVAL_POT intervals,
                    where each potential is repeated for int(step_duration / POINT_INTERVAL_POT) samples.
    """
    length_step = int(step_duration / POINT_INTERVAL_POT)
    return np.concatenate([
        np.full(length_step, potential, dtype=np.float32)
        for potential in potentials
    ])

def linear_sweep(start: float, end: float, scan_rate: float) -> np.ndarray:
    """
    Generates a linear sweep waveform from a start to an end value at a fixed scan rate.

    Args:
        start (float): Starting value (e.g., voltage or current).
        end (float): Ending value.
        scan_rate (float): Rate of change per second (units per second).

    Returns:
        np.ndarray: 1D array of values linearly interpolated from start to end, 
                    sampled at intervals of POINT_INTERVAL_POT seconds.
    """
    duration = abs(end - start) / scan_rate
    length = int(duration / POINT_INTERVAL_POT)
    return np.linspace(start, end, length, dtype=np.float32)

def cyclic_voltammetry(start: float, vertex: float, end: float, scan_rate: float, cycles: int) -> np.ndarray:
    """
    Generates a cyclic voltammetry waveform as a sequence of linear sweeps.

    Args:
        start (float): Initial value (e.g., voltage or current).
        vertex (float): Vertex (turning point) value.
        end (float): Final value.
        scan_rate (float): Rate of change per second (units per second).
        cycles (int): Number of complete cycles (forward and reverse) to generate.

    Returns:
        np.ndarray: 1D array representing the cyclic voltammetry waveform, 
                    sampled at intervals of POINT_INTERVAL_POT seconds.
    """
    segments = []
    for _ in range(cycles):
        segments.append(linear_sweep(start, vertex, scan_rate))
        segments.append(linear_sweep(vertex, end, scan_rate))
    return np.concatenate(segments)