# capcut_yt_toggle.py  (v2)
# Install first:  pip install pynput psutil
#
# Test key press only (no mouse interaction):  python capcut_yt_toggle.py test
# Real usage:                                   python capcut_yt_toggle.py
import ctypes
import sys
import threading
import time
from ctypes import wintypes

import psutil
from pynput import keyboard, mouse

# ====== Configuration ======
DELAY = 2                   # Seconds to wait before the second press
PROCESS_NAME = "capcut.exe"   # Lowercase process name (test with VS Code using "code.exe")
ZONE = (929, 523, 972, 560)   # Play button area in CapCut (x1, y1, x2, y2)
PRINT_POS = True              # Display click coordinates
STOP_KEY = keyboard.Key.f12   # Key to exit the script
# ===========================

user32 = ctypes.WinDLL("user32", use_last_error=True)
VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002

playing = False   # Is the video in CapCut currently playing?
pending = None    # The timer currently waiting (if any)


def toggle_youtube():
    """Send Media Play/Pause key directly via Windows API"""
    scan = user32.MapVirtualKeyW(VK_MEDIA_PLAY_PAUSE, 0)
    user32.keybd_event(VK_MEDIA_PLAY_PAUSE, scan, KEYEVENTF_EXTENDEDKEY, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_MEDIA_PLAY_PAUSE, scan,
                       KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
    print("-> Media Play/Pause key sent")


def active_process_name():
    hwnd = user32.GetForegroundWindow()
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    try:
        return psutil.Process(pid.value).name().lower()
    except psutil.Error:
        return ""


def in_zone(x, y):
    if ZONE is None:
        return True
    x1, y1, x2, y2 = ZONE
    return x1 <= x <= x2 and y1 <= y <= y2


def on_click(x, y, button, pressed):
    global playing, pending
    if not pressed or button != mouse.Button.left:
        return
    if PRINT_POS:
        print(f"Clicked at ({x}, {y}) | Process: {active_process_name()}")
    if active_process_name() != PROCESS_NAME:
        return

    if not playing:
        # Video is paused: must click inside the ZONE (Play button) only
        if not in_zone(x, y):
            return
        playing = True
        if pending is not None and pending.is_alive():
            # Pressed Play again before the delay finished: cancel the wait, YouTube remains paused
            pending.cancel()
            pending = None
            print("Wait canceled (YouTube remains paused)")
        else:
            toggle_youtube()                  # First click: immediately
    else:
        # Video is playing: clicking anywhere in CapCut means pause
        playing = False
        print(f"Waiting {DELAY} seconds...")
        pending = threading.Timer(DELAY, toggle_youtube)
        pending.start()                       # Second click: wait first


def on_press(key):
    if key == STOP_KEY:
        print("Closing script")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Test mode: Will send Play/Pause key in 3 seconds (Open YouTube to see if it pauses)")
        time.sleep(3)
        toggle_youtube()
        sys.exit()

    print(f"Ready | Target process: {PROCESS_NAME} | Press F12 to exit")
    with mouse.Listener(on_click=on_click) as ml, \
            keyboard.Listener(on_press=on_press) as kl:
        kl.join()
        ml.stop()
