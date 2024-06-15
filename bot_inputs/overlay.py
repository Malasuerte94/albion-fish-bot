import os
import tkinter as tk
from PIL import Image, ImageTk
from bot_inputs.bot_logic import set_fishing_region
import pygetwindow as gw

script_dir = os.path.dirname(os.path.abspath(__file__))
map_image_path = os.path.abspath(os.path.join(script_dir, '..', 'images', 'map.png'))

class MapSelectorOverlay:
    def __init__(self, root, selected_window, game_window_position, set_fishing_region):
        self.root = root
        self.selected_window = selected_window
        self.game_window_position = game_window_position
        self.set_fishing_region = set_fishing_region

        # Load the map.png image
        self.map_image = Image.open(map_image_path).convert("RGBA")  # Ensure transparency
        self.map_photo = ImageTk.PhotoImage(self.map_image)

        # Create a label to display the map image
        self.map_label = tk.Label(self.root, image=self.map_photo, bg='white')
        self.map_label.pack()

        # Add the "Set" button
        self.set_button = tk.Button(self.root, text="Set", command=self.save_settings)
        self.set_button.pack()

        # Set opacity to 50%
        self.root.attributes('-alpha', 0.5)

        # Bind events
        self.map_label.bind("<Button-1>", self.start_move)
        self.map_label.bind("<B1-Motion>", self.do_move)

        # Initialize position and dimensions
        self.start_x = 0
        self.start_y = 0
        self.width = self.map_image.width
        self.height = self.map_image.height

    def start_move(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.start_x
        y = self.root.winfo_pointery() - self.start_y
        self.root.geometry(f"+{x}+{y}")

    def save_settings(self):
        # Save the position and dimensions of the map overlay
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        region = (
            root_x - self.selected_window.left,
            root_y - self.selected_window.top,
            self.width,
            self.height
        )
        self.set_fishing_region(region, self.selected_window)

        # Hide the overlay
        self.root.destroy()


# Test
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    selected_window = gw.getActiveWindow()  # Assuming the game window is active
    overlay = tk.Toplevel(root)
    overlay.overrideredirect(True)  # Remove window decorations
    overlay.attributes("-topmost", True)  # Ensure it stays on top
    app = MapSelectorOverlay(overlay, selected_window, None, set_fishing_region)
    overlay.mainloop()
