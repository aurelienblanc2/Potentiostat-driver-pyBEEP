import matplotlib.pyplot as plt
import pandas as pd
import threading
import os


def plot_dual_channel(
        filepaths: str | list[str],
        figpath: str | None = None,
        show: bool = False
):
    """
    Plots potentiostat ADC capture (dual channel) for one or multiple CSV files.

    Each file is expected to have two columns: the first for WEOUT (A), the second for REOUT (V).
    All files are plotted on the same figure, overlaying traces per channel.
    The x-axis is the sample index (row number).

    Args:
        filepaths (Union[str, List[str]]): Single filepath or a list of filepaths to CSV files.

    Example:
        plot_dual_channel(['file1.csv', 'file2.csv'])
    """
    if isinstance(filepaths, str):
        filepaths = [filepaths]

    fig, axs = plt.subplots(2, sharex=True, figsize=(10, 6))
    fig.suptitle('Potentiostat ADC Capture (Overlayed)')

    for fp in filepaths:
        data = pd.read_csv(fp, header=None)
        label = os.path.basename(fp)
        # Plot WEOUT (A)
        axs[0].plot(data.index, data[0], label=label)
        # Plot REOUT (V)
        axs[1].plot(data.index, data[1], label=label)

    axs[0].set_ylabel('WEOUT (A)', color='tab:red')
    axs[1].set_ylabel('REOUT (V)', color='tab:blue')
    axs[1].set_xlabel("Sample #")

    # Add legends if more than one file
    if len(filepaths) > 1:
        axs[0].legend(loc='best')
        axs[1].legend(loc='best')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    print("Function plot called in thread:", threading.current_thread().name)
    if show:
        plt.show(block=True)
    if figpath:
        fig.savefig(figpath)
    plt.close(fig)
    
def plot_j_vs_V(
        filepaths: str | list[str],
        figpath: str | None = None,
        show: bool = False
):
    """
    Plots potentiostat ADC capture (dual channel) for one or multiple CSV files.

    Each file is expected to have two columns: the first for WEOUT (A), the second for REOUT (V).
    All files are plotted on the same figure, overlaying traces per channel.
    The x-axis is the sample index (row number).

    Args:
        filepaths (Union[str, List[str]]): Single filepath or a list of filepaths to CSV files.

    Example:
        plot_dual_channel(['file1.csv', 'file2.csv'])
    """
    if isinstance(filepaths, str):
        filepaths = [filepaths]

    fig, axs = plt.subplots(1, figsize=(10, 6))
    fig.suptitle('Potentiostat ADC Capture (Overlayed)')

    for fp in filepaths:
        data = pd.read_csv(fp, header=None)
        label = os.path.basename(fp)
        # Plot WEOUT (A)
        axs.plot(data[1], data[0], label=label)

    axs.set_ylabel('WEOUT (A)', color='tab:red')
    axs.set_xlabel('REOUT (V)', color='tab:blue')

    # Add legends if more than one file
    if len(filepaths) > 1:
        axs.legend(loc='best')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    print("Function plot called in thread:", threading.current_thread().name)
    if show:
        plt.show(block=True)
    if figpath:
        fig.savefig(figpath)
    plt.close(fig)