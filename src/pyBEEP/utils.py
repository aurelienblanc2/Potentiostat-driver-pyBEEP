import datetime
import tkinter as tk
import tkinter.filedialog as fd
import numpy as np

def default_filename(
        mode: str, 
        tia_gain: int,
) -> str:
    """
    Generates a default file name for saving data, with a timestamp and measurement details.

    Args:
        mode (str): The measurement mode.
        tia_gain (int): The transimpedance amplifier gain setting.

    Returns:
        str: The filename for the data file.
    """
    stamp = datetime.datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")
    return f"{stamp}_{mode}_tia{tia_gain}.csv"

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
    return list(np.frombuffer(np.array([value], dtype=np.float32).tobytes(order='C'), dtype=np.uint16))

def convert_uint16_to_float32(rd_data):
    adc_words = np.array(rd_data).astype(np.uint16)
    adc_bytes = adc_words.tobytes()
    rd_list = np.frombuffer(adc_bytes, np.float32)
    return np.reshape(rd_list, (-1, 2))