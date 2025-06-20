import csv
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DataLogger:
    """
    Streams data from a queue to a CSV file, with optional reduction (downsampling) by averaging every N rows.
    Handles arbitrary-sized incoming data blocks and ensures no data is lost, always averaging the specified number of points.
    """

    def __init__(self, queue, waveform: dict, filepath: str, reducing_factor: int | None, ):
        """
        Initialize the DataLogger.

        Args:
            queue: Queue providing data blocks (np.ndarray or list of rows).
            waveform (dict): Dictionary containing waveform metadata, e.g., applied potentials or currents.
            filepath (str): Path to the output CSV file.
            reducing_factor (int | None): If set, will average every N rows before saving. Defaults to None (no reduction).
        """
        self.queue = queue
        self.filepath = filepath
        self.reducing_factor = reducing_factor
        self.waveform = waveform
        self.metadata_keys = list(waveform.keys())

    def run(self)->None:
        """
        Continuously reads data blocks from the queue and writes them to a CSV file.
        If reducing_factor is set, averages every N rows before writing.
        Handles arbitrary block sizes and ensures all data is processed without loss.
        When the queue signals completion with None, any remaining data is also written (averaged if needed).
        """
        buffer = []
        data_idx = 0
        with open(self.filepath, mode="w", newline="") as file:
            header = ["Current (A)", "Potential (V)"]
            header = header + self.metadata_keys if self.waveform else header
            writer = csv.writer(file)
            writer.writerow(header)
            while True:
                item = self.queue.get()
                if item is None:
                    break
                buffer.extend(item)
                if len(buffer) > 20:
                    buffer, data_idx = self._save_batch(writer, buffer, data_idx)
                    file.flush()
            if buffer:
                self._save_batch(writer, buffer, data_idx, flush_all=True)
                file.flush()
        logger.info(f"Saved: {self.filepath}")

    def _save_batch(self, writer: csv.writer, buffer: list, data_idx: int, flush_all: bool = False) -> tuple:
        """
        Enriches the buffer with waveform metadata (if present) and writes as many reduced (averaged) rows as possible to the CSV file.
        Keeps any leftover rows (less than reducing_factor) in the buffer unless flush_all is True.

        Args:
            writer (csv.writer): CSV writer object used for writing rows.
            buffer (list): List of measured rows (each row is a list or np.ndarray).
            data_idx (int): Current offset into waveform arrays.
            flush_all (bool): If True, averages and writes any leftover rows (even if less than reducing_factor).

        Returns:
            tuple: (remaining buffer as list, updated data_idx)
        """
        factor = self.reducing_factor
        n = len(buffer)
        new_idx = data_idx + n
        measured = np.array(buffer)
        rows_to_write = []
        enriched_cols = []
        if self.waveform:
            for key in self.metadata_keys:
                #If key has any mayus
                if key[0].isupper():
                    arr = self.waveform[key][data_idx:new_idx]
                    arr = np.asarray(arr).reshape(-1, 1)
                    enriched_cols.append(arr)
        enriched_buffer = np.hstack([measured] + enriched_cols)

        if not factor or factor < 2:
            for row in enriched_buffer:
                writer.writerow(row)
            return [], new_idx
        else:
            idx = 0
            n = len(buffer)
            while n - idx >= factor:
                chunk = np.array(enriched_buffer[idx:idx + factor])
                avg = chunk.mean(axis=0)
                writer.writerow(avg.tolist())
                idx += factor

            if flush_all and idx < n:
                chunk = np.array(enriched_buffer[idx:])
                avg = chunk.mean(axis=0)
                writer.writerow(avg.tolist())
                idx = n

        return buffer[idx:], new_idx - idx