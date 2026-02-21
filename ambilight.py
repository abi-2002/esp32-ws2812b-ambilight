from PySide6.QtCore import Qt, QThread, QTimer
import time
from mss import mss
import numpy as np

from configs import *


# 🧵 Ambilight Worker Thread
class AmbilightWorker(QThread):
    def __init__(self, ser):
        super().__init__()
        self.ser = ser
        self.running = False
      

    def run(self):
        self.running = True
        self.sct = mss()

        self.width = self.sct.monitors[1].get('width', 1920)
        self.height = self.sct.monitors[1].get('height', 1080)

        self.zone_width = self.width // HORIZONTAL_ZONES
        self.zone_height = self.height // VERTICAL_ZONES

        while self.running:
            try:
                self.image = self.get_colors()
                bottom_rgb = self.bottom_slice()
                left_rgb = self.left_slice()
                top_rgb = self.top_slice()
                right_rgb = self.right_slice()

                led_rgb_data = bottom_rgb + left_rgb + top_rgb + right_rgb

                # DEBUG: ensure correct size
                if len(led_rgb_data) != NUM_LEDS * 3:
                    print("ERROR: wrong data size:", len(led_rgb_data))
                    continue

                self.ser.reset_input_buffer()
                self.ser.write(bytearray([FRAME_START] + [BRIGHTNESS] + led_rgb_data))
                time.sleep(1 / FPS)

            except Exception as e:
                print("Serial error:", e)
                self.running = False

    def stop(self):
        self.running = False
        self.wait()



    def get_colors(self):
        return np.array(self.sct.grab(self.sct.monitors[1]))


    def get_average_colour(self, zone):
        b, g, r, _ = np.mean(zone, axis=(0,1))
        return int(r), int(g), int(b)


    def top_slice(self):
        zone_average_colours = []
        for i in range(HORIZONTAL_ZONES):
            zone = self.image[0:SLICED_PIXELS, i * self.zone_width:(i + 1) * self.zone_width]
            zone_average_colours.extend(self.get_average_colour(zone))
        return zone_average_colours


    def bottom_slice(self):
        zone_average_colours = []
        for i in range(HORIZONTAL_ZONES - 1, -1, -1):
            zone = self.image[self.height - SLICED_PIXELS:self.height,
                        i * self.zone_width:(i + 1) * self.zone_width]
            zone_average_colours.extend(self.get_average_colour(zone))

        return zone_average_colours


    def left_slice(self):
        zone_average_colours = []
        for i in range(VERTICAL_ZONES - 1, -1, -1):
            zone = self.image[
                (i * self.zone_height) + SLICED_PIXELS:
                ((i + 1) * self.zone_height) + SLICED_PIXELS,
                0:SLICED_PIXELS
            ]
            zone_average_colours.extend(self.get_average_colour(zone))

        return zone_average_colours


    def right_slice(self):
        zone_average_colours = []
        for i in range(VERTICAL_ZONES):
            zone = self.image[
                (i * self.zone_height) + SLICED_PIXELS:
                ((i + 1) * self.zone_height) + SLICED_PIXELS,
                self.width - SLICED_PIXELS:self.width
            ]
            zone_average_colours.extend(self.get_average_colour(zone))

        return zone_average_colours

