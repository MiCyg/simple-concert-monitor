from SPL_meter import SPL_Meter_Manager
from guizero import App, PushButton, Text, Box
import threading
import math
from queue import Queue, Empty
from spl_log import SPLLogger, Logger


meas_logger = SPLLogger(directory="measurements", prefix="spl")
debug = Logger(directory="debug", prefix="log")

debug.log("Starting concert SPL monitor application")
spl_queue = Queue(5)
do_reset_queue = Queue(1)
# TODO dodać wczytywanie ustawień z plików json
measurement_manager = SPL_Meter_Manager({}, {})

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
        value = item.get(value_to_get, 0)
        if math.isnan(value): value=0
        if weigh=="a" and (time=="fifteen_mins" or time=="minute") and value>=100: text.text_color=danger_color
        if value<100: text.text_color=color_active
        if value != 0: text.value=f"{value:.1f}"     
        meas_logger.saveMeas(value)   
        queue.task_done()

app = App(title="Concert audio monitor", bg="#000000",  )
whole_app_box = Box(app, align="bottom", height="fill", width="fill")

level_indic_box = Box(whole_app_box, align="top", width="fill")

top_pad = Box(level_indic_box, height=100, width="fill", align="top")

text_box = Box(level_indic_box, align="top", width="fill")

text = Text(text_box, text="0", color=color_active, align="top",width="fill", size=300)
text.repeat(1000, lambda: get_data(spl_queue))  

botom_pad = Box(level_indic_box, height=0, width="fill", align="bottom")

buttons_box = Box(whole_app_box, layout="grid")

reset_button = PushButton(buttons_box, command=reset_avg, text="Reset averaging", grid=[0,0], padx=30, pady=30)

instant_button = PushButton(buttons_box, command=set_instant, text="Instant SPL", grid=[1,0], padx=80, pady=30)
one_button = PushButton(buttons_box, command=set_minute, text="1 minute average", grid=[2,0], padx=30, pady=30)
fifteen_button = PushButton(buttons_box, command=set_fifteen, text="15 minute average", grid=[3,0], padx=30, pady=30)

spacer_box = Box(buttons_box, width=50, height="fill", grid=[4,0])

buttons_filters_box = Box(whole_app_box, layout="grid")

a_button = PushButton(buttons_filters_box, command=set_a, text="A weighing", grid=[0,0], padx=30, pady=30)
lin_button = PushButton(buttons_filters_box, command=set_lin, text="Z weighing", grid=[1,0], padx=30, pady=30)

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
