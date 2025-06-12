from pyBEEP import PotentiostatDevice, PotentiostatController

device = PotentiostatDevice(port='COM9', address=1)
controller = PotentiostatController(device=device)

controller.apply_ca(potential=1, duration=5, tia_gain=0, plot = True)
controller.apply_ca(potential=3, duration=5, tia_gain=0, plot = True)
controller.apply_ca(potential=3, duration=5, tia_gain=1, plot = True)
controller.apply_ca(potential=3, duration=5, tia_gain=2, plot = True)