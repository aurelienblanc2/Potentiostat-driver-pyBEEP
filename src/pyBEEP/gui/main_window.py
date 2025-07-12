import sys
import ast
import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
from pyBEEP.device import PotentiostatDevice
from pyBEEP.controller import PotentiostatController


# GUI Application
class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Potentiostat driver - pyBEEP ")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.controller = self.connect_to_potentiostat()

        self.mode_list = self.controller.get_available_modes()

        # Mode Combobox (scrollable list dropdown)
        self.combobox_mode_item = tk.StringVar()
        self.combobox_mode_label = tk.Label(self.root, text="Select Mode:")
        self.combobox_mode = ttk.Combobox(
            self.root,
            textvariable=self.combobox_mode_item,
            values=self.mode_list,
            state="readonly",
            width=8,
        )
        self.combobox_mode_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.combobox_mode.grid(row=0, column=1, sticky="w")

        # Bind event to trigger change of plate
        self.combobox_mode.bind(
            "<<ComboboxSelected>>", lambda event: self.update_param_list()
        )

        self.param_dict = {}
        self.mode = None
        self.param = {}

        # Run button
        self.run_button = tk.Button(
            self.root,
            text="Run Experiment",
            command=self.run_experiment,
            bg="green",
            fg="white",
        )
        self.run_button.grid(row=0, column=2, padx=20, pady=20)

        self.parameters_list = []
        self.parameters_list_type = []
        self.parameters_values = []
        self.parameters_label = []
        self.parameters_entry = []

        self.optional_label = tk.Label(self.root, text="OPTIONAL PARAMETERS:")
        self.optional_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="e")

        self.tia_gain = tk.StringVar()
        self.tia_gain_label = tk.Label(self.root, text="tia_gain (int)")
        self.tia_gain_entry = tk.Entry(self.root, width=15, textvariable=self.tia_gain)
        self.tia_gain_label.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="e")
        self.tia_gain_entry.grid(row=2, column=1, padx=10, pady=(0, 10))

        self.sampling_interval = tk.StringVar()
        self.sampling_interval_label = tk.Label(
            self.root, text="sampling_interval (float)"
        )
        self.sampling_interval_entry = tk.Entry(
            self.root, width=15, textvariable=self.sampling_interval
        )
        self.sampling_interval_label.grid(
            row=3, column=0, padx=10, pady=(0, 10), sticky="e"
        )
        self.sampling_interval_entry.grid(row=3, column=1, padx=10, pady=(0, 10))

        self.filename = tk.StringVar()
        self.filename_label = tk.Label(self.root, text="filename (str)")
        self.filename_entry = tk.Entry(self.root, width=15, textvariable=self.filename)
        self.filename_label.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="e")
        self.filename_entry.grid(row=4, column=1, padx=10, pady=(0, 10))

        self.folder = tk.StringVar()
        self.folder_label = tk.Label(self.root, text="folder (str)")
        self.folder_entry = tk.Entry(self.root, width=15, textvariable=self.folder)
        self.folder_label.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="e")
        self.folder_entry.grid(row=5, column=1, padx=10, pady=(0, 10))

    def connect_to_potentiostat(self):
        ports = serial.tools.list_ports.comports()
        device = None
        if not ports:
            raise ValueError(
                "No ports found, verify that the device is connected (and flashed) then try again"
            )

        for port in ports:
            if (port.vid == 2022) and (port.pid == 22099):
                device = PotentiostatDevice(port=port.name, address=1)
                break

        if device is None:
            raise ValueError(
                "No port found for the potentiostat, verify that the device is connected (and flashed) then try again"
            )
        else:
            controller = PotentiostatController(device=device)

        return controller

    def update_param_list(self):
        self.mode = self.combobox_mode_item.get()
        self.param_dict = self.controller.get_mode_params(self.mode)

        # Destruction
        for i in range(len(self.parameters_list)):
            self.parameters_label[i].grid_remove()
            self.parameters_entry[i].grid_remove()

        self.parameters_label = []
        self.parameters_entry = []
        self.parameters_list = []
        self.parameters_list_type = []
        self.parameters_values = []

        # Creation
        self.required_label = tk.Label(self.root, text="REQUIRED PARAMETERS:")
        self.required_label.grid(row=6, column=0, padx=10, pady=(0, 10), sticky="e")

        self.parameters_list = list(self.param_dict.keys())
        for i, param in enumerate(self.parameters_list):
            self.parameters_values.append(tk.StringVar())

            # Creation
            self.parameters_list_type.append(self.param_dict[param].__name__)
            label = param + " (" + self.parameters_list_type[i] + ")"
            self.parameters_label.append(tk.Label(self.root, text=label))
            self.parameters_entry.append(
                tk.Entry(self.root, width=15, textvariable=self.parameters_values[i])
            )

            # Display
            self.parameters_label[i].grid(
                row=i + 7, column=0, padx=10, pady=(0, 10), sticky="e"
            )
            self.parameters_entry[i].grid(row=i + 7, column=1, padx=10, pady=(0, 10))

    def run_experiment(self):
        if self.mode is None:
            messagebox.showerror("Error", "Please select a mode")
            return

        for i, param in enumerate(self.parameters_list):
            value = self.parameters_values[i].get()
            if value == "":
                messagebox.showerror("Error", "Please fill all the parameters")
                return
            if self.parameters_list_type[i] == "float":
                self.param[param] = float(value)
            elif self.parameters_list_type[i] == "int":
                self.param[param] = int(float(value))
            elif self.parameters_list_type[i] == "List":
                self.param[param] = ast.literal_eval(value)
            else:
                raise TypeError(
                    f"Unknown parameter type: {self.parameters_list_type[i]}"
                )

        if self.tia_gain.get() == "":
            tia_gain = 0
        else:
            tia_gain = int(float(self.tia_gain.get()))
        if self.sampling_interval.get() == "":
            sampling_interval = None
        else:
            sampling_interval = float(self.sampling_interval.get())
        if self.filename.get() == "":
            filename = None
        else:
            filename = self.filename.get()
        if self.folder.get() == "":
            folder = None
        else:
            folder = self.folder.get()

        self.controller.apply_measurement(
            self.mode,
            self.param,
            tia_gain=tia_gain,
            sampling_interval=sampling_interval,
            filename=filename,
            folder=folder,
        )

    def on_close(self):
        self.root.destroy()
        sys.exit()


def Launch_GUI():
    root = tk.Tk()
    GUI(root)
    root.mainloop()


# Run the app
if __name__ == "__main__":
    Launch_GUI()
