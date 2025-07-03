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
    
class MeasurementMode(BaseModel):
    pid: bool
    waveform_func: Callable
    param_class: Type[BaseModel]
    
class MeasurementModeMap(RootModel[dict[ModeName, MeasurementMode]]):
    pass