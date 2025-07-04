from enum import Enum
from typing import Callable, Type
from pydantic import BaseModel, RootModel

class ModeName(str, Enum):
    CA = "CA"
    LSV = "LSV"
    CV = "CV"
    PSTEP = "PSTEP"
    CP = "CP"
    GS = "GS"
    GCV = "GCV"
    STEPSEQ = "STEPSEQ"
    OCP = "OCP"

class ControlMode(str, Enum):
    POT = "POT"
    GAL = "GAL"
    OCP = "OCP"
    
class MeasurementMode(BaseModel):
    mode_type: ControlMode
    waveform_func: Callable
    param_class: Type[BaseModel]
    
class MeasurementModeMap(RootModel[dict[ModeName, MeasurementMode]]):
    pass