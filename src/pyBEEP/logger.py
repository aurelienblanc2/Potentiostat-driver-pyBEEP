import csv
from typing import List
import numpy as np


class DataLogger:
    def __init__(self, queue, filepath: str):
        self.queue = queue
        self.filepath = filepath

    def run(self)->None:
        buffer = []
        with open(self.filepath, mode="w", newline="") as file:
            writer = csv.writer(file)
            while True:
                item = self.queue.get()
                if item is None:
                    break
                buffer.append(item)
                if len(buffer) > 20:
                    self._save_batch(buffer, writer)
                    buffer.clear()
                    file.flush()
            if buffer:
                self._save_batch(buffer, writer)
                file.flush()
        print(f"Saved: {self.filepath}")

    @staticmethod
    def _save_batch(batch: List[np.ndarray], writer: csv.writer):
        """
        Writes a batch of data to a CSV file using the provided writer object.

        Args:
            batch (list): A list of items, where each item is expected to be iterable (e.g., a list or tuple of rows).
            writer (csv.writer): A CSV writer object used to write rows to the file.
        """
        for block in batch:
            for row in block:
                writer.writerow(row)