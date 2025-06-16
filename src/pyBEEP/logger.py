import csv
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DataLogger:
    """
    Streams data from a queue to a CSV file, with optional reduction (downsampling) by averaging every N rows.
    Handles arbitrary-sized incoming data blocks and ensures no data is lost, always averaging the specified number of points.
    """

    def __init__(self, queue, filepath: str, reducing_factor: int | None):
        """
        Initialize the DataLogger.

        Args:
            queue: Queue providing data blocks (np.ndarray or list of rows).
            filepath (str): Path to the output CSV file.
            reducing_factor (int | None): If set, will average every N rows before saving. Defaults to None (no reduction).
        """
        self.queue = queue
        self.filepath = filepath
        self.reducing_factor = reducing_factor

    def run(self)->None:
        """
        Continuously reads data blocks from the queue and writes them to a CSV file.
        If reducing_factor is set, averages every N rows before writing.
        Handles arbitrary block sizes and ensures all data is processed without loss.
        When the queue signals completion with None, any remaining data is also written (averaged if needed).
        """
        buffer = []
        with open(self.filepath, mode="w", newline="") as file:
            writer = csv.writer(file)
            while True:
                item = self.queue.get()
                if item is None:
                    break
                buffer.extend(item)
                if len(buffer) > 20:
                    buffer = self._save_batch(writer, buffer)
                    file.flush()
            if buffer:
                self._save_batch(writer, buffer, flush_all=True)
                file.flush()
        logger.info(f"Saved: {self.filepath}")

    def _save_batch(self, writer: csv.writer, buffer: list, flush_all: bool = False) -> list:
        """
        Writes as many reduced (averaged) rows from the buffer as possible to the CSV file.
        Keeps any leftover rows (less than reducing_factor) in the buffer unless flush_all is True.

        Args:
            writer (csv.writer): CSV writer object used for writing rows.
            buffer (list): List of rows (each row is a list or np.ndarray).
            flush_all (bool): If True, averages and writes any leftover rows (even if less than reducing_factor).

        Returns:
            list: The remaining rows in the buffer that were not written out.
        """
        factor = self.reducing_factor
        if not factor or factor < 2:
            for row in buffer:
                writer.writerow(row)
            return []

        idx = 0
        n = len(buffer)
        while n - idx >= factor:
            chunk = np.array(buffer[idx:idx + factor])
            avg = chunk.mean(axis=0)
            writer.writerow(avg.tolist())
            idx += factor

        if flush_all and idx < n:
            chunk = np.array(buffer[idx:])
            avg = chunk.mean(axis=0)
            writer.writerow(avg.tolist())
            idx = n

        return buffer[idx:]