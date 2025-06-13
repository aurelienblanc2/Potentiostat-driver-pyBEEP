import datetime
import tkinter as tk
import tkinter.filedialog as fd
import threading
import numpy as np

def default_filepath(
        mode: str, 
        value: float, 
        time: float, 
        tia_gain: int,
        folder: str | None = None,
) -> str:
    """
    Generates a default file path for saving data, with a timestamp and measurement details.

    Args:
        mode (str): The measurement mode.
        value (float): The value for the mode (e.g., voltage or current).
        time (float): The duration of the measurement.
        tia_gain (int): The transimpedance amplifier gain setting.
        folder (str | None): Optional. Folder to use; if None, a dialog will prompt the user.

    Returns:
        str: The full path for the data file.
    """
    stamp = datetime.datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")
    if not folder:
        folder = select_folder()
    return f"{folder}/{stamp}_{mode}_{value}_{time}_tia{tia_gain}.csv"

def select_folder() -> str:
    """
        Opens a dialog for the user to select a folder for saving data.
        Returns the selected folder path as a string.

        Returns:
            str: The selected folder path.
        """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder = fd.askdirectory(parent=root, title='Choose folder to save the data')
    root.destroy()
    return folder

def float_to_uint16_list(value: float) -> list[int]:
    return list(np.frombuffer(np.array([value], dtype=np.float32).tobytes(), dtype=np.uint16))