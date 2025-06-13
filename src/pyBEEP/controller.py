from queue import Queue
import numpy as np
import queue
import threading
from time import time_ns
import minimalmodbus
import logging
from typing import Optional, Callable

from .device import PotentiostatDevice
from .logger import DataLogger
from .utils import default_filepath, float_to_uint16_list
from .waveforms import constant_waveform, linear_sweep, cyclic_voltammetry
from .constants import CMD, GAIN, REG_READ_ADDR, REG_WRITE_ADDR_PID, REG_WRITE_ADDR_POT, POINT_INTERVAL_GAL

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

class PotentiostatController:
    def __init__(self, device: PotentiostatDevice):
        self.device = device
        self.last_plot_path = None
        self.device_lock = threading.Lock()
        self._measurement_modes = {
            "CP": {"type": "pid_active"},
            "CA": {"type": "pid_inactive", "waveform_func": constant_waveform},
            "LSV": {"type": "pid_inactive", "waveform_func": linear_sweep},
            "CV": {"type": "pid_inactive", "waveform_func": cyclic_voltammetry}
        }

    def _setup_measurement(self, tia_gain: int, clear_fifo: bool = False, fifo_start: bool = False):
        self.device.send_command(CMD['SET_TIA_GAIN'], tia_gain)
        if clear_fifo:
            self.device.send_command(CMD['CLEAR_FIFO'], 1)
        if fifo_start:
            self.device.send_command(CMD['FIFO_START'], 1)
        self.device.send_command(CMD['SET_SWITCH'], 1)

    def _run_measurement(self, write_func: Callable[[queue.Queue], None], filepath: str):
        data_queue = queue.Queue()
        writer = DataLogger(data_queue, filepath)

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
        with self.device_lock:
            self.device.send_command(CMD["SET_SWITCH"], 0)
            self.device.send_command(CMD["TEST_STOP"], 1)

    def apply_measurement(self, mode: str, *args, tia_gain, filepath = None, **kwargs):
        mode_config = self._measurement_modes[mode.upper()]
        filepath = filepath or default_filepath(mode, *args, tia_gain=tia_gain)

        if mode_config['type'] == 'pid_active':
            current, duration = args
            self._run_measurement(
                lambda q: self._read_write_data_pid_active(q, current, duration, tia_gain),
                filepath)
        elif mode_config["type"] == "pid_inactive":
            waveform = mode_config["waveform_func"](mode, *args, **kwargs)
            self._run_measurement(lambda q: self._read_write_data_pid_inactive(q,waveform, tia_gain), filepath)

        self.last_plot_path = filepath

    def _read_write_data_pid_active(self,
                                   data_queue: Queue,
                                   currents_list: np.array,
                                   tia_gain: Optional[int] = 0,
                                   reducing_factor: Optional[int] = 5,
                                   n_register: Optional[int] = 120,
                                   ) -> None:
        """
        Function that handles the sending commands to the potentiostat and reading
        the output data when using the PID of the potentiostat to apply a fix current.
        The output data is added progressively to the 'data_queue'.

        Args:
            current (float): Current to be applied (in A).
            time (float): Time for the current to be applied (in sec).
            tia_gain (Optional[int]): Gain resistance to use in the transimpedance amplifier. Integers from
                0 to 4 refer to the different resistance from 1 k[Ohm] to 10 M[Ohm].
                This parameter is generally referred in commercial potentiostats as current/potential range.
            reducing_factor (Optional[int]): Factor for reducing data size. Ej, a reducing factor of 2 will average
                every two points to reduce data size to half. Defaults to 5.
            n_register (Optional[float]): Size of data packages sent to the potentiostat. Defaults to 120.

        Behaviour:
            - The current input is converted from np.float32 to uint16
            - The Transimpedance amplifier gain (TIA_GAIN) is initialized to the specified resistance. The FIFO
              is cleared and PID is switch on (which will switch already the FIFO).
            - The write and reading of data is performed in a loop until the time exceeds the input time of
              the measurement. In this loop, a try-except clause is used for both writing and reading. No delays for 
              writing or reading are applied.
            - When read, the output data is converted back from uint16 to np.float32 and added to 'data_queue'.
            - Optionally, before adding the data, a reducing factor can be applied to the data to RAM collapsing
              over time.
            - The 'data_queue' consist of a np.ndarray: A numpy array where each element is a pair of float values:
              [potential (in V), current (in A)]
            - Once the measurement is finished, potentiostat is switched off and adc_data list is returned.

        Notes:
            - Select the TIA_GAIN carefully according to you expected current range of the reaction. If the gian is
              higher than needed (lower resistance), a higher noise level will be assumed unnecessarily. But if the
              gain is set too low (higher resistance), the desired current might not be reached.
            - Unexpected behaviour is observed in first iterations of the while loop: number of reading operations is 
              lower than writing operations. Reading seems to fail for arround 1 to 5 times during first 0.1s.
              For that reason, delays to both operations were removed, which improves the situation but does not solve it.
        """
        self._setup_measurement(tia_gain=tia_gain, clear_fifo=True)

        params = {'busy_dly_ns': 400e6, 'wr_err_cnt': 0, 'rd_err_cnt': 0, 'wr_dly_st': 0,
                  'rd_dly_st': 0, 'rx_tx_reg': 0, 'wr_tx_reg': 0, 'rd_tx_reg': 0, 'transmission_st': time_ns()}

        current_list = values.tobytes(order='C')
        write_list = np.frombuffer(values, np.uint16)
        print(f"Write list element count {len(write_list)}.\n")
        n_items = len(write_list)
        
        # Get target value in uint16
        total_time = 0
        target = np.array([current,], dtype=np.float32).tobytes(order='C')
        target = np.frombuffer(target, np.uint16).tolist()


        # Start sending/collecting
        while total_time < time:
            st = time_ns()
            try:
                try:  # This has been modified since last time, need to be tested properly
                    if (st - params['wr_dly_st']) > params['busy_dly_ns']:
                        self.device.write_data(REG_WRITE_ADDR_PID, [CMD['PID_START']] + target)  # Send data
                        params['wr_err_cnt'] = 0
                        params['wr_tx_reg'] += 1
                except minimalmodbus.SlaveReportedException:
                    params['wr_dly_st'] = time_ns()
                    params['wr_err_cnt'] += 1

                # We need read two times for each write time because adc push two values to FIFO
                for r in range(0, 2):
                    if (st - params['rd_dly_st']) > params['busy_dly_ns']:
                        rd_data = self.device.read_data(REG_READ_ADDR,
                                                             n_register)  # Collect data
                        # Data conversion from uint16 to np.float32
                        adc_words = np.array(rd_data).astype(np.uint16)
                        adc_bytes = adc_words.tobytes()
                        rd_list = np.frombuffer(adc_bytes, np.float32)
                        rd_list = np.reshape(rd_list, (-1, 2))

                        data_queue.put(rd_list)
                        params['rd_tx_reg'] += len(rd_list)
                    else:
                        break
            except minimalmodbus.SlaveReportedException:
                params['rd_dly_st'] = time_ns()
                params['rd_err_cnt'] += 1
            total_time += (time_ns() - st) / 1000000000  # Time passed

        self._teardown_measurement()

        result_tm = (time_ns() - params['transmission_st']) / 1e9
        data_rate = (2 * params['rx_tx_reg']) / result_tm
        logger.info(f"\nTotal transmission time {result_tm:3.4} s, data rate {(data_rate / 1000):3.4} KBytes/s.\n")
        logger.debug(f"Failed writing: {params['wr_err_cnt']}")
        logger.debug(f"Failed reading: {params['rd_err_cnt']}")
        logger.debug(f"Send: {params['wr_tx_reg']}, Read: {params['rd_tx_reg']}, Diff: {params['rd_tx_reg'] - params['wr_tx_reg']*2}\n"
                     f"Time/point: {result_tm / params['wr_tx_reg']}\n")

    def _read_write_data_pid_inactive(self,
                                     data_queue: Queue,
                                     potentials_list: np.array,
                                     tia_gain: Optional[int] = 0,
                                     reducing_factor: Optional[int] = None,
                                     n_register: int = 120,
                                     ) -> None:
        """
        Function that handles sending commands to the potentiostat and reading the output data when using the PID
        of the potentiostat to apply a fixed potential. The output data is added progressively to the 'data_queue'.

        Args:
           potential (float): Potential to be applied (in V).
           time (float): Time for the potential to be applied (in sec).
           tia_gain (Optional[int]): Gain resistance to use in the transimpedance amplifier. Integers from
                0 to 4 refer to the different resistance from 1 k[Ohm] to 10 M[Ohm].
                This parameter is generally referred in commercial potentiostats as current/potential range.
           reducing_factor (Optional[int]): Factor for reducing data size. Ej, a reducing factor of 2 will average
                every two points to reduce data size to half. Defaults to 5.
           n_register (Optional[int]): Size of data packages sent to the potentiostat. Defaults to 120.

        Behaviour:
           - From the input potential, a numpy array is generated with a given length, assuming 0.2 ms interval
             between points. The array is then converted from np.float32 to uint16.
           - The Transimpedance amplifier gain (TIA_GAIN) is initialized to the specified resistance. Then FIFO
             and potentiostat are switched.
           - The writing and reading of data is performed in a loop until all the data list created is sent.
             In this loop, a try-except clause is used for both writing and reading. No delays for writing or reading
             are applied.
           - When reading, the output data is converted back from uint16 to np.float32 and added to 'data_queue'.
           - Optionally, before adding the data, a reducing factor can be applied to the data to RAM collapsing
             over time.
           - The 'data_queue' consist of a np.ndarray: A numpy array where each element is a pair of float values:
             [potential (in V), current (in A)]
           - Once the measurement is finished, potentiostat is switched off and adc_data list is returned.

        Notes:
           - Select the TIA_GAIN carefully according to your expected potential range of the reaction. If the gain
             is higher than needed (lower resistance), a higher noise level will be assumed unnecessarily. But if the
             gain is set too low (higher resistance), the desired potential might not be reached.
           - Unexpected behaviour is observed in first iterations of the while loop: number of reading operations is 
             lower than writing operations. Reading seems to fail for arround 1 to 5 times during first 0.1s.
             For that reason, delays to both operations were removed, which improves the situation but does not solve it.
        """

        params = {'busy_dly_ns': 400e6, 'wr_err_cnt': 0, 'rd_err_cnt': 0, 'wr_dly_st': 0,
                  'rd_dly_st': 0, 'rx_tx_reg': 0, 'wr_tx_reg': 0, 'rd_tx_reg': 0, 'transmission_st': time_ns()}

        # Generate numpy array to send
        y_bytes = potentials_list.tobytes(order='C')
        write_list = np.frombuffer(y_bytes, np.uint16)
        print(f"Write list element count {len(write_list)}.\n")
        n_items = len(write_list)

        self._setup_measurement(tia_gain=tia_gain, fifo_start=True)

        # Send and collect data
        i = 0
        params['transmission_st'] = time_ns()

        post_read_attempts = 0
        while post_read_attempts < 3:
            st = time_ns()
            if i < n_items: #Writing
                data = write_list[i:i + n_register].tolist()
                try:
                    if (st - params['wr_dly_st'] * 0) > params['busy_dly_ns']:
                        self.device.write_data(REG_WRITE_ADDR_POT, data)
                        params['wr_err_cnt'] = 0
                        i += n_register
                        params['rx_tx_reg'] += n_register
                        params['wr_tx_reg'] += n_register
                except minimalmodbus.SlaveReportedException:
                    params['wr_dly_st'] = time_ns()
                    params['wr_err_cnt'] += 1
            try:
                # We need read two times for each write time becase adc push two values to FIFO
                for r in range(0, 2):
                    if (st - params['rd_dly_st'] * 0) > params['busy_dly_ns']:
                        rd_data = self.device.read_data(REG_READ_ADDR,
                                                             n_register)  # Registernumber, number of decimals

                        # Data conversion from uint16 to np.float32
                        adc_words = np.array(rd_data).astype(np.uint16)
                        adc_bytes = adc_words.tobytes()
                        rd_list = np.frombuffer(adc_bytes, np.float32)
                        rd_list = np.reshape(rd_list, (-1, 2))

                        data_queue.put(rd_list)
                        params['rx_tx_reg'] += n_register
                        params['rd_tx_reg'] += n_register
                        params['rd_err_cnt'] = 0
                    else:
                        break
            except minimalmodbus.SlaveReportedException:
                params['rd_dly_st'] = time_ns()
                params['rd_err_cnt'] += 1
            finally:
                if i > n_items:
                    post_read_attempts += 1

        self._teardown_measurement()

        result_tm = (time_ns() - params['transmission_st']) / 1e9
        data_rate = (2 * params['rx_tx_reg']) / result_tm
        logger.info(f"\nTotal transmission time {result_tm:3.4} s, data rate {(data_rate / 1000):3.4} KBytes/s.\n")
        logger.debug(f"Failed writing: {params['wr_err_cnt']}")
        logger.debug(f"Failed reading: {params['rd_err_cnt']}")
        logger.debug(
            f"Send: {params['wr_tx_reg']}, Read: {params['rd_tx_reg']}, Read/Sent/2: {params['rd_tx_reg'] / params['wr_tx_reg'] / 2}\n"
            f"Time/point: {result_tm / params['wr_tx_reg']}\n")
        logger.debug(f"Send: {params['wr_tx_reg']}, Read: {params['rd_tx_reg']}")
        logger.debug(f"Actual points expected to read: {2 * params['wr_tx_reg']}, actual read: {params['rd_tx_reg']}")

