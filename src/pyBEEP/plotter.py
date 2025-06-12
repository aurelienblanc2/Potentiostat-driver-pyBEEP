import matplotlib.pyplot as plt
import pandas as pd


def plot_dual_channel(filepath: str):
    data = pd.read_csv(filepath, header=None)
    fig, axs = plt.subplots(2, sharex=True)
    fig.suptitle('Potentiostat ADC Capture')

    axs[0].plot(data[0], color='tab:red')
    axs[0].set_ylabel('WEOUT (A)', color='tab:red')

    axs[1].plot(data[1], color='tab:blue')
    axs[1].set_ylabel('REOUT (V)', color='tab:blue')

    plt.xlabel("Sample #")
    plt.tight_layout()
    plt.show()