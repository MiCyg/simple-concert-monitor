from time import sleep
from queue import Empty, Queue
import sounddevice as sd
import numpy as np
from A_weighting import A_weighting 
from numpy import mean, square, log10, percentile, frombuffer, sqrt
import os
from scipy.signal import lfilter

class SPL_Meter_Manager:
    """
    This is the class responsible for recording sound levels and passing them to a queue.
    """ 

    REFERENCE_LEVEL_NAME = "calibration_level"
    CALIBRATION_LEVEL_NAME = "calibration_correction_value"
    SENSITIVITY_NAME = "sensitivity_dbfs"
    SAMPLE_RATE_NAME = "sample_rate"
    TIMEWEIGHTING_NAME = "timeweighting"

    DEVICE_NUM_NAME = "device"
    CHANNELS_NUM_NAME = "channels"

    def __init__(self, meas_config:dict=None, sd_config:dict=None) -> None:
        #ładowanie ustawień
        self.meas_config = meas_config
        self.sd_config = sd_config

        #zerowanie wyników
        self.max_frame_count = int(60*15*1/self.meas_config[self.TIMEWEIGHTING_NAME]) # zakladam max czas usredniania jako 15 minut
        self.l_dbs = []
        self.a_dbs = []
        self.update_config = False

        print("configs:")
        print("sd:")
        print(self.sd_config)
        print("meas:")
        print(self.meas_config)
    
    def set_meas_config(self, meas_config:dict):
        self.meas_config = meas_config
        self.update_config = True

    def get_meas_config(self) -> dict:
        return self.meas_config

    def update_sounddevice_config(self, sd_config):
        self.sd_config = sd_config
        self.update_config = True
        

    def callback(self, indata, frames, time, status):
        if any(indata):
            reference_level = self.meas_config[self.REFERENCE_LEVEL_NAME]
            calibration = self.meas_config[self.CALIBRATION_LEVEL_NAME]
            sensitivity = self.meas_config[self.SENSITIVITY_NAME]
            sampling_rate = self.meas_config[self.SAMPLE_RATE_NAME]
            

            max_lvl = reference_level - sensitivity

            data_input=indata[:,0]
            l_data = data_input - np.mean(data_input)

            b, a = A_weighting(sampling_rate)
            a_data = lfilter(b, a, l_data)

            l_db = max_lvl + 20*np.log10(np.mean(np.sqrt(l_data**2))) + calibration
            a_db = max_lvl + 20*np.log10(np.mean(np.sqrt(a_data**2))) + calibration

            self.l_dbs.append(l_db)
            self.a_dbs.append(a_db)
        
            if(len(self.l_dbs)>=self.max_frame_count): 
                self.l_dbs.pop(0)
                self.a_dbs.pop(0)       
        else:
            print('no input')


    def measure_SPL(self, spl_queue, do_reset_queue):
        while True:
            timeweighting = self.meas_config[self.TIMEWEIGHTING_NAME]
            sample_rate = self.meas_config[self.SAMPLE_RATE_NAME]
            sdchannel = self.sd_config[self.CHANNELS_NUM_NAME]
            sddevicenum = self.sd_config[self.DEVICE_NUM_NAME]
            print("settings")
            print(timeweighting)
            print(sdchannel)
            print(sddevicenum)
            print(sample_rate)

            with sd.InputStream(device=sddevicenum, channels=sdchannel, callback=self.callback,
                            blocksize=int(sample_rate * timeweighting),
                            samplerate=sample_rate):
                while True:
                    sleep(1)
                    if not do_reset_queue.empty():
                        item = do_reset_queue.get_nowait()
                        if item==True:
                            print('Resetting average')
                            self.l_dbs = []
                            self.a_dbs = []
                            do_reset_queue.task_done()
                
                    lin_npy = np.array(self.l_dbs)
                    a_npy = np.array(self.a_dbs)
                    out_dict = {
                        "lin_instant":20*np.log10(np.mean(10**(lin_npy[-int(1/timeweighting):]/20))),
                        "lin_minute":20*np.log10(np.mean(10**(lin_npy[-int(60/timeweighting):]/20))),
                        "lin_fifteen_mins":20*np.log10(np.mean(10**(lin_npy[-int(900/timeweighting):]/20))),
                        "a_instant":20*np.log10(np.mean(10**(a_npy[-int(1/timeweighting):]/20))),
                        "a_minute":20*np.log10(np.mean(10**(a_npy[-int(60/timeweighting):]/20))),
                        "a_fifteen_mins":20*np.log10(np.mean(10**(a_npy[-int(900/timeweighting):]/20)))
                    }
                    spl_queue.put(out_dict)
                    
                    # reload config if changed
                    if self.update_config:
                        self.update_config = False
                        break


if __name__=="__main__":
    from config_mng import ConfigurationManager 
    print(sd.query_devices())
    
    measConfig = ConfigurationManager("config/meas.json")
    soundDeviceConfig = ConfigurationManager("config/sounddevice.json")
    spl_met = SPL_Meter_Manager(measConfig.get_config(), soundDeviceConfig.get_config())

    spl_met.measure_SPL(Queue(), Queue())
