import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
from PIL import Image, ImageTk
import cv2
from tkcalendar import DateEntry


class WMSGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WMS Frame Interpolation")

        # WMS Configuration Frame
        self.config_frame = ttk.LabelFrame(
            root, text="WMS Configuration", padding=10)
        self.config_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # WMS URL
        ttk.Label(self.config_frame, text="WMS URL:").grid(
            row=0, column=0, sticky="w")
        self.url_entry = ttk.Entry(self.config_frame, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=2)
        self.url_entry.insert(0, "http://your.wms.server/wms")

        # Layer Name
        ttk.Label(self.config_frame, text="Layer Name:").grid(
            row=1, column=0, sticky="w")
        self.layer_entry = ttk.Entry(self.config_frame, width=30)
        self.layer_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=2)
        self.layer_entry.insert(0, "satellite_imagery")

        # Bounding Box
        ttk.Label(self.config_frame, text="Bounding Box:").grid(
            row=2, column=0, sticky="w")
        self.bbox_frame = ttk.Frame(self.config_frame)
        self.bbox_frame.grid(row=2, column=1, columnspan=2, pady=2)

        self.bbox_entries = []
        labels = ["Min X:", "Min Y:", "Max X:", "Max Y:"]
        default_values = [-180, -90, 180, 90]

        for i, (label, value) in enumerate(zip(labels, default_values)):
            ttk.Label(self.bbox_frame, text=label).grid(row=0, column=i * 2)
            entry = ttk.Entry(self.bbox_frame, width=8)
            entry.grid(row=0, column=i * 2 + 1, padx=2)
            entry.insert(0, str(value))
            self.bbox_entries.append(entry)

        # Resolution Frame
        self.res_frame = ttk.LabelFrame(
            root, text="Output Resolution", padding=10)
        self.res_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        ttk.Label(self.res_frame, text="Width:").grid(row=0, column=0)
        self.width_entry = ttk.Entry(self.res_frame, width=8)
        self.width_entry.grid(row=0, column=1, padx=5)
        self.width_entry.insert(0, "1920")

        ttk.Label(self.res_frame, text="Height:").grid(row=0, column=2)
        self.height_entry = ttk.Entry(self.res_frame, width=8)
        self.height_entry.grid(row=0, column=3, padx=5)
        self.height_entry.insert(0, "1080")

        # Time Range Frame
        self.time_frame = ttk.LabelFrame(root, text="Time Range", padding=10)
        self.time_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # Start Time
        ttk.Label(self.time_frame, text="Start Time:").grid(row=0, column=0)
        self.start_date_entry = DateEntry(self.time_frame, width=12, background='darkblue',
                                          foreground='white', borderwidth=2)
        self.start_date_entry.grid(row=0, column=1, padx=5)

        self.start_hour = ttk.Spinbox(self.time_frame, from_=0, to=23, width=5)
        self.start_hour.grid(row=0, column=2, padx=5)
        self.start_hour.set(0)

        self.start_minute = ttk.Spinbox(
            self.time_frame, from_=0, to=59, width=5)
        self.start_minute.grid(row=0, column=3, padx=5)
        self.start_minute.set(0)

        # End Time
        ttk.Label(self.time_frame, text="End Time:").grid(row=1, column=0)
        self.end_date_entry = DateEntry(self.time_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2)
        self.end_date_entry.grid(row=1, column=1, padx=5)

        self.end_hour = ttk.Spinbox(self.time_frame, from_=0, to=23, width=5)
        self.end_hour.grid(row=1, column=2, padx=5)
        self.end_hour.set(23)

        self.end_minute = ttk.Spinbox(self.time_frame, from_=0, to=59, width=5)
        self.end_minute.grid(row=1, column=3, padx=5)
        self.end_minute.set(59)

        # Progress Frame
        self.progress_frame = ttk.LabelFrame(root, text="Progress", padding=10)
        self.progress_frame.grid(
            row=3, column=0, padx=10, pady=5, sticky="nsew")

        self.progress_bar = ttk.Progressbar(
            self.progress_frame, length=400, mode='determinate')
        self.progress_bar.grid(row=0, column=0, pady=5)

        self.status_label = ttk.Label(self.progress_frame, text="Ready")
        self.status_label.grid(row=1, column=0, pady=5)

        # Generate Button
        self.generate_btn = ttk.Button(root, text="Generate Video",
                                       command=self.start_generation)
        self.generate_btn.grid(row=4, column=0, pady=10)

        # Preview Frame
        self.preview_frame = ttk.LabelFrame(root, text="Preview", padding=10)
        self.preview_frame.grid(
            row=0, column=1, rowspan=5, padx=10, pady=5, sticky="nsew")

        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.grid(row=0, column=0)

    def get_datetime(self, date_entry, hour_spinbox, minute_spinbox):
        """Extracts datetime from UI elements"""
        date_str = date_entry.get()
        hour = int(hour_spinbox.get())
        minute = int(minute_spinbox.get())
        return datetime.strptime(f"{date_str} {hour}:{minute}", "%m/%d/%y %H:%M")

    def get_config(self):
        """Get all configuration values from GUI"""
        return {
            'wms_url': self.url_entry.get(),
            'layer_name': self.layer_entry.get(),
            'bbox': tuple(float(entry.get()) for entry in self.bbox_entries),
            'width': int(self.width_entry.get()),
            'height': int(self.height_entry.get()),
            'start_time': self.get_datetime(self.start_date_entry, self.start_hour, self.start_minute),
            'end_time': self.get_datetime(self.end_date_entry, self.end_hour, self.end_minute)
        }

    def start_generation(self):
        """Start video generation in a separate thread"""
        config = self.get_config()
        self.generate_btn['state'] = 'disabled'

        def generate():
            try:
                self.update_progress(0, "Initializing...")
                self.update_progress(100, "Complete!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.generate_btn['state'] = 'normal'

        thread = threading.Thread(target=generate)
        thread.start()

    def update_progress(self, value, status):
        self.progress_bar['value'] = value
        self.status_label['text'] = status
        self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = WMSGUI(root)
    root.mainloop()
