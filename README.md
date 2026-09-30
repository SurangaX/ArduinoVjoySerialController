# Arduino Vjoy Serial Controller (COM to vJoy) 🕹️

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Arduino](https://img.shields.io/badge/Firmware-Arduino%20%2F%20ESP8266-teal.svg)](https://www.arduino.cc/)
[![vJoy](https://img.shields.io/badge/vJoy-Virtual%20Joystick-orange.svg)](https://github.com/njz3/vJoy)
[![License: MIT-NC](https://img.shields.io/badge/License-MIT--NC%20(Non--Commercial)-red.svg)](LICENSE)

A Windows GUI utility and microcontroller firmware suite that bridges serial (COM) input from hardware microcontrollers (Arduino, ESP8266, ESP32) into virtual joystick inputs using **vJoy**.

Designed for DIY sim-racing steering wheels, custom flight sticks, button boxes, and game controllers.

---

## 🚀 Features

- **Modern Dark UI**: Clean, responsive interface featuring real-time steering wheel angle animation and 6 live button LED indicators.
- **Multiple Sensor Modes**:
  - **Potentiometer**: Analog input (0–1023) with Exponential Moving Average (EMA) smoothing mapped to vJoy Axis X.
  - **AS5600 Magnetic Encoder**: 12-bit contactless rotary sensor with multi-turn continuous angle tracking.
  - **Combined Mode**: Dual-axis support (Potentiometer $\rightarrow$ Axis X, AS5600 Magnetic Sensor $\rightarrow$ Axis Y).
- **Steering Wheel Calibration & Tuning**:
  - Center wheel calibration at any angle.
  - Axis Inversion toggle.
  - Adjustable Deadzone slider ($0\% - 20\%$).
  - Adjustable Smoothing Factor ($0.05 - 0.90$).
  - Rotation Range / DOR (Degrees of Rotation): $180^\circ$, $270^\circ$, $360^\circ$, $540^\circ$, $900^\circ$, $1080^\circ$.
- **System Tray & Background Running**:
  - Minimizes to the Windows system tray with notifications.
  - Single-instance protection prevents duplicate instances.
  - Global emergency disconnect hotkey (`Ctrl + Shift + S`).
- **Included Firmware Suite**:
  - Ready-to-flash sketches for ESP8266 and Arduino boards.

---

## 📁 Repository Structure

```
ArduinoVjoySerialController/
├── com_to_vjoy_gui.py      # Main Python GUI application
├── com_to_vjoy.exe         # Pre-compiled standalone Windows executable
├── wheel.png               # Wheel graphic asset for UI rotation
├── logo.ico                # Application & system tray icon
├── com_to_vjoy_gui.spec    # PyInstaller build specification
├── Run COM_to_vJoy.vbs     # Silent background launcher
├── firmware/
│   ├── V30/                # AS5600 multi-turn + Potentiometer + 6 debounced buttons
│   │   └── V30.ino
│   ├── steeringwheel20/    # Potentiometer + 6 debounced buttons
│   │   └── steeringwheel20.ino
│   ├── steeringwheel_basic/# Minimal potentiometer-only sketch
│   │   └── steeringwheel_basic.ino
│   └── AS5600_Debug/       # Diagnostic script for AS5600 I2C connection & magnet strength
│       └── AS5600_Debug.ino
├── LICENSE                 # MIT Non-Commercial License
└── README.md
```

---

## ⚡ Prerequisites

1. **vJoy Device Driver**:
   - Download and install [vJoy](https://github.com/njz3/vJoy).
   - Open **Configure vJoy** from the Windows Start menu.
   - Ensure **Device #1** is enabled with:
     - Axes: **X** (and optionally **Y**)
     - Number of Buttons: at least **6**
2. **Hardware**:
   - Microcontroller (e.g. NodeMCU / ESP8266, Arduino Nano, Uno, Pro Micro).
   - Sensor: 10k Potentiometer and/or AS5600 I2C magnetic rotary encoder.
   - Up to 6 push buttons / microswitches.

---

## 🔌 Hardware Wiring (ESP8266 Example)

| Component | Pin on ESP8266 | Description |
| :--- | :--- | :--- |
| **AS5600 SDA** | `D2` (GPIO4) | I2C Data line |
| **AS5600 SCL** | `D1` (GPIO5) | I2C Clock line |
| **Potentiometer Wiper**| `A0` (ADC0) | 0–3.3V analog input |
| **Button 1** | `D4` (GPIO2) | Input pull-up (Do not hold during boot) |
| **Button 2** | `RX` (GPIO3) | Input pull-up |
| **Button 3** | `D5` (GPIO14) | Input pull-up |
| **Button 4** | `D7` (GPIO13) | Input pull-up |
| **Button 5** | `D6` (GPIO12) | Input pull-up |
| **Button 6** | `D0` (GPIO16) | Input pull-up |

*All buttons connect between their respective GPIO pin and `GND` (using internal pull-up resistors).*

---

## 📦 How to Use

### Option 1: Run Pre-compiled Binary
1. Connect your microcontroller via USB.
2. Launch `com_to_vjoy.exe`.
3. Select your microcontroller's **COM Port** (e.g. `COM3`, `COM4`).
4. Select Baud Rate (`115200` by default).
5. Choose your Sensor Mode: **Potentiometer**, **AS5600 Magnetic**, or **Combined**.
6. Click **Connect**.
7. Center your physical wheel and click **Center Wheel** if required.

### Option 2: Run from Source
1. Install Python 3.8 or higher.
2. Install required dependencies:
   ```bash
   pip install pyvjoy pyserial pillow pystray keyboard
   ```
3. Run the GUI application:
   ```bash
   python com_to_vjoy_gui.py
   ```
   *(Or double-click `Run COM_to_vJoy.vbs` to launch without an open console window).*

---

## 🛠️ Building the Standalone Executable

To rebuild `com_to_vjoy.exe` using PyInstaller:

```bash
pip install pyinstaller
pyinstaller com_to_vjoy_gui.spec
```

The compiled binary will be generated in the `dist/` directory.

---

## 📄 Serial Protocol

The GUI parses incoming serial strings at 115200 baud:

- **Potentiometer**: `Smoothed Potentiometer Value: <0-1023>`
- **AS5600 Multi-turn**: `Continuous Angle: <-32768 to 32767>`
- **AS5600 Degrees**: `Degrees: <0.0 - 360.0>`
- **Button Press**: `Button <1-6> pressed!`
- **Button Release**: `Button <1-6> released!`

---

## 📃 License

Distributed under the **MIT Non-Commercial License (MIT-NC)**. Free for personal, educational, and hobbyist use. Commercial use, redistribution for profit, or inclusion in commercial products is prohibited without permission. See [LICENSE](LICENSE) for details.

---

Created with ❤️ by [SurangaX](https://github.com/SurangaX)
