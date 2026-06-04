# esp32-ws2812b-ambilight

PC screen capture → ESP32-driven WS2812B LED strip. Real-time ambilight via serial/Bluetooth, with Android companion app for static color control.

## Features

- **Screen Ambilight** — captures edges of your primary monitor, averages colors per zone, and streams them to the LED strip in real time
- **Custom Static Color** — pick any solid color from the GUI, CLI, or Android app to fill the entire strip
- **Dual Transport** — communicates over USB Serial (wired) or Bluetooth Classic (wireless via ESP32)
- **GUI + CLI** — PySide6 desktop app for everyday use, CLI flags for scripting or headless setups

## Hardware

| Component | Details |
|-----------|---------|
| Microcontroller | ESP32 (or Arduino Uno/Nano with USB) |
| LED Strip | WS2812B (or any FastLED-compatible) |
| Connection | USB Serial or Bluetooth Classic (ESP32 only) |

## Project Structure

```
├── main.py              # Entry point — GUI (PySide6) and CLI
├── worker.py            # Screen capture + color analysis (QThread)
├── configs.py           # Zones, LEDs, serial, brightness settings
├── controller/
│   └── controller.ino   # Arduino/ESP32 firmware (FastLED)
├── android/             # Ambilight Controller Android app
└── old/                 # Archived prototypes
```

## Quick Start

### 1. Upload Firmware

Open `controller/controller.ino` in Arduino IDE, select your board (ESP32 or Arduino), and upload.

### 2. Install Python Dependencies

```bash
pip install PySide6 pyserial mss numpy
```

### 3. Configure

Edit `configs.py`:

- `SERIAL_PORT` — set to your Arduino/ESP32 COM port (e.g. `COM6`)
- `NUM_LEDS` — number of LEDs in your strip
- `HORIZONTAL_ZONES` / `VERTICAL_ZONES` — zone count along each edge

### 4. Run

**GUI mode:**
```bash
python main.py
```

**CLI ambilight:**
```bash
python main.py --ambilight
```

**CLI static color:**
```bash
python main.py --custom 255,100,50
```

## Protocol

Packets follow this format:

```
[0xFF] [Brightness] [Mode] [Data...]
```

| Byte | Field | Description |
|------|-------|-------------|
| 0 | `FRAME_START` | Always `0xFF` |
| 1 | Brightness | 0–255 |
| 2 | Mode | `0` = Ambilight, `1` = Static |
| 3+ | Data | See below |

**Mode 0 (Ambilight):** Packed RGB565 (2 bytes per LED)

**Mode 1 (Static):** Raw RGB888 (3 bytes: R, G, B)

## Android App

The companion [Ambilight Controller](https://github.com/abi-2002/AmbilightController) app connects to the ESP32 via Bluetooth and sends static color packets using the same protocol.
