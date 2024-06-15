import cv2
import time

import pyautogui
from pywinauto import mouse
import random
from pywinauto.keyboard import send_keys
from threading import Thread, Event
from bot_inputs.bot_logic import focus_game_window, take_screenshot_region, take_screenshot, load_settings

def press_space():
    send_keys('{SPACE down}')
    press_duration = random.uniform(0.1, 0.2)
    print("Hit Space")
    time.sleep(press_duration)
    send_keys('{SPACE up}')


class FishBot(Thread):
    def __init__(self, window_title):
        super().__init__()
        self.window_title = window_title
        self.stop_event = Event()
        self.game_window = focus_game_window(self.window_title)
        self.images = {
            'floater': cv2.imread('images/floater.png'),
            'idle': cv2.imread('images/idle.png'),
            'detected': cv2.imread('images/detected.png'),
            'detected1': cv2.imread('images/detected1.png'),
            'caught': cv2.imread('images/caught.png')
        }
        self.locations = {}

    def run(self):
        if not self.game_window:
            print(f"Could not find game window: {self.window_title}")
            return

        print("Running FishBot module...")
        settings = load_settings()
        fishing_region = settings.get('fishing_region')
        self.floater_throw(fishing_region)
        last_detection_time = time.time()
        detection_timeout = 30

        while not self.stop_event.is_set():
            screenshot = take_screenshot_region(self.game_window, fishing_region)
            if self.detect_fish(screenshot):
                print("-- Fish detected --")
                self.catch_game()
                time.sleep(2)
                self.floater_throw(fishing_region)
                last_detection_time = time.time()
            else:
                if time.time() - last_detection_time > detection_timeout:
                    print("No fish detected for 30 seconds, restarting...")
                    last_detection_time = time.time()
                    self.floater_throw(fishing_region)
            time.sleep(0.1)

    def stop(self):
        self.stop_event.set()

    def detect_fish(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(self.images['detected1'], cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val > 0.6:
            print(max_val)

        # cv2.imshow('Result', result)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        if max_val >= 0.75:
            return True
        return False

    def catch_game(self):
        center_x = self.game_window.left + self.game_window.width // 2
        pyautogui.click()
        time.sleep(0.3)
        print('Catching..')
        while True:
            ss = take_screenshot(self.game_window)
            floater_pos = self.detect_floater_game(ss)
            if floater_pos is None:
                print("Floater not detected.")
                break  # Exit if the floater is not detected
            floater_x = self.game_window.left + floater_pos[0]

            if floater_x < center_x+5:
                pyautogui.mouseDown(button='left')
                while floater_x < center_x+5:
                    ss = take_screenshot(self.game_window)
                    floater_pos = self.detect_floater_game(ss)
                    if floater_pos is None:
                        break
                    floater_x = self.game_window.left + floater_pos[0]
                pyautogui.mouseUp(button='left')

            if floater_pos is None:
                print("Floater disappeared.")
                break  # Exit if the floater disappears

    def detect_floater_game(self, image, threshold=0.8):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(self.images['caught'], cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            return max_loc
        return None

    def click_on_detected(self, item_name):
        x, y = self.locations[item_name]
        window_left, window_top = self.game_window.left, self.game_window.top
        pyautogui.moveTo(window_left + x, window_top + y, 0.2)
        mouse.click(button='right', coords=(window_left + x, window_top + y))
        self.move_mouse_back()

    def click_image(self, name, button):
        window_left, window_top = self.game_window.left, self.game_window.top
        x, y = self.locations[name]
        click_pos = (window_left + x, window_top + y)
        pyautogui.moveTo(click_pos, duration=0.1)
        mouse.click(button=button, coords=click_pos)

    def floater_throw(self, region):
        left = region[0] + self.game_window.left + (region[3] // 2)
        top = region[1] + self.game_window.top + (region[2] // 2)

        # Calculate the center of the game window
        game_center_x = left
        game_center_y = top

        # Move the mouse to the center of the game window
        pyautogui.moveTo(game_center_x, game_center_y, duration=0.2)
        pyautogui.mouseDown(button='left')
        time.sleep(0.3)
        pyautogui.mouseUp(button='left')
        pyautogui.moveTo(game_center_x + 50, game_center_y - 50, duration=0.2)

    def move_mouse_back(self):
        game_center_x = self.game_window.left + self.game_window.width // 2
        game_center_y = self.game_window.top + self.game_window.height // 2
        pyautogui.moveTo(game_center_x // 2, game_center_y // 2, 0.2)
