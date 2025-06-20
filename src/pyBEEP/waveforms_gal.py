import numpy as np

from pyBEEP.constants import POINT_INTERVAL

def single_point(current: float, duration: float) -> dict:
    """
    Generates a single galvanostatic step.

    Args:
        current (float): Constant current to apply (in Amperes).
        duration (float): Duration of the step (in seconds).

    Returns:
        dict: {
            "Applied Current (A)": np.ndarray,  # shape (N,)
            "Time (s)": np.ndarray,             # shape (N,)
            "current_steps": np.ndarray,        # shape (1,)
            "duration_steps": np.ndarray,       # shape (1,)
            "length_steps": np.ndarray          # shape (1,)
        }
    """
    num_points = int(duration / POINT_INTERVAL)
    applied_current = np.full(num_points, current, dtype=np.float32)
    time = np.arange(num_points) * POINT_INTERVAL

    return {
        "Applied Current (A)": applied_current,
        "Time (s)": time,
        "current_steps": np.array([current], dtype=np.float32),
        "duration_steps": np.array([duration], dtype=np.float32),
        "length_steps": np.array([num_points], dtype=np.int32)
    }


def current_steps(currents: list[float], step_duration: float) -> dict:
    """
    Generates a sequence of galvanostatic steps, each with the same duration.

    Args:
        currents (list[float]): List of current values (in Amperes) to apply.
        step_duration (float): Duration (in seconds) for each step.

    Returns:
        dict: {
            "Applied Current (A)": np.ndarray,
            "Time (s)": np.ndarray,
            "current_steps": np.ndarray,
            "duration_steps": np.ndarray,
            "length_steps": np.ndarray
        }
    """
    num_points_per_step = int(step_duration / POINT_INTERVAL)
    applied_current = np.repeat(currents, num_points_per_step).astype(np.float32)
    total_points = len(applied_current)
    time = np.arange(total_points) * POINT_INTERVAL

    return {
        "Applied Current (A)": applied_current,
        "Time (s)": time,
        "current_steps": np.array(currents, dtype=np.float32),
        "duration_steps": np.full(len(currents), step_duration, dtype=np.float32),
        "length_steps": np.full(len(currents), num_points_per_step, dtype=np.int32)
    }


def linear_galvanostatic_sweep(start: float, end: float, num_steps: int, step_duration: float) -> dict:
    """
    Generates a linear sweep of current from start to end in equal steps.

    Args:
        start (float): Starting current (in Amperes).
        end (float): Ending current (in Amperes).
        num_steps (int): Number of discrete current steps.
        step_duration (float): Duration (in seconds) of each step.

    Returns:
        dict: {
            "Applied Current (A)": np.ndarray,
            "Time (s)": np.ndarray,
            "current_steps": np.ndarray,
            "duration_steps": np.ndarray,
            "length_steps": np.ndarray
        }
    """
    currents = np.linspace(start, end, num_steps, dtype=np.float32)
    points_per_step = int(step_duration / POINT_INTERVAL)
    applied_current = np.repeat(currents, points_per_step)
    time = np.arange(len(applied_current)) * POINT_INTERVAL

    return {
        "Applied Current (A)": applied_current,
        "Time (s)": time,
        "current_steps": currents,
        "duration_steps": np.full(num_steps, step_duration, dtype=np.float32),
        "length_steps": np.full(num_steps, points_per_step, dtype=np.int32)
    }


def cyclic_galvanostatic(
    start: float,
    vertex1: float,
    vertex2: float,
    num_steps: int,
    step_duration: float,
    cycles: int,
    end: float = None
) -> dict:
    """
    Generates a cyclic galvanostatic waveform with two vertex currents.

    Each cycle consists of:
        start → vertex1 → vertex2 → start

    Optionally, a final sweep from start to `end` is added if specified.

    Args:
        start (float): Starting current (in Amperes).
        vertex1 (float): First vertex current.
        vertex2 (float): Second vertex current.
        num_steps (int): Number of steps per segment.
        step_duration (float): Duration (in seconds) of each step.
        cycles (int): Number of full cycles.
        end (float, optional): Final current (if different from start).

    Returns:
        dict: {
            "Applied Current (A)": np.ndarray,
            "Time (s)": np.ndarray,
            "current_steps": np.ndarray,
            "duration_steps": np.ndarray,
            "length_steps": np.ndarray,
            "cycle": np.ndarray
        }
    """
    current_steps_list = []
    duration_steps_list = []
    length_steps_list = []
    applied_current_segments = []
    cycle_segments = []

    points_per_step = int(step_duration / POINT_INTERVAL)

    for cycle_num in range(1, cycles + 1):
        for i_start, i_end in [(start, vertex1), (vertex1, vertex2), (vertex2, start)]:
            step_currents = np.linspace(i_start, i_end, num_steps, dtype=np.float32)
            segment = np.repeat(step_currents, points_per_step)
            applied_current_segments.append(segment)
            current_steps_list.extend(step_currents.tolist())
            duration_steps_list.extend([step_duration] * num_steps)
            length_steps_list.extend([points_per_step] * num_steps)
            cycle_segments.append(np.full_like(segment, cycle_num, dtype=np.int32))

    # Optional final segment
    if end is not None and end != start:
        step_currents = np.linspace(start, end, num_steps, dtype=np.float32)
        segment = np.repeat(step_currents, points_per_step)
        applied_current_segments.append(segment)
        current_steps_list.extend(step_currents.tolist())
        duration_steps_list.extend([step_duration] * num_steps)
        length_steps_list.extend([points_per_step] * num_steps)
        cycle_segments.append(np.full_like(segment, cycles + 1, dtype=np.int32))

    applied_current = np.concatenate(applied_current_segments)
    cycle_array = np.concatenate(cycle_segments)
    time = np.arange(len(applied_current)) * POINT_INTERVAL

    return {
        "Applied Current (A)": applied_current,
        "Time (s)": time,
        "Cycle": cycle_array,
        "current_steps": np.array(current_steps_list, dtype=np.float32),
        "duration_steps": np.array(duration_steps_list, dtype=np.float32),
        "length_steps": np.array(length_steps_list, dtype=np.int32),
    }

