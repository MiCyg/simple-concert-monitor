from SPL_meter import SPL_Meter_Manager
from guizero import App, PushButton, Text, Box, TextBox
from keyboard import NumericKeyboard

import threading
import math
from queue import Queue, Empty
from spl_log import CSVLogger, Logger
from config_mng import ConfigurationManager


meas_logger = CSVLogger(directory="measurements", prefix="spl")
debug = Logger(directory="debug", prefix="log")


debug.log("Starting concert SPL monitor application")
spl_queue = Queue(5)
do_reset_queue = Queue(1)

default_measConfig = {
    "calibration_level": 94.0,
    "calibration_correction_value": 0.0,
    "sensitivity_dbfs": -26.0,
    "sample_rate": 48000,
    "timeweighting": 0.125
}
default_sdConfig = {
    "device": 1,
    "channels": 1
}
measConfig = ConfigurationManager("config/meas.json", default_measConfig)
soundDeviceConfig = ConfigurationManager("config/sounddevice.json", default_sdConfig)
measurement_manager = SPL_Meter_Manager(measConfig.get_config(), soundDeviceConfig.get_config())


debug.log("Start measurement thread")
meas_thread = threading.Thread(target=measurement_manager.measure_SPL, args=(spl_queue,do_reset_queue,), daemon=True)
meas_thread.start()

color_active = "#00E626"
color_active_weighing = "#162bfa"
danger_color = "#ed1e1e"

def set_a():
    a_button.text_color=color_active_weighing
    lin_button.text_color="#ffffff"

def set_lin():
    a_button.text_color="#ffffff"
    lin_button.text_color=color_active_weighing


def set_instant():
    one_button.text_color="#ffffff"
    fifteen_button.text_color="#ffffff"
    instant_button.text_color=color_active

def set_minute():
    one_button.text_color=color_active
    fifteen_button.text_color="#ffffff"
    instant_button.text_color="#ffffff"

def set_fifteen():
    one_button.text_color="#ffffff"
    fifteen_button.text_color=color_active
    instant_button.text_color="#ffffff"

def reset_avg():
    if do_reset_queue.empty():
     do_reset_queue.put_nowait(True)
     text.value=f"{0:.1f}"

def get_data(queue):
    time=""
    weigh=""

    if fifteen_button.text_color==color_active: time="fifteen_mins"
    if one_button.text_color==color_active: time="minute"
    if instant_button.text_color==color_active: time="instant"

    if a_button.text_color==color_active_weighing: weigh="a"
    if lin_button.text_color==color_active_weighing: weigh="lin"

    value_to_get = f"{weigh}_{time}"
    try:
        item = queue.get_nowait()
    except Empty:
        print("empty")
    else:
        meas_logger.saveMeas(item)  
        value = item.get(value_to_get, 0)
        debug.log(value)
        if math.isnan(value): value=0
        if weigh=="a" and (time=="fifteen_mins" or time=="minute") and value>=100: text.text_color=danger_color
        if value<100: text.text_color=color_active
        if value != 0: text.value=f"{value:.1f}"     

        queue.task_done()


    
def OpenAccespoint():
    # TODO create accespoint which automatically off after x minutes
    pass

config_fields = [
    "calibration_level",
    "calibration_correction_value",
    "sensitivity_dbfs",
    "sample_rate",
    "timeweighting",
]

config_entries = {}

def show_config():
    config = measurement_manager.get_meas_config()
    for field in config_fields:
        config_entries[field].value = str(config.get(field, ""))

    main_view.hide()
    config_view.show()

def save_config():
    new_config = {}

    for field in config_fields:
        value = config_entries[field].value

        if field in ["calibration_level", "calibration_correction_value", "sensitivity_dbfs", "timeweighting"] :
            try:
                new_config[field] = float(value)
            except:
                new_config[field] = 0.0

        elif field == "sample_rate":
            try:
                new_config[field] = int(value)
            except:
                new_config[field] = 48000

        else:
            new_config[field] = value

    measurement_manager.set_meas_config(new_config)
    measConfig.save_config(new_config)

    config_view.hide()
    main_view.show()




app = App(title="Concert audio monitor", bg="#000000",  )
main_view = Box(app, width="fill", height="fill")

# main view 

level_indic_box = Box(main_view, align="top", width="fill")

top_pad = Box(level_indic_box, height=100, width="fill", align="top")

text_box = Box(level_indic_box, align="top", width="fill")

text = Text(text_box, text="0", color=color_active, align="top",width="fill", size=300)
text.repeat(1000, lambda: get_data(spl_queue))  

botom_pad = Box(level_indic_box, height=0, width="fill", align="bottom")

buttons_box = Box(main_view, layout="grid")

reset_button = PushButton(buttons_box, command=reset_avg, text="Reset averaging", grid=[0,0], padx=30, pady=30)

instant_button = PushButton(buttons_box, command=set_instant, text="Instant SPL", grid=[1,0], padx=80, pady=30)
one_button = PushButton(buttons_box, command=set_minute, text="1 minute average", grid=[2,0], padx=30, pady=30)
fifteen_button = PushButton(buttons_box, command=set_fifteen, text="15 minute average", grid=[3,0], padx=30, pady=30)

spacer_box = Box(buttons_box, width=50, height="fill", grid=[4,0])

buttons_filters_box = Box(main_view, layout="grid")

a_button = PushButton(buttons_filters_box, command=set_a, text="A weighing", grid=[0,0], padx=30, pady=30)
lin_button = PushButton(buttons_filters_box, command=set_lin, text="Z weighing", grid=[1,0], padx=30, pady=30)

buttons_config_box = Box(main_view, layout="grid")

config_button = PushButton(buttons_config_box, command=show_config, text="Configuration", grid=[0,0], padx=30, pady=30)
config_button.text_color = "#ffffff"
config_button.text_size = 20

AP_button = PushButton(buttons_config_box, command=OpenAccespoint, text="GetFiles", grid=[1,0], padx=30, pady=30)
AP_button.text_color = "#ffffff"
AP_button.text_size = 20


config_view = Box(app, width="fill", height="fill", visible=False)
config_settings_box = Box(config_view, grid=[0,0], width="fill")
config_keyboard_box = Box(config_view, grid=[0,1], width="fill")

keyboard = NumericKeyboard(config_keyboard_box)
#  config view 

for i, field in enumerate(config_fields):
    entry_box = Box(config_settings_box, height=80, layout="grid", grid=[0, i], width=500)

    label = Text(entry_box, text=field, color="white", grid=[0, 0], width="fill", height="fill")
    label.text_size = 20

    config_entries[field] = TextBox(entry_box,  grid=[0, 1], width="fill", height="fill", align="bottom")
    config_entries[field].bg = "#111111"
    config_entries[field].text_color = "#ffffff"
    config_entries[field].text_size = 20

    keyboard.attach(config_entries[field])


cancel_button = PushButton(
    config_settings_box,
    text="Cancel",
    command=lambda: (config_view.hide(), main_view.show()),
    grid=[0, len(config_fields)],
    width=20
)

ok_button = PushButton(
    config_settings_box,
    text="OK",
    command=save_config,
    grid=[1, len(config_fields)],
    width=20
)

ok_button.text_color = "#ffffff"
ok_button.text_size = 20

cancel_button.text_color = "#ffffff"
cancel_button.text_size = 20





instant_button.text_color=color_active
instant_button.text_size=20

one_button.text_color="#ffffff"
one_button.text_size=20

fifteen_button.text_color="#ffffff"
fifteen_button.text_size=20

reset_button.text_color="#ffffff"
reset_button.text_size=20

a_button.text_color=color_active_weighing
a_button.text_size=20

lin_button.text_color="#ffffff"
lin_button.text_size=20

debug.log("Set up complete, displaying app")
app.set_full_screen()
app.display()
