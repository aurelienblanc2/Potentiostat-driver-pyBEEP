"""
Test files for the proper package import check

    Sub-package:
        gui
        measurement_modes
        utils

    Modules:
        controller
        device
        logger
        plotter
"""


def test_package_import() -> None:
    """Test that the pyBEEP package can be imported."""
    import pyBEEP

    assert hasattr(pyBEEP, "__version__")
    assert isinstance(pyBEEP.__version__, str)

    # assert hasattr(pyBEEP, "gui")
    assert hasattr(pyBEEP, "measurement_modes")
    assert hasattr(pyBEEP, "utils")

    assert hasattr(pyBEEP, "controller")
    assert hasattr(pyBEEP, "device")
    assert hasattr(pyBEEP, "logger")
    assert hasattr(pyBEEP, "plotter")


def test_gui_import() -> None:
    """Test that the gui sub-package can be imported."""
    # from pyBEEP import gui
    pass


def test_measurement_modes_import() -> None:
    """Test that the measurement_modes sub-package can be imported."""
    from pyBEEP import measurement_modes

    assert hasattr(measurement_modes, "measurement_modes")
    assert hasattr(measurement_modes, "waveform_outputs")
    assert hasattr(measurement_modes, "waveform_params")
    assert hasattr(measurement_modes, "waveforms_gal")
    assert hasattr(measurement_modes, "waveforms_ocp")
    assert hasattr(measurement_modes, "waveforms_pot")


def test_driver_utils_import() -> None:
    """Test that the measurement_modes sub-package can be imported."""
    from pyBEEP import utils

    assert hasattr(utils, "constants")
    assert hasattr(utils, "utils")
