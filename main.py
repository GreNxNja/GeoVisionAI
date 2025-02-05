import tkinter as tk
from tkinter import messagebox
from gui import WMSGUI
from frame_interpolation import WMSVideoGenerator


class WMSApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.gui = WMSGUI(self.root)
        self.setup_callbacks()

    def setup_callbacks(self):
        self.gui.generate_btn.config(command=self.start_generation)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_generation(self):
        config = self.gui.get_config()
        generator = WMSVideoGenerator(
            config['wms_url'],
            config['layer_name'],
            config['bbox'],
            config['width'],
            config['height'],
            self.gui.update_progress
        )
        generator.generate_video(config['start_time'], config['end_time'])

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.quit()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = WMSApplication()
    app.run()
