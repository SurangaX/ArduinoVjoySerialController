<<<<<<< HEAD
COM to vJoy
===========

A Windows GUI utility to bridge serial (COM) input from a microcontroller (like an Arduino or ESP8266) to a virtual joystick using vJoy.  
Created by SurangaX 🕹️

----------------------
🚀 Features
----------------------

- Reads serial input (e.g., potentiometer and buttons)
- Sends data to vJoy Virtual Joystick in real-time
- Runs in the background with system tray support
- Start/Stop functionality for clean device control

----------------------
📦 How to Use
----------------------

1. Connect your device (e.g., Arduino/ESP) to your PC via USB.
2. Run `com_to_vjoy.exe` (or from source if you prefer).
3. Select the correct COM port (like COM3, COM4, etc.).
4. Click Start to begin communication.

You’ll see joystick movements and button presses reflected in vJoy.

----------------------
📂 Running from Source
----------------------

Make sure you have Python installed with dependencies:

    pip install pyserial pyvjoy pystray pillow

Then run:

    com_to_vjoy_gui.py

----------------------
🧠 Under the Hood
----------------------

- Uses `pyserial` to read data from the microcontroller.
- Looks for lines like:
      Smoothed Potentiometer Value: 512
      Button 1 pressed!
      Button 2 released!
- Maps those values to:
    - vJoy Axis X (scaled from 0–1023 to 0–32767)
    - vJoy Buttons (1–6)

A simple while loop handles real-time input while the app is running, and everything is cleanly stopped when the user clicks Stop or exits.

----------------------
⚠️ Known Issues
----------------------

1. Arduino/ESP might not respond sometimes  
   → This usually happens when the COM port gets stuck.  
   🔌 Try unplugging and plugging it back in.

2. App may not start correctly after being stopped once  
   → This was a bug in the initial version, caused by serial or thread conflicts.  
   ✅ It’s now mostly fixed — serial port and vJoy are re-initialized properly.  
   If you still face this, try clicking Quit and reopening the app.

----------------------
📥 Downloads
----------------------

You can download the compiled `.exe` from the Releases tab on GitHub.

----------------------
📃 License
----------------------

MIT License

----------------------

Created with ❤️ by SurangaX
=======
# com-to-vjoy
>>>>>>> dd62de6510f552729c9ee7dd37fbbd31b8d386f4
