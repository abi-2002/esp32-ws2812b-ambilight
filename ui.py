import sys
import time
import serial
import serial.tools.list_ports
import argparse

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QColorDialog
)
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtCore import Qt, QThread, QTimer

from ambilight import AmbilightWorker
from configs import *


# 🖥️ UI Class
class AmbilightUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ambilight Control")
        self.setFixedSize(APP_WIDTH, APP_HEIGHT)
        self.setStyleSheet("background-color: #121212;")

        self.ser = None
        self.connected = False
        self.worker = None

        self.load_font()
        self.setup_ui()

        # Try connect immediately
        self.try_connect()

        # Retry every 2 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.try_connect)
        self.timer.start(2000)

    # 🔤 Load Reddit Sans
    def load_font(self):
        font_id = QFontDatabase.addApplicationFont(FONT)

        if font_id != -1:
            family = QFontDatabase.applicationFontFamilies(font_id)[0]
            app_font = QFont(family)
            app_font.setPointSize(10)
            QApplication.setFont(app_font)
        else:
            print("Font failed to load")

    # 🎨 Setup UI
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(50)
        main_layout.setContentsMargins(0, 50, 0, 0)

        # Title
        title = QLabel("Ambilight")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 42px;
            font-weight: 600;
            color: white;
        """)

        # Status label
        self.status_label = QLabel("⚠ Connect Arduino")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #ff5555;
            font-size: 18px;
        """)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(40)

        self.ambilight_btn = QPushButton("Start Ambilight")
        self.custom_btn = QPushButton("Custom")

        self.ambilight_btn.setFixedSize(MODE_BUTTON_WIDTH, MODE_BUTTON_HEIGHT)
        self.custom_btn.setFixedSize(MODE_BUTTON_WIDTH, MODE_BUTTON_HEIGHT)

        self.ambilight_btn.setStyleSheet(self.button_style())
        self.custom_btn.setStyleSheet(self.button_style())

        # Connect signals
        self.ambilight_btn.clicked.connect(self.toggle_ambilight)
        self.custom_btn.clicked.connect(self.open_color_picker)

        # Add widgets
        button_layout.addWidget(self.ambilight_btn)
        button_layout.addWidget(self.custom_btn)

        main_layout.addWidget(title)
        main_layout.addWidget(self.status_label)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Initially disabled
        self.enable_controls(False)

    def button_style(self):
        return """
        QPushButton {
            font-size: 22px;
            border-radius: 24px;
            border: 2px solid #2e2e2e;
            background-color: #1e1e1e;
            color: white;
        }
        QPushButton:hover {
            background-color: #2c2c2c;
        }
        QPushButton:pressed {
            background-color: #444;
        }
        QPushButton:disabled {
            background-color: #555;
            color: #999;
        }
        """

    # 🔌 Try connecting Arduino
    def try_connect(self):
        if self.connected:
            return

        ports = serial.tools.list_ports.comports()

        for port in ports:
            try:
                print(f"Trying {port.device}...")

                self.ser = serial.Serial(port.device, BAUD_RATE, write_timeout=0)
                time.sleep(2)

                self.connected = True

                print(f"Connected to {port.device}")

                self.status_label.setText(f"Connected: {port.description}")
                self.status_label.setStyleSheet("color: #55ff55; font-size: 18px;")

                self.enable_controls(True)

                self.worker = AmbilightWorker(self.ser)

                return

            except:
                continue

        # Not connected
        self.connected = False
        self.status_label.setText("⚠ Connect Arduino")
        self.status_label.setStyleSheet("color: #ff5555; font-size: 18px;")
        self.enable_controls(False)

    # 🔘 Enable/disable UI
    def enable_controls(self, enabled):
        self.ambilight_btn.setEnabled(enabled)
        self.custom_btn.setEnabled(enabled)

    # 🎯 Start/Stop Ambilight
    def toggle_ambilight(self):
        if not self.connected or self.worker is None:
            return

        if self.worker.isRunning():
            self.worker.stop()
            self.ambilight_btn.setText("Start Ambilight")
        else:
            self.worker.start()
            self.ambilight_btn.setText("Stop Ambilight")

    # 🎨 Color picker
    def open_color_picker(self):
        if not self.connected or self.ser is None:
            return
        
        # Stop ambilight
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.ambilight_btn.setText("Start Ambilight")

        color = QColorDialog.getColor()

        if color.isValid():
            r = color.red()
            g = color.green()
            b = color.blue()

            print("Selected:", r, g, b)


            data = [FRAME_START] + [BRIGHTNESS] + [r, g, b] * NUM_LEDS

            try:
                self.ser.reset_input_buffer()
                self.ser.write(bytearray(data))
                self.ser.flush()  
            except:
                print("Disconnected")
                self.connected = False

    # 🛑 Cleanup
    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()

        if self.ser:
            self.ser.close()

        event.accept()


def run_cli(args):
    print("Running in CLI mode")

    # Find Arduino
    ser = None

    ports = serial.tools.list_ports.comports()

    for port in ports:
        try:
            print(f"Trying {port.device}...")
            ser = serial.Serial(port.device, BAUD_RATE, write_timeout=0)
            time.sleep(2)
            print(f"Connected to {port.device}")
            break
        except:
            continue

    if ser is None:
        print("❌ Arduino not found")
        return

    # -------- Ambilight Mode --------
    if args.ambilight:
        print("Starting Ambilight (CLI)")

        worker = AmbilightWorker(ser)
        worker.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
            worker.stop()
            ser.close()
            return

    # -------- Custom Color --------
    if args.custom:
        try:
            r, g, b = map(int, args.custom.split(","))

            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            print(f"Setting color {r},{g},{b}")

            data = [FRAME_START] + [BRIGHTNESS] + [r, g, b] * NUM_LEDS

            ser.reset_input_buffer()
            ser.reset_output_buffer()
            ser.write(bytearray(data))
            
            ser.flush()        
            time.sleep(0.1)   
            ser.close()  
            print("Done")

        except Exception as e:
            print("Invalid format. Use R,G,B")
            print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--ambilight", action="store_true")
    parser.add_argument("--custom", type=str)

    args = parser.parse_args()

    # 🔥 CLI mode
    if args.ambilight or args.custom:
        run_cli(args)
        sys.exit(0)

    # 🔥 GUI mode
    app = QApplication(sys.argv)

    window = AmbilightUI()
    window.show()

    sys.exit(app.exec())