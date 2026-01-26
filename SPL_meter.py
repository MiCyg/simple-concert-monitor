from time import sleep
from queue import Empty, Queue
import sounddevice as sd
import numpy as np
from A_weighting import A_weighting 
from numpy import mean, square, log10, percentile, frombuffer, sqrt
import os
from scipy.signal import lfilter

class SPL_Meter_Manager:
    """This is the class responsible for recording sound levels and passing them to a queue.
    """ 
    l_dbs = []
    a_dbs = []
    reference_level = 94
    calibration = 0
    sampling_rate = 48000
    sensitivity = -26
    timeweighting = 0.125

    frame_counter=0
    max_frame_count = 0

    def __init__(self, sound_config, sd_config) -> None:
        #ładowanie ustawień
        self.reference_level = float(sound_config.get("calibration_level", 94))
        self.calibration = float(sound_config.get("calibration_correction_value", 0))
        self.sensitivity = float(sound_config.get("sensitivity_dbfs", -26))
        self.sampling_rate = int(sound_config.get("sample_rate", 48000))
        self.timeweighting = float(sound_config.get("timeweighting", 0.125)) #domyślnie stała czasowa fast

        self.sddevicenum=int(sd_config.get("device", 1))
        self.sdchannel = int(sd_config.get("channels", 1))



        #zerowanie wyników
        self.max_frame_count = int(60*15*1/self.timeweighting) # zakladam max czas usredniania jako 15 minut
        self.l_dbs = []
        self.a_dbs = []

    def callback(self, indata, frames, time, status):
        if any(indata):
            max_lvl = self.reference_level - self.sensitivity

            data_input=indata[:,0]
            l_data = data_input - np.mean(data_input)

            b, a = A_weighting(self.sampling_rate)
            a_data = lfilter(b, a, l_data)

            l_db = max_lvl + 20*np.log10(np.mean(np.sqrt(l_data**2))) + self.calibration
            a_db = max_lvl + 20*np.log10(np.mean(np.sqrt(a_data**2))) + self.calibration

            self.l_dbs.append(l_db)
            self.a_dbs.append(a_db)
        
            if(len(self.l_dbs)>=self.max_frame_count): 
                self.l_dbs.pop(0)
                self.a_dbs.pop(0)       
        else:
            print('no input')

    # def save_csv(self, measurement_time, leq, laeq):
    #     path = os.path.join(self.path,"SPL_"+str(measurement_time.date())+".csv")
    #     f_object = open(path, 'a')
    #     f_object.write("{},{:.2f},{:.2f}\n".format(
    #                 measurement_time, leq,  laeq))
    #     f_object.close()

    def measure_SPL(self, spl_queue, do_reset_queue):
        CHANNEL = 1 #To NIE zmienia się w naszej konfiguracji. Jeśli zmienił się model mikrofonu i nie działa, to tutaj można szukać winnego
        with sd.InputStream(device=self.sddevicenum, channels=self.sdchannel, callback=self.callback,
                        blocksize=int(self.sampling_rate * self.timeweighting),
                        samplerate=self.sampling_rate):
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
                    "lin_instant":20*np.log10(np.mean(10**(lin_npy[-int(1/self.timeweighting):]/20))),
                    "lin_minute":20*np.log10(np.mean(10**(lin_npy[-int(60/self.timeweighting):]/20))),
                    "lin_fifteen_mins":20*np.log10(np.mean(10**(lin_npy[-int(900/self.timeweighting):]/20))),
                    "a_instant":20*np.log10(np.mean(10**(a_npy[-int(1/self.timeweighting):]/20))),
                    "a_minute":20*np.log10(np.mean(10**(a_npy[-int(60/self.timeweighting):]/20))),
                    "a_fifteen_mins":20*np.log10(np.mean(10**(a_npy[-int(900/self.timeweighting):]/20)))
                }
                spl_queue.put(out_dict)
                # print(out_dict)



if __name__=="__main__":
    print(sd.query_devices())
    spl_met = SPL_Meter_Manager({})
    spl_met.measure_SPL(Queue(), Queue())
