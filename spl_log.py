import os
import time
from pathlib import Path

class CSVLogger:
    def __init__(self, directory="measurements", prefix="meas"):
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.filename = Path(directory) / f"{prefix}_{timestamp}.csv"
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        self.first_write = True


    def saveMeas(self, values:dict):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if self.first_write:
            self.first_write = False
            with open(self.filename, 'w') as f:
                f.write("timestamp;")
                for val in values:
                    f.write(val + ";")
                f.write('\n') 
            
        with open(self.filename, 'a') as f:
            f.write(f"{timestamp};")
            for val in values:
                f.write(str(values[val]) + ";")
            f.write('\n') 

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
    measure = CSVLogger(directory="test_measurement")
    item = {"test1": 112, "testval2": 545, "testval3":5555}
    measure.saveMeas(item)
    item = {"test1": 113, "testval2": 546, "testval3":5556}
    measure.saveMeas(item)
    item = {"test1": 114, "testval2": 547, "testval3":5557}
    measure.saveMeas(item)

    logger.log("Measurement ended")
