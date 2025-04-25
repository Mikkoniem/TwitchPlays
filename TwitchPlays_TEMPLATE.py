import concurrent.futures
import random
import keyboard
import ctypes
import pyautogui
import TwitchPlays_Connection
from TwitchPlays_KeyCodes import *
import time

##################### GAME VARIABLES #####################

TWITCH_CHANNEL = 'maltzu10'
STREAMING_ON_TWITCH = True
YOUTUBE_CHANNEL_ID = "YOUTUBE_CHANNEL_ID_HERE"
YOUTUBE_STREAM_URL = None

##################### MESSAGE QUEUE VARIABLES #####################

MESSAGE_RATE = 0.5
MAX_QUEUE_LENGTH = 20
MAX_WORKERS = 100

last_time = time.time()
message_queue = []
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
active_tasks = []
pyautogui.FAILSAFE = False

##################### WINDOWS ACTIVE WINDOW CHECK #####################

def get_active_window_title():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value

##################### KEY PRESS FUNCTION #####################

def press_key(hexKeyCode):
    ctypes.windll.user32.keybd_event(hexKeyCode, 0, 0x0000, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(hexKeyCode, 0, 0x0002, 0)

##################### COUNTDOWN BEFORE START #####################

countdown = 5
while countdown > 0:
    print(countdown)
    countdown -= 1
    time.sleep(1)

##################### CONNECT TO TWITCH OR YOUTUBE #####################

if STREAMING_ON_TWITCH:
    t = TwitchPlays_Connection.Twitch()
    t.twitch_connect(TWITCH_CHANNEL)
else:
    t = TwitchPlays_Connection.YouTube()
    t.youtube_connect(YOUTUBE_CHANNEL_ID, YOUTUBE_STREAM_URL)

##################### HANDLE CHAT MESSAGE #####################
def grab():
    HoldKey(Z)
    HoldKey(S)
    time.sleep(0.1)
    ReleaseKey(Z)
    ReleaseKey(S)

def panic():
    HoldAndReleaseKey(S, 0.1)
    HoldAndReleaseKey(UP_ARROW, 0.5)
    HoldAndReleaseKey(S, 0.1)
def high_jump():
    HoldKey(UP_ARROW)
    time.sleep(0.5)
    HoldAndReleaseKey(Z, 0.5)
    time.sleep(0.2)
    ReleaseKey(UP_ARROW)
def left_jump():
    HoldKey(LEFT_ARROW)
    time.sleep(0.5)
    HoldAndReleaseKey(Z, 0.5)
    time.sleep(0.2)
    ReleaseKey(UP_ARROW)
def right_jump():
    HoldKey(RIGHT_ARROW)
    time.sleep(0.5)
    HoldAndReleaseKey(Z, 0.5)
    time.sleep(0.2)
    ReleaseKey(UP_ARROW)

def handle_message(message):
    try:
        msg = message['message'].lower()
        username = message['username'].lower()

        # allowed_initials = ['a', 'b', 'm']
        # if not username[0] in allowed_initials:
        #     print(f"Käyttäjä {username} ei ole sallittu.")
        #     return

        active_window = get_active_window_title()
        print(f"Aktiivinen ikkuna: {active_window}")
        print("Got this message from " + username + ": " + msg)
        if msg == "ljump":
            left_jump()
        if msg == "hjump":
            high_jump()
        if msg == "panic":
                panic()
        if msg =="grab":
            grab()
        if msg == "matias":
            HoldAndReleaseKey(V, 0.1)
        if msg == "left":
            HoldAndReleaseKey(LEFT_ARROW, 0.7)
        if msg == "left2":
            HoldKey(LEFT_ARROW)
        if msg == "right2":
            HoldKey(RIGHT_ARROW)
        if msg == "up2":
            HoldKey(UP_ARROW)
        if msg == "staydown":
            HoldAndReleaseKey(DOWN_ARROW, 3)
        if msg == "stop":
            ReleaseKey(LEFT_ARROW)
            ReleaseKey(RIGHT_ARROW)
            ReleaseKey(DOWN_ARROW)
            ReleaseKey(UP_ARROW)
        if msg == "right":
            HoldAndReleaseKey(RIGHT_ARROW, 0.7)
        if msg == "run":
            HoldAndReleaseKey(UP_ARROW, 0.8)
        if msg == "walk":
            HoldAndReleaseKey(UP_ARROW, 0.4)
        if msg == "up":
            HoldAndReleaseKey(UP_ARROW, 0.1)
        if msg == "down":
            HoldAndReleaseKey(DOWN_ARROW, 4)
        if msg == "down2":
            HoldKey(DOWN_ARROW)
        if msg == "jump":
            HoldAndReleaseKey(Z, 0.1)
        if msg == "square":
            HoldAndReleaseKey(X, 0.1)
        if msg == "spin":
            HoldAndReleaseKey(S, 0.1)
        if msg == "triangle":
            HoldAndReleaseKey(D, 0.1)
        if msg == "tapa":
            HoldKey(Z,0.1),
            ReleaseKey(Z),
            HoldKey(Z,0.1),
            ReleaseKey(Z),
            HoldKey(Z,0.1),
            ReleaseKey(Z),
        if msg == "x":
            HoldAndReleaseKey(Z, 0.1)
  #komennot kuntoon (nimeämiset, ajastus)
    except Exception as e:
        print("Encountered exception: " + str(e))

##################### MAIN LOOP #####################

while True:
    active_tasks = [t for t in active_tasks if not t.done()]

    new_messages = t.twitch_receive_messages()
    if new_messages:
        message_queue += new_messages
        message_queue = message_queue[-MAX_QUEUE_LENGTH:]

    messages_to_handle = []
    if not message_queue:
        last_time = time.time()
    else:
        r = 1 if MESSAGE_RATE == 0 else (time.time() - last_time) / MESSAGE_RATE
        n = int(r * len(message_queue))
        if n > 0:
            messages_to_handle = message_queue[0:n]
            del message_queue[0:n]
            last_time = time.time()

    if keyboard.is_pressed('shift+backspace'):
        print("Suljetaan...")
        exit()

    if not messages_to_handle:
        continue
    else:
        for message in messages_to_handle:
            if len(active_tasks) <= MAX_WORKERS:
                active_tasks.append(thread_pool.submit(handle_message, message))
            else:
                print(f'WARNING: active tasks ({len(active_tasks)}) exceeds number of workers ({MAX_WORKERS}). ({len(message_queue)} messages in the queue)')
