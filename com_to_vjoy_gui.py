import pyvjoy
import serial
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import os
import sys

# SurangaX

class VJoyApp:
    def __init__(self, master):
        self.master = master
        self.master.withdraw()

        self.vjoy_device = None
        self.ser = None
        self.running = False
        self.tray_thread = None
        self.icon = None

        self.setup_gui()
        self.create_tray_icon()

    def setup_gui(self):
        self.window = tk.Toplevel(self.master)
        self.window.title("COM to vJoy")
        self.window.geometry("300x250")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        ttk.Label(self.window, text="Serial Port (e.g., COM3):").pack(pady=5)

        self.com_entry = ttk.Entry(self.window)
        self.com_entry.insert(0, "COM3")
        self.com_entry.pack(pady=5)

        self.start_btn = ttk.Button(self.window, text="Start", command=self.start)
        self.start_btn.pack(pady=10)

        self.stop_btn = ttk.Button(self.window, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack()

        self.quit_btn = ttk.Button(self.window, text="Quit", command=self.force_quit)
        self.quit_btn.pack(pady=10)

        self.status_label = ttk.Label(self.window, text="Status: Idle")
        self.status_label.pack(pady=5)

        style = ttk.Style()
        style.configure("Credit.TLabel", font=("Segoe UI", 9, "bold"))
        self.credit_label = ttk.Label(self.window, text="Created By SurangaX", style="Credit.TLabel")
        self.credit_label.pack(pady=2)

    def start(self):
        if self.running:
            return

        try:
            port = self.com_entry.get()
            self.ser = serial.Serial(port, 115200, timeout=1)
            self.vjoy_device = pyvjoy.VJoyDevice(1)
            self.running = True
            self.status_label.config(text=f"Status: Reading {port}")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            threading.Thread(target=self.read_serial, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.stop()

    def stop(self):
        if not self.running:
            return

        self.running = False
        time.sleep(0.2)  # Allow time for thread to exit

        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.ser = None
        except Exception as e:
            print(f"Error closing serial: {e}")

        if self.vjoy_device:
            for btn in range(1, 7):
                self.vjoy_device.set_button(btn, 0)
            self.vjoy_device = None

        self.status_label.config(text="Status: Stopped")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def read_serial(self):
        try:
            while self.running and self.ser and self.ser.is_open:
                try:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.process_line(line)
                except Exception:
                    continue
        except Exception as e:
            if self.running:
                messagebox.showerror("Serial Error", str(e))
            self.stop()

    def process_line(self, line):
        if "Smoothed Potentiometer Value:" in line:
            try:
                value = int(line.split(":")[1].strip())
                scaled = int((value / 1023) * 32767)
                self.vjoy_device.set_axis(pyvjoy.HID_USAGE_X, scaled)
            except:
                pass

        for i in range(1, 7):
            if f"Button {i} pressed!" in line:
                self.vjoy_device.set_button(i, 1)
            elif f"Button {i} released!" in line:
                self.vjoy_device.set_button(i, 0)

    def create_tray_icon(self):
        icon_image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon_image)
        draw.ellipse((8, 8, 56, 56), fill="dodgerblue")

        self.icon = pystray.Icon("vjoy_icon", icon_image, "CSH vJoy", menu=self.create_tray_menu())
        self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.tray_thread.start()

    def create_tray_menu(self):
        return (
            item("Open", self.open_window),
            item("Start", lambda icon, item: self.start()),
            item("Stop", lambda icon, item: self.stop()),
            item("Exit", lambda icon, item: self.force_quit())
        )

    def open_window(self, icon=None, item=None):
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        if self.icon:
            self.icon.visible = False

    def on_close(self):
        self.window.withdraw()
        if self.icon:
            self.icon.visible = True

    def force_quit(self):
        try:
            self.stop()
            if self.icon:
                self.icon.visible = False
                self.icon.stop()
            self.window.destroy()
            self.master.destroy()
        except Exception as e:
            print("Error during quit:", e)
        finally:
            os._exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = VJoyApp(root)
    root.mainloop()
