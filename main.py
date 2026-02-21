from mss import mss
import numpy as np
import serial
import time

from configs import *

# ---------------- CONFIG ----------------
SERIAL_PORT = 'COM3'   # CHANGE THIS
BAUD_RATE = 115200
# ----------------------------------------

sct = mss()

WIDTH = sct.monitors[1].get('width', 1920)
HEIGHT = sct.monitors[1].get('height', 1080)

ZONE_WIDTH = WIDTH // HORIZONTAL_ZONES
ZONE_HEIGHT = HEIGHT // VERTICAL_ZONES

# -------- SERIAL --------
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, write_timeout=0)
time.sleep(2)


def get_colors():
    return np.array(sct.grab(sct.monitors[1]))


def get_average_colour(zone):
    b, g, r, _ = np.mean(zone, axis=(0,1))
    return int(r), int(g), int(b)


def top_slice(image):
    zone_average_colours = []
    for i in range(HORIZONTAL_ZONES):
        zone = image[0:SLICED_PIXELS, i * ZONE_WIDTH:(i + 1) * ZONE_WIDTH]
        zone_average_colours.extend(get_average_colour(zone))
    return zone_average_colours


def bottom_slice(image):
    zone_average_colours = []
    for i in range(HORIZONTAL_ZONES - 1, -1, -1):
        zone = image[HEIGHT - SLICED_PIXELS:HEIGHT,
                     i * ZONE_WIDTH:(i + 1) * ZONE_WIDTH]
        zone_average_colours.extend(get_average_colour(zone))

    return zone_average_colours


def left_slice(image):
    zone_average_colours = []
    for i in range(VERTICAL_ZONES - 1, -1, -1):
        zone = image[
            (i * ZONE_HEIGHT) + SLICED_PIXELS:
            ((i + 1) * ZONE_HEIGHT) + SLICED_PIXELS,
            0:SLICED_PIXELS
        ]
        zone_average_colours.extend(get_average_colour(zone))

    return zone_average_colours


def right_slice(image):
    zone_average_colours = []
    for i in range(VERTICAL_ZONES):
        zone = image[
            (i * ZONE_HEIGHT) + SLICED_PIXELS:
            ((i + 1) * ZONE_HEIGHT) + SLICED_PIXELS,
            WIDTH - SLICED_PIXELS:WIDTH
        ]
        zone_average_colours.extend(get_average_colour(zone))

    return zone_average_colours




def main():

    while True:
        image = get_colors()

        bottom_rgb = bottom_slice(image)
        left_rgb = left_slice(image)
        top_rgb = top_slice(image)
        right_rgb = right_slice(image)

        led_rgb_data = bottom_rgb + left_rgb + top_rgb + right_rgb

        # DEBUG: ensure correct size
        if len(led_rgb_data) != NUM_LEDS * 3:
            print("ERROR: wrong data size:", len(led_rgb_data))
            continue

        # Add frame start byte
        data = bytearray([FRAME_START] + [BRIGHTNESS] + led_rgb_data)

        ser.reset_input_buffer()

        try:
            ser.write(data)
        except:
            print("Serial write failed")

        time.sleep(1/FPS)




if __name__ == "__main__":
    main()


