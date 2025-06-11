import os
import datetime
import tkinter as tk
import tkinter.filedialog as fd

def default_filepath(
        mode: str, 
        value: float, 
        time: float, 
        tia_gain: int,
        folder: str | None = None,
) -> str:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")
    if not folder:
        folder = select_folder()
    return f"{folder}/{stamp}_{mode}_{value}_{time}_tia{tia_gain}.csv"

def select_folder()->str:
    root = tk.Tk()
    folder = fd.askdirectory(parent=root, title='Choose folder to save the data')
    root.destroy()
    return folder