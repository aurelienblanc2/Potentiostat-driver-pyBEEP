"""
Test files for the proper package import check

Sub-package:
    datapipeline : Sub-package focused on data processing, analysis and visualization of the potentiostat data
        Modules:
            cli : CLI for the sub-package datapipeline
            data_processing : Data processing functions for the potentiostat
            signal_processing : General Signal processing functions used for data processing of the potentiostat
            types : Types Declaration for the sub-package datapipeline
            visualization : Visualization of the potentiostat data

    driver : Sub-package focused on controlling and communicating with the potentiostat
"""


def test_package_import() -> None:
    """Test that the potentiostat package can be imported."""
    import pyBEEP

    assert hasattr(pyBEEP, "__version__")
    assert isinstance(pyBEEP.__version__, str)

    assert hasattr(pyBEEP, "datapipeline")
    assert hasattr(pyBEEP, "driver")


def test_datapipeline_import() -> None:
    """Test that the datapipeline sub-package can be imported."""
    from pyBEEP import datapipeline

    assert hasattr(datapipeline, "cli")
    assert hasattr(datapipeline, "data_processing")
    assert hasattr(datapipeline, "signal_processing")
    assert hasattr(datapipeline, "types")
    assert hasattr(datapipeline, "visualization")


def test_driver_import() -> None:
    """Test that the driver sub-package can be imported."""
    from pyBEEP import driver

    assert hasattr(driver, "measurement_modes")
    assert hasattr(driver, "utils")

    assert hasattr(driver, "controller")
    assert hasattr(driver, "device")
    assert hasattr(driver, "logger")
    assert hasattr(driver, "plotter")


def test_driver_measurement_modes_import() -> None:
    """Test that the measurement_modes sub-package of the driver sub-package can be imported."""
    from pyBEEP.driver import measurement_modes

    assert hasattr(measurement_modes, "measurement_modes")
    assert hasattr(measurement_modes, "waveform_outputs")
    assert hasattr(measurement_modes, "waveform_params")
    assert hasattr(measurement_modes, "waveforms_gal")
    assert hasattr(measurement_modes, "waveforms_ocp")
    assert hasattr(measurement_modes, "waveforms_pot")


def test_driver_utils_import() -> None:
    """Test that the measurement_modes sub-package of the driver sub-package can be imported."""
    from pyBEEP.driver import utils

    assert hasattr(utils, "constants")
    assert hasattr(utils, "utils")
