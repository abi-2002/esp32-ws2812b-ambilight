import serial
import time

SERIAL_PORT = 'COM3'   # CHANGE THIS
BAUD_RATE = 115200

FRAME_START = 255
BRIGHTNESS = 20
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(2)


ser.reset_input_buffer()
ser.write(bytearray([FRAME_START] + [BRIGHTNESS] + [1] + [15,221,6]))


def pack(r, g, b):
    r = r >> 3
    g = g >> 3
    b = b >> 3
    shifted = r << 10 | g << 5 | b
    return shifted.to_bytes(2, 'big')


def unpack(packed_bytes):
    packed_int = int.from_bytes(packed_bytes, 'big')

    b = (packed_int & 31) << 3
    g = ((packed_int >> 5) & 31) << 3
    r = ((packed_int >> 10) & 31) << 3

    return r, g, b



def pipeline():

    rgb_values_1 = [
        (123, 45, 200),
        (12, 234, 67),
        (255, 100, 50),
        (0, 128, 255),
        (76, 89, 34),
        (210, 10, 140),
        (33, 222, 111),
        (199, 199, 199)
    ]
    rgb_values_2 = [
        (5, 250, 180),
        (87, 60, 240),
        (145, 90, 10),
        (250, 180, 30),
        (60, 10, 220),
        (180, 70, 160),
        (30, 200, 90)
    ]

    led_array = []

    for r, g, b in rgb_values_1:
        print(f"{r}, {g}, {b}")
        packed = pack(r, g, b)

        led_array.extend(packed)
    
    for r, g, b in rgb_values_2:
        print(f"{r}, {g}, {b}")
        packed = pack(r, g, b)
        led_array.extend(packed)

    return led_array