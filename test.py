import serial
import time

SERIAL_PORT = 'COM3'   # CHANGE THIS
BAUD_RATE = 115200

FRAME_START = 255
BRIGHTNESS = 20
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
time.sleep(2)


ser.reset_input_buffer()
ser.write(bytearray([FRAME_START] + [BRIGHTNESS] + [15,221,6] * 92))
