import cv2
import time

import pyautogui
from pywinauto import mouse
from threading import Thread, Event
from bot_inputs.bot_logic import focus_game_window, take_screenshot_region_detected, take_screenshot, load_settings, \
    take_screenshot_region, enhance_image
from PIL import Image, ImageTk
import numpy as np


class FishBot(Thread):
    def __init__(self, window_title, image_label):
        super().__init__()
        self.window_title = window_title
        self.stop_event = Event()
        self.game_window = focus_game_window(self.window_title)
        self.images = {
            'floater': enhance_image(cv2.imread('images/floater.png')),
            'detected': enhance_image(cv2.imread('images/detected.png')),
            'caught': cv2.cvtColor(cv2.imread('images/caught.png'), cv2.COLOR_BGR2GRAY)
        }
        self.image_label = image_label
        self.idle_floater_loc = None
        self.detection_timeout = 30
        self.fishing_region = None

    def run(self):
        if not self.game_window:
            print(f"Could not find game window: {self.window_title}")
            return

        print("Running FishBot module...")
        settings = load_settings()
        self.fishing_region = settings.get('fishing_region')

        self.floater_throw()
        last_detection_time = time.time()

        while not self.stop_event.is_set():
            if self.is_floater_in_water():
                print("> Floater in water, start fishing --")
                self.start_fishing(last_detection_time)
                last_detection_time = time.time()  # Reset detection timer after starting fishing
            else:
                print("-- Floater NOT in water, throwing again --")
                self.floater_throw()
                last_detection_time = time.time()

            if time.time() - last_detection_time > self.detection_timeout:
                print("No action taken for 30 seconds, restarting...")
                last_detection_time = time.time()
                self.floater_throw()

            time.sleep(0.1)

    def start_fishing(self, start_time):
        while True:
            screenshot = take_screenshot_region(self.game_window, self.fishing_region)
            self.update_screenshot_image(screenshot)

            if self.detect_fish(screenshot):
                print("-- Fish detected --")
                self.catch_game()
                time.sleep(2)
                self.floater_throw()
                return  # Exit the method after catching fish and throwing the floater again

            if not self.is_floater_in_water():
                print("Floater is out of the water, throwing again...")
                self.floater_throw()
                return  # Exit the method to re-throw the floater

            if time.time() - start_time > self.detection_timeout:
                print("No fish detected for 30 seconds, restarting fishing process...")
                self.floater_throw()
                return  # Exit the method if no fish detected within timeout

            time.sleep(0.1)

    def stop(self):
        self.stop_event.set()

    def detect_fish(self, bgrSS):
        enhancedGreySS = enhance_image(bgrSS)
        detectedFloater = self.images['detected']

        scales = np.linspace(0.8, 1.5, 7)
        best_val = -np.inf

        for scale in scales:
            resized_template = cv2.resize(detectedFloater, (0, 0), fx=scale, fy=scale)
            result = cv2.matchTemplate(enhancedGreySS, resized_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val > best_val:
                best_val = max_val

        if best_val > 0.70:
            return True
        return False

    def catch_game(self):
        print('Catching..')
        pyautogui.click()
        center_x = self.game_window.left + self.game_window.width // 2
        time.sleep(0.2)
        while True:
            ss = take_screenshot(self.game_window)
            floater_pos = self.detect_floater_game(ss)
            if floater_pos is None:
                print("Floater not detected.")
                break  # Exit if the floater is not detected
            floater_x = self.game_window.left + floater_pos[0]

            if floater_x < center_x + 5:
                pyautogui.mouseDown(button='left')
                while floater_x < center_x + 5:
                    ss = take_screenshot(self.game_window)
                    floater_pos = self.detect_floater_game(ss)
                    if floater_pos is None:
                        break
                    floater_x = self.game_window.left + floater_pos[0]
                pyautogui.mouseUp(button='left')

            if floater_pos is None:
                print("Floater disappeared.")
                break  # Exit if the floater disappears

    def detect_floater_game(self, image, threshold=0.7):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_template = self.images['caught']

        result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            return max_loc
        return None

    def floater_throw(self):
        region = self.fishing_region
        left = region[0] + self.game_window.left + (region[3] // 2)
        top = region[1] + self.game_window.top + (region[2] // 2)

        # Calculate the center of the game window
        game_center_x = left
        game_center_y = top

        # Move the mouse to the center of the game window
        pyautogui.moveTo(game_center_x, game_center_y, duration=0.2)
        pyautogui.mouseDown(button='left')
        time.sleep(0.1)
        pyautogui.mouseUp(button='left')
        pyautogui.moveTo(game_center_x + 50, game_center_y - 50, duration=0.2)
        self.idle_floater_loc = None
        time.sleep(2)

    def is_floater_in_water(self):
        bgrSS = take_screenshot_region(self.game_window, self.fishing_region)
        enhancedGreySS = enhance_image(bgrSS)
        idleFloater = self.images['floater']

        scales = np.linspace(0.8, 1.5, 7)
        best_val = -np.inf
        best_loc = None

        for scale in scales:
            resized_template = cv2.resize(idleFloater, (0, 0), fx=scale, fy=scale)
            result = cv2.matchTemplate(enhancedGreySS, resized_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc

        if best_val > 0.7:
            self.idle_floater_loc = best_loc
            return True

        return False

    def move_mouse_back(self):
        game_center_x = self.game_window.left + self.game_window.width // 2
        game_center_y = self.game_window.top + self.game_window.height // 2
        pyautogui.moveTo(game_center_x // 2, game_center_y // 2, 0.2)

    def update_screenshot_image(self, image):
        img = ImageTk.PhotoImage(image=Image.fromarray(image))
        self.image_label.config(image=img)
        self.image_label.image = img
