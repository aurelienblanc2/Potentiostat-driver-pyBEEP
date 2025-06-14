import numpy as np

def single_point(current: float, duration: float) -> np.ndarray:
    """
    Generates a single galvanostatic step.

    Args:
        current (float): The constant current value to apply (in Amperes).
        duration (float): Duration (in seconds) for which the current is held.

    Returns:
        np.ndarray: 2D array of shape (1, 2), where the row is [current, duration].
    """
    return np.array([[current, duration]], dtype=np.float32)

def current_steps(currents: list[float], step_duration: float) -> np.ndarray:
    """
    Generates a sequence of galvanostatic steps, each with the same duration.

    Args:
        currents (list[float]): List of current values (in Amperes) to apply sequentially.
        step_duration (float): Duration (in seconds) for which each current is held.

    Returns:
        np.ndarray: 2D array of shape (N, 2), where each row is [current, step_duration].
    """
    durations = [step_duration] * len(currents)
    return np.column_stack((currents, durations)).astype(np.float32)

def linear_galvanostatic_sweep(start: float, end: float, num_steps: int, step_duration: float) -> np.ndarray:
    """
    Generates a linear sweep of current from start to end value in equal steps, each with the same duration.

    Args:
        start (float): Starting current value (in Amperes).
        end (float): Ending current value (in Amperes).
        num_steps (int): Number of steps in the sweep.
        step_duration (float): Duration (in seconds) for which each current is held.

    Returns:
        np.ndarray: 2D array of shape (num_steps, 2), where each row is [current, step_duration].
    """
    currents = np.linspace(start, end, num_steps, dtype=np.float32)
    durations = np.full(num_steps, step_duration, dtype=np.float32)
    return np.column_stack((currents, durations))

def cyclic_galvanostatic(start: float, vertex: float, end: float, num_steps: int, step_duration: float, cycles: int) -> np.ndarray:
    """
    Generates a cyclic galvanostatic waveform consisting of sweeps from start to vertex and vertex to end,
    repeated for a specified number of cycles.

    Args:
        start (float): Initial current value (in Amperes).
        vertex (float): Vertex (turning point) current value.
        end (float): Final current value (in Amperes).
        num_steps (int): Number of steps in each sweep segment.
        step_duration (float): Duration (in seconds) for which each current is held.
        cycles (int): Number of complete cycles (start->vertex->end) to generate.

    Returns:
        np.ndarray: 2D array of shape (cycles * 2 * num_steps, 2),
                    where each row is [current, step_duration].
    """
    segments = []
    for _ in range(cycles):
        segments.append(linear_galvanostatic_sweep(start, vertex, num_steps, step_duration))
        segments.append(linear_galvanostatic_sweep(vertex, end, num_steps, step_duration))
    return np.vstack(segments)