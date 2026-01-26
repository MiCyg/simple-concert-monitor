import os
import time
from pathlib import Path

class SPLLogger:
    def __init__(self, directory="measurements", prefix="meas", header="Timestamp;SPL[dB]"):
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.filename = Path(directory) / f"{prefix}_{timestamp}.csv"

        self.filename.parent.mkdir(parents=True, exist_ok=True)

        with open(self.filename, 'w') as f:
            f.write(f"{header}\n")

    def saveMeas(self, spl_value):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(self.filename, 'a') as f:
            f.write(f"{timestamp};{spl_value:.2f}\n")

class Logger:
    def __init__(self, directory="log", prefix="log", header=""):
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.filename = Path(directory) / f"{prefix}_{timestamp}.log"

        self.filename.parent.mkdir(parents=True, exist_ok=True)

        with open(self.filename, 'w') as f:
            f.write(f"{header}\n")

    def log(self, log_message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(self.filename, 'a') as f:
            f.write(f"{timestamp}: {log_message}\n")

if __name__ == "__main__":
    logger = Logger(directory="log")
    logger.log("Measurement started")
    measure = SPLLogger(directory="test_measurement")
    measure.saveMeas(12.3)
    measure.saveMeas(111.1)
    logger.log("Measurement ended")
