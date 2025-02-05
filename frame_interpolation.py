import requests
import numpy as np
import cv2
from datetime import datetime, timedelta
import torch
import torch.nn as nn
import torch.nn.functional as F
from owslib.wms import WebMapService
from PIL import Image
import io


class FrameInterpolator(nn.Module):
    def __init__(self):
        super(FrameInterpolator, self).__init__()
        # Encoder
        self.conv1 = nn.Conv2d(6, 64, kernel_size=7, padding=3)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=5, padding=2)
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)

        # Decoder
        self.deconv1 = nn.ConvTranspose2d(256, 128, kernel_size=3, padding=1)
        self.deconv2 = nn.ConvTranspose2d(128, 64, kernel_size=5, padding=2)
        self.deconv3 = nn.ConvTranspose2d(64, 3, kernel_size=7, padding=3)

    def forward(self, frame1, frame2):
        x = torch.cat([frame1, frame2], dim=1)
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = F.relu(self.deconv1(x))
        x = F.relu(self.deconv2(x))
        x = torch.sigmoid(self.deconv3(x))
        return x


class WMSVideoGenerator:
    def __init__(self, wms_url, layer_name, bbox, width, height, progress_callback=None):
        self.wms = WebMapService(wms_url)
        self.layer_name = layer_name
        self.bbox = bbox
        self.width = width
        self.height = height
        self.progress_callback = progress_callback
        self.interpolator = FrameInterpolator()
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.interpolator.to(self.device)

    def update_progress(self, progress, status):
        if self.progress_callback:
            self.progress_callback(progress, status)

    def get_wms_frame(self, timestamp):
        img = self.wms.getmap(
            layers=[self.layer_name],
            srs='EPSG:4326',
            bbox=self.bbox,
            size=(self.width, self.height),
            format='image/png',
            time=timestamp.isoformat()
        )
        img_array = np.array(Image.open(io.BytesIO(img.read())))
        return img_array

    def interpolate_frames(self, frame1, frame2, num_intermediate):
        f1 = torch.from_numpy(frame1).float().permute(
            2, 0, 1).unsqueeze(0).to(self.device) / 255.0
        f2 = torch.from_numpy(frame2).float().permute(
            2, 0, 1).unsqueeze(0).to(self.device) / 255.0

        intermediate_frames = []
        for i in range(num_intermediate):
            t = (i + 1) / (num_intermediate + 1)
            with torch.no_grad():
                frame = self.interpolator(f1, f2)
            frame = (frame.cpu().squeeze(0).permute(
                1, 2, 0).numpy() * 255).astype(np.uint8)
            intermediate_frames.append(frame)
        return intermediate_frames

    def generate_video(self, start_time, end_time, output_path='output.mp4', interval_minutes=30, fps=30):
        self.update_progress(0, "Starting video generation...")

        current_time = start_time
        timestamps = []
        while current_time <= end_time:
            timestamps.append(current_time)
            current_time += timedelta(minutes=interval_minutes)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps,
                              (self.width, self.height))

        total_frames = len(timestamps) - 1
        for i in range(total_frames):
            progress = (i / total_frames) * 100
            self.update_progress(progress, f"Processing frame {
                                 i+1}/{total_frames}")

            frame1 = self.get_wms_frame(timestamps[i])
            frame2 = self.get_wms_frame(timestamps[i + 1])

            num_intermediate = int(interval_minutes * 60 * fps / 60) - 1
            intermediate_frames = self.interpolate_frames(
                frame1, frame2, num_intermediate)

            out.write(cv2.cvtColor(frame1, cv2.COLOR_RGB2BGR))
            for frame in intermediate_frames:
                out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        out.write(cv2.cvtColor(frame2, cv2.COLOR_RGB2BGR))
        out.release()

        self.update_progress(100, "Video generation complete!")
        return output_path


def test_generator():
    wms_url = "http://your.wms.server/wms"
    layer_name = "satellite_imagery"
    bbox = (-180, -90, 180, 90)
    width = 1920
    height = 1080

    def progress_callback(progress, status):
        print(f"Progress: {progress}%, Status: {status}")

    generator = WMSVideoGenerator(
        wms_url, layer_name, bbox, width, height, progress_callback)
    start_time = datetime(2024, 2, 1, 0, 0)
    end_time = datetime(2024, 2, 1, 2, 0)
    generator.generate_video(start_time, end_time)


if __name__ == "__main__":
    test_generator()
