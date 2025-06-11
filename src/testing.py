from controller import PotentiostatController
from device import PotentiostatDevice

device = PotentiostatDevice(port='COM9', address=1)
controller = PotentiostatController(device=device)

controller.apply_cp(current=-0.001, duration=5, tia_gain=0, plot = False)