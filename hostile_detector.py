import os
from threading import Thread, Event
import time

import cv2
import telebot
import numpy as np
from bot_inputs.bot_logic import focus_game_window, take_screenshot, detect_image
from PIL import ImageGrab
from dotenv import load_dotenv

load_dotenv()


class HostileDetector(Thread):
    def __init__(self, game_title):
        super().__init__()
        self.game_window = focus_game_window(game_title)
        self.stop_event = Event()
        self.hostilePicture = None
        self.images = {
            'hostile_hb': cv2.imread('images/hostile_hb.png'),
            'hostile_ic': cv2.imread('images/hostile_ic.png')
        }
        self.locations = {}
        self.credentials = {
            'bot_token': os.getenv('BOT_TOKEN'),
            'chat_id': os.getenv('CHAT_ID')
        }

    def run(self):
        if not self.game_window:
            print(f"Could not find game window")
            return
        print("Running Hostile Detector module...")

        while not self.stop_event.is_set():
            self.detect_hostile()
            self.detect_local_message()
            time.sleep(1)

    def stop(self):
        self.stop_event.set()

    def detect_hostile(self):
        img = take_screenshot(self.game_window)
        hostileLoc = detect_image(img, 'hostile_hb', 0.8)
        if hostileLoc:
            print("Hostile detected")
            self.hostilePicture = self.screenshot_hostile(hostileLoc)
            self.send_telegram_message("Hostile detected!")
            time.sleep(10)

    def detect_local_message(self):
        screenshot = take_screenshot(self.game_window)
        if detect_image(screenshot, 'local_gm', 0.8):
            print("Message local detected")
            self.send_telegram_message("Local message detected!")
            time.sleep(10)

    def screenshot_hostile(self, loc):
        left, top = loc
        left += self.game_window.left
        top += self.game_window.top
        height = 100
        width = 200

        center_x = left
        center_y = top

        bbox = (center_x - width // 2, center_y, center_x + width // 2, center_y + height // 2)
        screenshot = np.array(ImageGrab.grab(bbox))

        img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        # for plotting image
        # cv2.imshow('Captured Image', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # # img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        return img

    def send_telegram_message(self, message="Mesaj nou!"):
        bot = telebot.TeleBot(self.credentials['bot_token'])

        temp_file_path = "temp_screenshot.png"
        cv2.imwrite(temp_file_path, self.img)

        with open(temp_file_path, 'rb') as photo:
            # bot.send_message(self.credentials['chat_id'], "Ai primit un mesaj nou!")
            bot.send_photo(self.credentials['chat_id'], photo, caption={message})

        os.remove(temp_file_path)
