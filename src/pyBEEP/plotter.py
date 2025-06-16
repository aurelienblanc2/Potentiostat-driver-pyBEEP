import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

def plot_time_series(
    filepaths: str | list[str],
    figpath: str | None = None,
    show: bool = False,
    dt: float = 1.0  # sample period in seconds; adjust if known, or infer from data if available
):
    """
    Plot current and potential vs time for CA, CP, GS, etc.
    """
    if isinstance(filepaths, str):
        filepaths = [filepaths]

    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(10, 6))
    fig.suptitle('Current & Potential vs Time')

    for fp in filepaths:
        data = pd.read_csv(fp, header=None)
        t = np.arange(len(data)) * dt
        label = os.path.basename(fp)
        axs[0].plot(t, data[0], label=label)  # Current (A)
        axs[1].plot(t, data[1], label=label)  # Potential (V)

    axs[0].set_ylabel('Current (A)', color='tab:red')
    axs[1].set_ylabel('Potential (V)', color='tab:blue')
    axs[1].set_xlabel('Time (s)')

    if len(filepaths) > 1:
        axs[0].legend()
        axs[1].legend()

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    if show:
        plt.show()
    if figpath:
        fig.savefig(figpath)
    plt.close(fig)

def plot_iv_curve(
    filepaths: str | list[str],
    figpath: str | None = None,
    show: bool = False
):
    """
    Plot current vs potential for LSV, CV, GCV, etc.
    """
    if isinstance(filepaths, str):
        filepaths = [filepaths]

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.suptitle('Current vs Potential')

    for fp in filepaths:
        data = pd.read_csv(fp, header=None)
        label = os.path.basename(fp)
        ax.plot(data[1], data[0], label=label)

    ax.set_xlabel('Potential (V)')
    ax.set_ylabel('Current (A)')
    if len(filepaths) > 1:
        ax.legend()
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    if show:
        plt.show()
    if figpath:
        fig.savefig(figpath)
    plt.close(fig)

def plot_cv_cycles(
    filepath: str,
    figpath: str | None = None,
    show: bool = False,
    scan_points: int | None = None,
    cycles: int | None = None
):
    """
    Plot CV data with each cycle shown in a different color.
    Assumes the data is ordered as [current, potential] rows, scans concatenated.
    Provide scan_points (points per scan, optional) and cycles (optional) if known.
    """
    data = pd.read_csv(filepath, header=None)
    current = data[0].values
    potential = data[1].values

    # If cycles or scan_points not given, try to infer:
    if scan_points is None and cycles is not None:
        scan_points = len(data) // cycles
    elif cycles is None and scan_points is not None:
        cycles = len(data) // scan_points
    elif cycles is None and scan_points is None:
        # Try to guess: look for periodicity (fall back to 1)
        scan_points = len(data)
        cycles = 1

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.suptitle('Cyclic Voltammetry (CV) - Individual Cycles')

    for n in range(cycles):
        i0 = n * scan_points
        i1 = (n + 1) * scan_points
        ax.plot(potential[i0:i1], current[i0:i1], label=f"Cycle {n+1}")

    ax.set_xlabel('Potential (V)')
    ax.set_ylabel('Current (A)')
    ax.legend()
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    if show:
        plt.show()
    if figpath:
        fig.savefig(figpath)
    plt.close(fig)