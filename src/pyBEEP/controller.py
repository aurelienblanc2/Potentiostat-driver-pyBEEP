from queue import Queue
import numpy as np
import queue
import threading
from time import monotonic_ns
import minimalmodbus
import logging
from typing import Callable
from pydantic import ValidationError

from .device import PotentiostatDevice
from .logger import DataLogger
from .utils import default_filename, convert_uint16_to_float32, select_folder
from .waveforms_pot import constant_waveform, linear_sweep, cyclic_voltammetry, potential_steps
from .waveforms_gal import single_point, linear_galvanostatic_sweep, cyclic_galvanostatic, current_steps
from .constants import CMD, REG_READ_ADDR, REG_WRITE_ADDR_PID, REG_WRITE_ADDR_POT, BUSSY_DLAY_NS
from .waveform_params import (
    ConstantWaveformParams, PotentialStepsParams, LinearSweepParams, CyclicVoltammetryParams,
    SinglePointParams, CurrentStepsParams, LinearGalvanostaticSweepParams, CyclicGalvanostaticParams
)

logger = logging.getLogger(__name__)

class PotentiostatController:
    def __init__(self, device: PotentiostatDevice, default_folder: str | None = None):
        """
       Initialize the PotentiostatController.

       Args:    
           device (PotentiostatDevice): The hardware interface for the potentiostat.
           default_folder (str | None): Default folder for saving measurement files. If None, no default is set.
       """
        self.device = device
        self.default_folder = default_folder
        self.last_plot_path = None
        self.device_lock = threading.Lock()
        self._measurement_modes = {
            "CA": {"pid": False, "waveform_func": constant_waveform, "param_class": ConstantWaveformParams},
            "LSV": {"pid": False, "waveform_func": linear_sweep, "param_class": LinearSweepParams},
            "CV": {"pid": False, "waveform_func": cyclic_voltammetry, "param_class": CyclicVoltammetryParams},
            "PSTEP": {"pid": False, "waveform_func": potential_steps, "param_class": PotentialStepsParams},

            "CP": {"pid": True, "waveform_func": single_point, "param_class": SinglePointParams},
            "GS": {"pid": True, "waveform_func": linear_galvanostatic_sweep,
                   "param_class": LinearGalvanostaticSweepParams},
            "GCV": {"pid": True, "waveform_func": cyclic_galvanostatic, "param_class": CyclicGalvanostaticParams},
            "STEPSEQ": {"pid": True, "waveform_func": current_steps, "param_class": CurrentStepsParams},
        }
        
    def set_default_folder(self, folder: str | None = None):
        """
        Set the default folder for saving measurement files.

        Args:
            folder (str | None): The folder path to set as default. If None, no default is set.
        """
        if folder:
            self.default_folder = folder
        else:
            self.default_folder = select_folder()
        logger.info(f"Default folder set to: {self.default_folder}")

    def get_default_folder(self) -> str:
        """
        Get the default folder used for saving measurement files.

        Returns:
            str: The currently set default folder path. If not set, prompts the user to select one.
        """
        if not self.default_folder:
            self.set_default_folder()
        return self.default_folder
            
    def get_available_modes(self) -> list[str]:
        """
        Get a list of available measurement modes supported by this controller.

        Returns:
            list[str]: A list of string keys for supported measurement modes (e.g. 'CA', 'CV', 'LSV', etc.).
        """
        return list(self._measurement_modes.keys())

    def get_mode_params(self, mode: str) -> dict[str, type]:
        """
        Get the parameter names and types required for a given measurement mode.

        Args:
            mode (str): The measurement mode key (e.g. 'CA', 'CV').

        Returns:
            dict[str, type]: A dictionary mapping parameter names to their expected types.

        Raises:
            ValueError: If the mode is not recognized.
        """
        mode_config = self._measurement_modes.get(mode.upper())
        if not mode_config:
            raise ValueError(f"Unknown measurement mode: {mode}")
        param_class = mode_config["param_class"]
        return {name: field.annotation for name, field in param_class.model_fields.items()}

    def get_waveform_func(self, mode: str) -> Callable | None:
        """
        Retrieve the waveform generation function associated with a given mode.

        Args:
            mode (str): The measurement mode key.

        Returns:
            Callable | None: The waveform generation function, or None if the mode is not found.
        """
        return self._measurement_modes.get(mode.upper(), {}).get("waveform_func")

    def is_pid_active(self, mode: str) -> bool:
        """
        Check if PID control is active for the given measurement mode.

        Args:
            mode (str): The measurement mode key.

        Returns:
            bool: True if PID control is used for this mode, False otherwise.
        """
        return self._measurement_modes.get(mode.upper(), {}).get("pid")

    def _setup_measurement(self, tia_gain: int, clear_fifo: bool = False, fifo_start: bool = False):
        """
        Configure and initialize the potentiostat hardware for a new measurement.

        Args:
            tia_gain (int): Transimpedance amplifier gain setting.
            clear_fifo (bool, optional): Whether to clear the FIFO buffer before starting. Defaults to False.
            fifo_start (bool, optional): Whether to start the FIFO immediately. Defaults to False.
        """
        self.device.send_command(CMD['SET_TIA_GAIN'], tia_gain)
        if clear_fifo:
            self.device.send_command(CMD['CLEAR_FIFO'], 1)
        if fifo_start:
            self.device.send_command(CMD['FIFO_START'], 1)
        self.device.send_command(CMD['SET_SWITCH'], 1)

    def _run_measurement(self, write_func: Callable[[queue.Queue], None], filepath: str, reducing_factor: int | None):
        """
        Run the measurement  process, managing writing and saving threads.

        Args:
            write_func (Callable): Function to perform measurement and write data to a queue.
            filepath (str): Path to the file where data will be saved.
            reducing_factor (int | None): If set, will average every N rows before saving. Defaults to None (no reduction).
        """
        data_queue = queue.Queue()
        writer = DataLogger(data_queue, filepath, reducing_factor)

        write_thread = threading.Thread(target=write_func, args=(data_queue,))
        save_thread = threading.Thread(target=writer.run)

        write_thread.start()
        save_thread.start()

        try:
            write_thread.join()
        finally:
            data_queue.put(None)
            save_thread.join()

    def _teardown_measurement(self):
        """
        Switch off potentiostat after measurement is complete.
        """
        self.device.send_command(CMD["SET_SWITCH"], 0)
        self.device.send_command(CMD["TEST_STOP"], 1)

    def apply_measurement(
        self,
        mode: str,
        params: dict,
        *,
        tia_gain: int = 0,
        reducing_factor: int | None = None,
        filename: str | None = None,
        folder: str | None = None
    ):
        """
        Function for performing electrochemical measurements with the potentiostat. Takes electrochemical method 
        and its parameters, validates them, generate waveform for running the experiment, and runs it.

        Args:
            mode (str): Measurement mode key (e.g., 'CA', 'CV', etc.).
            params (dict): Dictionary of parameters for the waveform generation.
            tia_gain (int, optional): Transimpedance amplifier gain setting. Defaults to 0.
            reducing_factor (int | None): If set, will average every N rows before saving. Defaults to None (no reduction).
            filename (str | None, optional): File path for storing measurement data. If None, a default is generated.
            folder (str | None, optional): Folder for storing the file. Used if filepath is None.

        Raises:
            ValueError: If the mode is unknown or parameter validation fails.
        
        Notes:
            - Select the TIA_GAIN carefully according to you expected current range of the reaction. If the gian is
              higher than needed (lower resistance), a higher noise level will be assumed unnecessarily. But if the
              gain is set too low (higher resistance), the desired current might not be reached.
        """
        mode_config = self._measurement_modes.get(mode.upper())
        if not mode_config:
            raise ValueError(f"Unknown measurement mode: {mode}")

        param_class = mode_config["param_class"]
        try:
            # Validate and parse user input with Pydantic
            param_obj = param_class(**params)
        except ValidationError as e:
            required_fields = [f for f in param_class.model_fields.keys()]
            raise ValueError(
                f"Parameter error for mode '{mode}':\n"
                f"{e}\n"
                f"Expected fields: {required_fields}"
            )

        # Use .model_dump() for Pydantic v2 to unpack validated params
        waveform = mode_config["waveform_func"](**param_obj.model_dump())
        
        filename = filename or default_filename(mode=mode, tia_gain=tia_gain)
        folder = folder or self.get_default_folder()
        filepath = f"{folder}/{filename}"

        if mode_config['pid']:
            write_func = lambda q: self._read_write_data_pid_active(q, waveform, tia_gain)
        else:
            write_func = lambda q: self._read_write_data_pid_inactive(q,waveform, tia_gain)
        with self.device_lock:
            logger.debug(f'Mode: {mode.upper()}\nWavefunction: {mode_config["waveform_func"]}\n'
                         f'Gain: {tia_gain}\nFilepath: {filepath}')
            self._run_measurement(write_func, filepath, reducing_factor)

        self.last_plot_path = filepath

    def _read_operation(self,
            st: int,
            params: dict,
            n_register: int,
            ) -> list | None:
        try:
            if (st - params['rd_dly_st']*0) > params['busy_dly_ns']:
                rd_data = self.device.read_data(REG_READ_ADDR,
                                                n_register)  # Collect data
                return rd_data
        except minimalmodbus.SlaveReportedException or minimalmodbus.SlaveDeviceBusyError:
            logger.debug('Reading error, retrying...')
            params['rd_dly_st'] = monotonic_ns()
            params['rd_err_cnt'] += 1
            if params['rd_err_cnt'] > 16:
                logger.error('Reading errors exceeded the limit, potentiostat not responding.')
                raise
        return None

    def _read_write_data_pid_active(
            self,
            data_queue: Queue,
            waveform: np.ndarray,
            tia_gain: int | None = 0,
            n_register: int | None = 120,
    ) -> None:
        """
        Perform a measurement using PID-regulated current mode. The function handles writing commands 
        of the commands to the potentiostat, given the current steps given, and reading of the 
        potentiostat adc output data, which is added to a queue.

        Args:
            data_queue (Queue): Queue to which acquired data is pushed.
            waveform (np.ndarray): Array of [current, duration] pairs to be applied sequentially.
            tia_gain (int | None): TIA gain setting for measurement.
            n_register (int | None): Number of data words to read per register operation.

        Raises:
            minimalmodbus.SlaveReportedException: If serial communication with the potentiostat fails repeatedly.

        Behaviour:
            - The current input is converted from np.float32 to uint16
            - The Transimpedance amplifier gain (TIA_GAIN) is initialized to the specified resistance and the FIFO
              is cleared.
            - For each current step, the PID is activated (which will switch on the FIFO too), setting the current 
              value of the corresponding step as target (converted to uint16). This is followed a a reading loop that
              keeps withdrawing data during the step duration. The data read, is converted back to np.float32 and 
              added to the 'data_queue' shared with the saving thread.
            - The 'data_queue' consist of a np.ndarray: A numpy array where each element is a pair of float values:
              [potential (in V), current (in A)]
            - Once the measurement is finished, potentiostat is switched off.
        """
        self._setup_measurement(tia_gain=tia_gain, clear_fifo=True)

        params = {'busy_dly_ns': BUSSY_DLAY_NS, 'wr_err_cnt': 0, 'rd_err_cnt': 0, 'wr_dly_st': 0,
                  'rd_dly_st': 0, 'rx_tx_reg': 0, 'wr_tx_reg': 0, 'rd_tx_reg': 0, 'transmission_st': monotonic_ns()}

        global_start_ns = monotonic_ns()

        for current, duration in waveform:
            target = np.array([current,], dtype=np.float32).tobytes(order='C')
            target = np.frombuffer(target, np.uint16).tolist()

            #Activate PID and set target
            self.device.write_data(REG_WRITE_ADDR_PID, [CMD['PID_START']] + target)  # Send data

            start_ns = monotonic_ns()
            end_ns = start_ns + int(duration * 1e9)

            # Start collecting
            while monotonic_ns() < end_ns:
                st = monotonic_ns()
                # We need read two times for each write time because adc push two values to FIFO
                for _ in range(0, 2):
                    rd_data = self._read_operation(st, params, n_register)
                    if rd_data:
                        rd_list = convert_uint16_to_float32(rd_data)
                        data_queue.put(rd_list)
                        params['rd_tx_reg'] += len(rd_list)
                        params['rd_err_cnt'] = 0
                    else:
                        break

        self._teardown_measurement()

        total_time_ns = monotonic_ns() - global_start_ns
        result_tm = total_time_ns / 1e9
        data_rate = (2 * params['rx_tx_reg']) / result_tm
        logger.info(f"\nTotal transmission time {result_tm:3.4} s, data rate {(data_rate / 1000):3.4} KBytes/s.\n")
        logger.info(f"Failed writing: {params['wr_err_cnt']}")
        logger.info(f"Failed reading: {params['rd_err_cnt']}")
        logger.info(f"Send: {params['wr_tx_reg']}, Read: {params['rd_tx_reg']}, Diff: {params['rd_tx_reg'] - params['wr_tx_reg']*2}\n")

    def _read_write_data_pid_inactive(
            self,
            data_queue: Queue,
            waveform: np.ndarray,
            tia_gain: int | None = 0,
            n_register: int = 120,
    ) -> None:
        """
        Perform a measurement using standard voltage-controlled mode. The function handles writing 
        commands of the commands to the potentiostat, given the current steps given, and reading of
        the potentiostat adc output data, which is added to a queue.

         Args:
            data_queue (Queue): Queue to which acquired data is pushed.
            waveform (np.ndarray): Array of potential values to be applied over time.
            tia_gain (int | None): TIA gain setting for measurement.
            n_register (int): Number of data words to read per register operation.

        Raises:
            minimalmodbus.SlaveReportedException: If serial communication with the potentiostat fails repeatedly.

        Behaviour:
           - The Transimpedance amplifier gain (TIA_GAIN) is initialized to the specified resistance and the FIFO
             is cleared and switch on.
           - The writing and reading of data is performed in a loop until all the data list created is sent.
             In this loop, a try-except clause is used for both writing and reading. No delays for writing or reading
             are applied, it will always keep trying to send and read data. Once all input voltage list is consumed,
             it will attept to read the FIFO 3 more times, to make sure all data is collected.
           - When reading, the output data is converted back from uint16 to np.float32 and added to 'data_queue'.
           - The 'data_queue' consist of a np.ndarray: A numpy array where each element is a pair of float values:
             [potential (in V), current (in A)]
           - Once the measurement is finished, potentiostat is switched off and adc_data list is returned.

        Notes:
           - Select the TIA_GAIN carefully according to your expected potential range of the reaction. If the gain
             is higher than needed (lower resistance), a higher noise level will be assumed unnecessarily. But if the
             gain is set too low (higher resistance), the desired potential might not be reached.
           - Unexpected behaviour is sometimes observed in first iterations of the while loop: number of reading 
             operations is sometimes lower than writing operations. This was solved by (1) eliminating delays on
             reading and writing attempts, and (2) Adding 3 extra attempt after writing finishes to try to not leave
             any unread data in the FIFO. Still issues arise if measurements last less than 1s.
        """

        params = {'busy_dly_ns': BUSSY_DLAY_NS, 'wr_err_cnt': 0, 'rd_err_cnt': 0, 'wr_dly_st': 0,
                  'rd_dly_st': 0, 'rx_tx_reg': 0, 'wr_tx_reg': 0, 'rd_tx_reg': 0, 'transmission_st': monotonic_ns()}

        # Generate numpy array to send
        y_bytes = waveform.tobytes(order='C')
        write_list = np.frombuffer(y_bytes, np.uint16)
        logger.debug(f"Write list element count {len(write_list)}.")
        n_items = len(write_list)

        self._setup_measurement(tia_gain=tia_gain, clear_fifo=True, fifo_start=True)

        # Send and collect data
        i = 0
        params['transmission_st'] = monotonic_ns()

        post_read_attempts = 0
        while (post_read_attempts < 3) or ((params['rd_tx_reg'] / params['wr_tx_reg'] / 2) <1.0):
            st = monotonic_ns()
            if i < n_items: #Writing
                data = write_list[i:i + n_register].tolist()
                try:
                    if (st - params['wr_dly_st'] * 0) > params['busy_dly_ns']:
                        self.device.write_data(REG_WRITE_ADDR_POT, data)
                        params['wr_err_cnt'] = 0
                        params['wr_tx_reg'] += n_register
                        i += n_register
                except minimalmodbus.SlaveReportedException or minimalmodbus.InvalidResponseError:
                    params['wr_dly_st'] = monotonic_ns()
                    params['wr_err_cnt'] += 1
                    if params['wr_err_cnt'] > 10:
                        logger.error('Writing errors exceeded the limit, potentiostat not responding.')
                        raise
            # We need read two times for each write time because adc push two values to FIFO
            for _ in range(0, 2):
                rd_data = self._read_operation(st, params, n_register)
                if rd_data:
                    rd_list = convert_uint16_to_float32(rd_data)
                    data_queue.put(rd_list)
                    params['rd_tx_reg'] += len(rd_data)
                    params['rd_err_cnt'] = 0
            if i >= n_items:
                post_read_attempts += 1

        self._teardown_measurement()

        result_tm = (monotonic_ns() - params['transmission_st']) / 1e9
        data_rate = (2 * params['rx_tx_reg']) / result_tm
        logger.info(f"\nTotal transmission time {result_tm:3.4} s, data rate {(data_rate / 1000):3.4} KBytes/s.\n")
        logger.info(
            f"Send: {params['wr_tx_reg']}, Read: {params['rd_tx_reg']}, Read/Sent/2: {params['rd_tx_reg'] / params['wr_tx_reg'] / 2}\n")
        logger.info(f"Actual points expected to read: {2 * params['wr_tx_reg']}, actual read: {params['rd_tx_reg']}, extra read operations: {int((params['rd_tx_reg'] - params['wr_tx_reg'] * 2)/120)}\n")

