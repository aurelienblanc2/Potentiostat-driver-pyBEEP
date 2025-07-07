"""
Sub-package focused on data processing, analysis and visualization of the potentiostat data

Modules:

    cli : CLI for the sub-package datapipeline

        Functions:
            process_raw_cli
            peak_detection_proc_cli

    data_processing : Data processing functions for the potentiostat

        Functions:
            process_raw
            peak_detection_proc
        Nested Functions:
            _cleaning_raw

    signal_processing : General Signal processing functions used for data processing of the potentiostat

        Functions:
            peak_detection
            slicing_ramp
        Nested Functions:
            _merge_neighbor_idx
            _non_consecutive_idx
            _find_candidate_extremum
            _extract_row_extremum

    types : Types Declaration for the sub-package datapipeline
        Structures:
            ParametersPeakDetection

    visualization : Visualization of the potentiostat data
        Functions:
            plot_potentiostat_raw
            plot_potentiostat_proc
        Nested functions:
            _plot_ramp
            _plot_cycle
"""

from pyBEEP.datapipeline.cli import (
    process_raw_cli,
    peak_detection_proc_cli,
)

from pyBEEP.datapipeline.data_processing import (
    process_raw,
    peak_detection_proc,
)

from pyBEEP.datapipeline.signal_processing import (
    peak_detection,
    slicing_ramp,
)

from pyBEEP.datapipeline.types import (
    ParametersPeakDetection,
)

from pyBEEP.datapipeline.visualization import (
    plot_potentiostat_raw,
    plot_potentiostat_proc,
)


__all__ = [
    "process_raw_cli",
    "peak_detection_proc_cli",
    "process_raw",
    "peak_detection_proc",
    "peak_detection",
    "slicing_ramp",
    "ParametersPeakDetection",
    "plot_potentiostat_raw",
    "plot_potentiostat_proc",
]
