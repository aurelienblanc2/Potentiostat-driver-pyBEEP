from pyBEEP import PotentiostatDevice, PotentiostatController
from pyBEEP.plotter import plot_dual_channel
import numpy as np

device = PotentiostatDevice(port='COM9', address=1)
controller = PotentiostatController(device=device)

plot = True
time = 2

paths = []
for tia_gain in range(1):
    filepath = fr'C:\Users\pinillas\OneDrive - ICFO\Desktop\CAtia{tia_gain}'
    for current in [0.8,1.2]:
        controller.apply_ca(potential=current, duration=time, tia_gain=tia_gain, plot = plot,
                            filepath = filepath)
        filepath = filepath + 'j' + str(np.round(current*1000,2))
        paths.append(controller.last_plot_path)
plot_dual_channel(paths, show= True, figpath=r'C:\Users\pinillas\OneDrive - ICFO\Desktop\test.png')
