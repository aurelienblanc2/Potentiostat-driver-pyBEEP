from pydantic import BaseModel
from typing import List

# --- Potentiostatic waveform parameters ---

class ConstantWaveformParams(BaseModel):
    value: float
    duration: float

class PotentialStepsParams(BaseModel):
    potentials: List[float]
    step_duration: float

class LinearSweepParams(BaseModel):
    start: float
    end: float
    scan_rate: float

class CyclicVoltammetryParams(BaseModel):
    start: float
    vertex: float
    end: float
    scan_rate: float
    cycles: int

# --- Galvanostatic waveform parameters ---

class SinglePointParams(BaseModel):
    current: float
    duration: float

class CurrentStepsParams(BaseModel):
    currents: List[float]
    step_duration: float

class LinearGalvanostaticSweepParams(BaseModel):
    start: float
    end: float
    num_steps: int
    step_duration: float

class CyclicGalvanostaticParams(BaseModel):
    start: float
    vertex: float
    end: float
    num_steps: int
    step_duration: float
    cycles: int