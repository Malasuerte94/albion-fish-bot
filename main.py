import sys
import tkinter as tk
from tkinter import ttk
import pygetwindow as gw
from bot_inputs.bot_logic import set_fishing_region, load_settings, update_window_list, set_hostile_detector
from fishbot import FishBot
from bot_inputs.overlay import MapSelectorOverlay
from ttkthemes import ThemedStyle
from hostile_detector import HostileDetector

# Global variables to hold the selected window and bot states
selected_window = None
fish_bot_running = False
farm_bot_running = False
hostile_detector_running = False

# Load saved settings
settings = load_settings()

# Initialize Threads
fish_bot = None
hostile_detector_th = None


def start_fish_bot():
    global selected_window, fish_bot_running, fish_bot
    if selected_window and not fish_bot_running:
        window_dropdown.config(state="disabled")
        fish_bot_running = True
        fish_bot = FishBot(selected_window.title)
        fish_bot.start()
        if settings.get('hostile_detector', True):
            start_hostile_detector()
    else:
        print("Please select a window.")


def stop_fish_bot():
    global fish_bot_running, fish_bot
    if fish_bot_running:
        print("Stopping Fish Bot...")
        fish_bot_running = False
        fish_bot.stop()
        fish_bot.join(timeout=1)
        fish_bot = None
        stop_hostile_detector()
    else:
        print("Fish Bot is not running.")


def start_hostile_detector():
    global selected_window, hostile_detector_running, hostile_detector_th
    if not hostile_detector_running:
        hostile_detector_running = True
        hostile_detector_th = HostileDetector(selected_window.title)
        hostile_detector_th.start()
    else:
        print("Hostile Detector is already running.")


def stop_hostile_detector():
    global selected_window, hostile_detector_running, hostile_detector_th
    if hostile_detector_running:
        hostile_detector_running = False
        hostile_detector_th.stop()
        hostile_detector_th.join(timeout=1)
        hostile_detector_th = None
    else:
        print("Hostile Detector is not running.")


def select_window(event):
    global selected_window
    for window in gw.getAllWindows():
        if window.title == window_var.get():
            selected_window = window
            print(f"Selected window: {selected_window}")
            break


def open_fishing_region_selector():
    global selected_window
    if selected_window:
        overlay = tk.Toplevel()
        game_window_position = selected_window.topleft
        MapSelectorOverlay(overlay, selected_window, game_window_position, set_fishing_region)
    else:
        print("Please select a window first.")


class PrintRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


# Create the main window
root = tk.Tk()
root.title("Bot Controller")
root.resizable(False, False)  # Disable window resizing
root.configure(bg="grey")

# Dark mode theme colors
dark_bg = "#282828"
dark_fg = "#FFFFFF"

# Style configuration
style = ThemedStyle(root)
style.theme_use('black')

style.configure('TButton', padding=6)
style.configure('TLabel', padding=6)
style.configure('TCheckbutton', padding=6)
style.configure('TEntry', padding=6)
style.configure('TNotebook', padding=6)
style.configure('TNotebook.Tab', padding=6)

# Window selection
ttk.Label(root, text="Select Game Window:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
window_var = tk.StringVar()
window_dropdown = ttk.Combobox(root, textvariable=window_var)
window_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky='we')
window_dropdown.bind("<<ComboboxSelected>>", select_window)
window_dropdown['values'] = update_window_list()

# Create tab control
tab_control = ttk.Notebook(root)
fish_bot_tab = ttk.Frame(tab_control)
tab_control.add(fish_bot_tab, text='Fish Bot')
tab_control.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

# Fish Bot tab
ttk.Label(fish_bot_tab, text="Fish Bot Controls").grid(row=0, column=0, padx=10, pady=10, sticky='w')
ttk.Button(fish_bot_tab, text="Start Fish Bot", command=start_fish_bot).grid(row=1, column=0, padx=10, pady=10,
                                                                             sticky='w')
ttk.Button(fish_bot_tab, text="Stop Fish Bot", command=stop_fish_bot).grid(row=1, column=1, padx=10, pady=10,
                                                                           sticky='w')
# Map Selector
fishing_selector_button = ttk.Button(fish_bot_tab, text="Map Selector", command=open_fishing_region_selector)
fishing_selector_button.grid(row=4, column=0, padx=10, pady=10, sticky='w')

# Hostile Detector checkbox
hostile_detector_var = tk.BooleanVar(value=settings.get('hostile_detector', False))
gm_detector_checkbox = ttk.Checkbutton(fish_bot_tab, text="Hostile Detector", variable=hostile_detector_var,
                                       command=lambda: set_hostile_detector(hostile_detector_var.get()))
gm_detector_checkbox.grid(row=2, column=0, padx=10, pady=10, sticky='w')

# Log output text widget
log_output = tk.Text(root, height=10, wrap='word', state='normal')
log_output.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

# Redirect print statements to the log output text widget
sys.stdout = PrintRedirector(log_output)

# Run the main loop
root.mainloop()
