"""
random_wallpaper.pyw
Picks a random image from a folder and sets it as the Windows desktop background.
Meant to be run silently (via pythonw.exe) at login.
"""

import os
import random
import ctypes
import sys

# ---- CONFIG: change this to your actual wallpaper folder ----
WALLPAPER_FOLDER = r"" #your wallpaper folder path **********************************************

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02


def log_error(message):
    """Write errors to a log file next to the script, since there's no console."""
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wallpaper_log.txt")
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception:
        pass  # if even logging fails, just give up silently


def get_random_image(folder):
    if not os.path.isdir(folder):
        log_error(f"Folder not found: {folder}")
        return None

    images = [
        f for f in os.listdir(folder)
        if f.lower().endswith(VALID_EXTENSIONS)
    ]

    if not images:
        log_error(f"No valid images found in: {folder}")
        return None

    chosen = random.choice(images)
    return os.path.join(folder, chosen)


def set_wallpaper(image_path):
    abs_path = os.path.abspath(image_path)
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        abs_path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    if result == 0:
        log_error(f"SystemParametersInfoW failed for: {abs_path}")
        return False
    return True


def main():
    image_path = get_random_image(WALLPAPER_FOLDER)
    if image_path is None:
        sys.exit(1)

    success = set_wallpaper(image_path)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
