import json
import os

import mss
import pygetwindow as gw
import numpy as np
import cv2
import tkinter as tk
from PIL import Image, ImageTk

# Global variable to hold map region
from matplotlib import pyplot as plt

script_dir = os.path.dirname(os.path.abspath(__file__))
settings_path = os.path.abspath(os.path.join(script_dir, '..', 'settings.json'))


def update_window_list():
    windows = gw.getAllTitles()
    metin_windows = [window for window in windows if 'albion' in window.lower()]
    return metin_windows


def set_hostile_detector(state):
    set_setting('hostile_detector', state)
    print(f"Hostile Detector set to: {state}")


def set_fishing_region(region, selected_window):
    fishing_region = region

    relative_position = (
        fishing_region[0],
        fishing_region[1],
        fishing_region[2],
        fishing_region[3]
    )

    set_setting('fishing_region', relative_position)
    print(f"Fishing region set to: {fishing_region}")


def focus_game_window(window_title):
    print(f"Window title: {window_title}")
    try:
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            window = windows[0]
            window.activate()
            return window
        else:
            print(f"No window found with title: {window_title}")
            return None
    except Exception as e:
        print(f"Error occurred while getting window: {e}")
        return None


def take_screenshot_region(window, region):
    # Calculate coordinates relative to the game window
    left, top, width, height = window.left, window.top, window.width, window.height
    region_left, region_top, region_width, region_height = region

    # Calculate the center of the region
    center_x = left + region_left
    center_y = top + region_top

    bbox = {
        'left': center_x,
        'top': center_y,
        'width': region_width,
        'height': region_height
    }

    with mss.mss() as sct:
        screenshot = sct.grab(bbox)
        img = np.array(screenshot)
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    # save_screenshot(resized_img)

    return gray_image


def take_screenshot(window):
    left, top, width, height = window.left, window.top, window.width, window.height
    bbox = {
        'left': left,
        'top': top,
        'width': width,
        'height': height
    }

    with mss.mss() as sct:
        screenshot = sct.grab(bbox)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    return img


def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)


def save_settings(settings):
    with open(settings_path, "r+") as file:
        data = json.load(file)
        data.update(settings)
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()


def load_settings():
    try:
        with open(settings_path, "r") as file:
            settings = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty/invalid JSON, initialize with default settings
        settings = {
            "fishing_region": None,
            "tolerance": 17,
            # Add more default settings as needed
        }
    return settings


def save_screenshot(image, filename='screenshot.png'):
    try:
        cv2.imwrite(filename, image)
        print(f"Screenshot saved as {filename}")
    except Exception as e:
        print(f"Error saving screenshot: {e}")

