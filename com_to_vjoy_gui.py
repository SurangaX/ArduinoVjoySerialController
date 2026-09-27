# -*- coding: utf-8 -*-
import pyvjoy
import serial
import serial.tools.list_ports
import threading
import time
import math
import tkinter as tk
from tkinter import ttk, messagebox
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import os
import sys
import tempfile
import atexit
try:
    import msvcrt
except ImportError:
    import fcntl

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

# SurangaX — Modern Fantech-Style UI v3

# ─── Colour Palette ───────────────────────────────────────────────────────────
C_BG          = "#0d0d0d"   # window background
C_PANEL       = "#141414"   # title bar / footer bar
C_CARD        = "#1a1a1a"   # settings card interior
C_PANEL2      = "#222222"   # entry / combobox field background
C_BORDER      = "#2e2e2e"   # subtle border colour
C_FG          = "#e8e8e8"   # primary text
C_LABEL       = "#888888"   # muted label text
C_ACCENT      = "#00d4ff"   # cyan accent
C_ACCENT2     = "#0099bb"   # darker cyan
C_SUCCESS     = "#00ff88"   # bright green (connect button)
C_SUCCESS_MUT = "#007744"   # muted green (centered status)
C_ERROR       = "#ff3b3b"   # bright red
C_ERROR_DIM   = "#1e0808"   # very dark red (disconnect button bg)
C_WARNING     = "#ffaa00"   # amber warning
C_BTN_BG      = "#1e1e1e"   # generic button background
C_BTN_HOV     = "#2a2a2a"   # generic button hover
C_WHEEL_RIM   = "#444444"   # lightened wheel rim (was #2a2a2a)
C_WHEEL_HUB   = "#333333"   # wheel hub
C_WHEEL_ACC   = "#00d4ff"   # wheel accent / spoke highlight
C_WHEEL_GRP   = "#383838"   # grip segment fill

FONT      = "Segoe UI"
FONT_MONO = "Consolas"


# ─── System requirements ──────────────────────────────────────────────────────

def check_system_requirements():
    missing = []
    try:
        import pyvjoy
        pyvjoy.VJoyDevice(1)
    except ImportError:
        missing.append("pyvjoy library is missing")
    except Exception as e:
        if "vjoy" in str(e).lower():
            missing.append("vJoy Driver is not installed or not working properly")
        else:
            missing.append(f"vJoy system error: {str(e)}")
    try:
        import serial.tools.list_ports
    except ImportError:
        missing.append("Serial port support is missing")
    return missing


def show_requirements_dialog(missing):
    msg = "❌ Missing System Requirements\n\n"
    msg += "The following components are required but not found:\n\n"
    for req in missing:
        if "vJoy" in req:
            msg += "• vJoy Virtual Joystick Driver\n"
            msg += "  → Download: https://vjoystick.sourceforge.net/\n\n"
        else:
            msg += f"• {req}\n\n"
    msg += "1. Download vJoy\n2. Run as Administrator\n3. Restart\n4. Re-launch app"
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askquestion("System Requirements", msg + "\n\nOpen download page?", icon='warning')
    if result == 'yes':
        try:
            import webbrowser
            webbrowser.open('https://vjoystick.sourceforge.net/')
        except Exception:
            pass
    root.destroy()


# ─── Steering Wheel Canvas ────────────────────────────────────────────────────

class WheelCanvas(tk.Canvas):
    """Fast canvas-drawn steering wheel — rotates with zero lag."""
    WHEEL_R = 92
    RIM_W   = 14
    HUB_R   = 14
    SPOKE_W = 7

    def __init__(self, parent, size=220, **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg=C_BG, highlightthickness=0, **kwargs)
        self.size  = size
        self.cx    = size // 2
        self.cy    = size // 2
        self.angle = 0.0
        self._draw()

    def set_angle(self, degrees: float):
        if abs(degrees - self.angle) > 0.4:
            self.angle = degrees
            self._draw()

    def _polar(self, cx, cy, r, deg):
        rad = math.radians(deg - 90)
        return cx + r * math.cos(rad), cy + r * math.sin(rad)

    def _draw(self):
        self.delete("all")
        cx, cy = self.cx, self.cy
        a  = self.angle
        r  = self.WHEEL_R
        rw = self.RIM_W

        # Shadow
        sr = r + rw // 2 + 6
        self.create_oval(cx-sr, cy-sr, cx+sr, cy+sr,
                         outline="#000000", width=8, fill="")

        # Outer rim — mid-gray so it's visible on dark bg
        self.create_oval(cx-r, cy-r, cx+r, cy+r,
                         outline=C_WHEEL_RIM, width=rw, fill="")

        # Grip segments (3 arcs, rotate with wheel)
        for ga in [a+90, a+210, a+330]:
            self.create_arc(cx-r, cy-r, cx+r, cy+r,
                            start=-(ga+30), extent=60,
                            outline=C_WHEEL_GRP, width=rw-2, style=tk.ARC)

        # Spokes + thin cyan highlight
        se = r - rw//2 + 1
        ss = self.HUB_R + 2
        for so in [a, a+120, a+240]:
            x1, y1 = self._polar(cx, cy, ss, so)
            x2, y2 = self._polar(cx, cy, se, so)
            self.create_line(x1, y1, x2, y2,
                             fill=C_WHEEL_RIM, width=self.SPOKE_W, capstyle=tk.ROUND)
            xa1, ya1 = self._polar(cx, cy, ss+4, so)
            xa2, ya2 = self._polar(cx, cy, se-4, so)
            self.create_line(xa1, ya1, xa2, ya2,
                             fill=C_WHEEL_ACC, width=1, capstyle=tk.ROUND)

        # Hub
        hr = self.HUB_R
        self.create_oval(cx-hr, cy-hr, cx+hr, cy+hr,
                         outline=C_WHEEL_ACC, width=2, fill=C_WHEEL_HUB)

        # Fixed reference tick — always at 12 o'clock, never rotates
        ti = r - rw//2 - 2
        to = r + rw//2 + 4
        self.create_line(cx, cy-ti, cx, cy-to,
                         fill=C_ACCENT, width=3, capstyle=tk.ROUND)

        # Outer accent ring
        ar = r + rw//2 + 2
        self.create_oval(cx-ar, cy-ar, cx+ar, cy+ar,
                         outline=C_ACCENT, width=1, fill="")


# ─── Main Application ─────────────────────────────────────────────────────────

class VJoyApp:
    def __init__(self, master, start_minimized=False):
        self.master = master
        self.master.withdraw()

        self.vjoy_device          = None
        self.ser                  = None
        self.running              = False
        self.tray_thread          = None
        self.icon                 = None
        self.start_minimized      = start_minimized
        self.selected_vjoy_device = 1

        # Steering state
        self.current_angle  = 0.0
        self.center_offset  = 0
        self.request_center = False

        # Button LED states
        self.btn_leds = {}   # {n: (canvas, oval_id, text_id)}

        # Hotkey
        self.center_hotkey     = "ctrl+shift+c"
        self.hotkey_registered = False

        self.set_master_icon()
        self.setup_gui()
        self.create_tray_icon()

        if not self.start_minimized:
            self.window.deiconify()
        else:
            self.window.withdraw()

    # ── Resource helpers ──────────────────────────────────────────────────────

    def get_resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(base_path, relative_path)

    def set_master_icon(self):
        try:
            p = self.get_resource_path("logo.ico")
            if os.path.exists(p):
                self.master.iconbitmap(p)
        except Exception:
            pass

    def set_window_icon(self):
        try:
            p = self.get_resource_path("logo.ico")
            if os.path.exists(p):
                self.window.iconbitmap(p)
        except Exception:
            pass

    # ── GUI Setup ─────────────────────────────────────────────────────────────

    def setup_gui(self):
        self.window = tk.Toplevel(self.master)
        self.window.title("COM to vJoy")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.configure(bg=C_BG)
        self.window.resizable(False, False)
        self.set_window_icon()
        self._apply_ttk_style()

        # ── Title bar ─────────────────────────────────────────────────────────
        title_bar = tk.Frame(self.window, bg=C_PANEL, height=48)
        title_bar.pack(fill='x')
        title_bar.pack_propagate(False)
        tk.Label(title_bar, text="⬡", font=(FONT, 18, "bold"),
                 fg=C_ACCENT, bg=C_PANEL).pack(side='left', padx=(16, 6), pady=8)
        tk.Label(title_bar, text="COM to vJoy",
                 font=(FONT, 13, "bold"), fg=C_FG, bg=C_PANEL).pack(side='left', pady=8)
        tk.Label(title_bar, text="by SurangaX",
                 font=(FONT, 8), fg=C_LABEL, bg=C_PANEL).pack(side='left', padx=(6, 0), pady=14)

        # ── Steering wheel ─────────────────────────────────────────────────────
        vis_frame = tk.Frame(self.window, bg=C_BG)
        vis_frame.pack(fill='x', padx=16, pady=(16, 0))

        self.wheel_canvas = WheelCanvas(vis_frame, size=220)
        self.wheel_canvas.pack()

        # Degree readout
        self.angle_label = tk.Label(vis_frame, text="0.0°",
                                    font=(FONT_MONO, 13, "bold"),
                                    fg=C_ACCENT, bg=C_BG)
        self.angle_label.pack(pady=(8, 0))

        # Center wheel — ghost button directly below degree readout
        center_btn = tk.Button(vis_frame,
                               text="🎯  Center Wheel",
                               font=(FONT, 9),
                               fg=C_ACCENT, bg=C_BG,
                               activebackground=C_CARD,
                               activeforeground=C_ACCENT,
                               relief='flat', bd=0,
                               highlightthickness=1,
                               highlightbackground=C_ACCENT,
                               padx=16, pady=5,
                               command=self.trigger_center,
                               cursor="hand2")
        center_btn.pack(pady=(8, 0))

        # ── Button LEDs — single horizontal row ───────────────────────────────
        led_row = tk.Frame(self.window, bg=C_BG)
        led_row.pack(pady=(14, 6))

        LED = 32
        for n in range(1, 7):
            cell = tk.Frame(led_row, bg=C_BG)
            cell.pack(side='left', padx=7)
            c = tk.Canvas(cell, width=LED, height=LED, bg=C_BG, highlightthickness=0)
            c.pack()
            oval = c.create_oval(2, 2, LED-2, LED-2,
                                 fill=C_PANEL, outline=C_BORDER, width=1)
            txt  = c.create_text(LED//2, LED//2, text=f"B{n}",
                                 font=(FONT, 7, "bold"), fill=C_LABEL)
            self.btn_leds[n] = (c, oval, txt)

        # ── Separator ─────────────────────────────────────────────────────────
        self._separator()

        # ── Settings card ─────────────────────────────────────────────────────
        # 1-px border achieved by thin outer frame in border colour
        card_border = tk.Frame(self.window, bg=C_BORDER, padx=1, pady=1)
        card_border.pack(fill='x', padx=16, pady=(10, 8))
        card = tk.Frame(card_border, bg=C_CARD, padx=18, pady=14)
        card.pack(fill='both', expand=True)

        # Row 1 — PORT (left) | vJOY DEVICE (right)
        row1 = tk.Frame(card, bg=C_CARD)
        row1.pack(fill='x', pady=(0, 10))

        # PORT column
        port_col = tk.Frame(row1, bg=C_CARD)
        port_col.pack(side='left', fill='x', expand=True, padx=(0, 10))

        tk.Label(port_col, text="PORT", font=(FONT, 7, "bold"),
                 fg=C_LABEL, bg=C_CARD, anchor='w').pack(anchor='w', pady=(0, 3))

        port_input = tk.Frame(port_col, bg=C_CARD)
        port_input.pack(fill='x')
        self.com_combobox = ttk.Combobox(port_input, width=12,
                                          state="readonly", font=(FONT, 9))
        self.com_combobox.pack(side='left', fill='x', expand=True)
        tk.Button(port_input, text="⟳",
                  font=(FONT, 10), fg=C_LABEL, bg=C_PANEL2,
                  activebackground=C_BTN_HOV, activeforeground=C_FG,
                  relief='flat', bd=0, padx=7, pady=1,
                  command=self.refresh_ports,
                  cursor="hand2").pack(side='left', padx=(4, 0))

        # vJOY DEVICE column
        vjoy_col = tk.Frame(row1, bg=C_CARD)
        vjoy_col.pack(side='right')

        tk.Label(vjoy_col, text="vJOY DEVICE", font=(FONT, 7, "bold"),
                 fg=C_LABEL, bg=C_CARD, anchor='w').pack(anchor='w', pady=(0, 3))
        self.vjoy_combobox = ttk.Combobox(vjoy_col, width=5, state="readonly",
                                           font=(FONT, 9),
                                           values=[str(i) for i in range(1, 17)])
        self.vjoy_combobox.pack()
        self.vjoy_combobox.current(0)

        # Row 2 — SENSOR (left) | STEERING LOCK (right)
        row2 = tk.Frame(card, bg=C_CARD)
        row2.pack(fill='x', pady=(0, 10))

        sensor_col = tk.Frame(row2, bg=C_CARD)
        sensor_col.pack(side='left', fill='x', expand=True, padx=(0, 10))

        tk.Label(sensor_col, text="SENSOR", font=(FONT, 7, "bold"),
                 fg=C_LABEL, bg=C_CARD, anchor='w').pack(anchor='w', pady=(0, 3))
        self.sensor_type = ttk.Combobox(sensor_col, state="readonly",
                                         font=(FONT, 9),
                                         values=["Potentiometer",
                                                 "AS5600 Magnetic",
                                                 "Combined (Pot=X, Mag=Y)"])
        self.sensor_type.pack(fill='x')
        self.sensor_type.current(1)

        lock_col = tk.Frame(row2, bg=C_CARD)
        lock_col.pack(side='right')

        tk.Label(lock_col, text="STEERING LOCK", font=(FONT, 7, "bold"),
                 fg=C_LABEL, bg=C_CARD, anchor='w').pack(anchor='w', pady=(0, 3))
        self.degree_var = ttk.Combobox(lock_col, width=6, state="readonly",
                                        font=(FONT, 9),
                                        values=["180", "270", "360",
                                                "540", "900", "1080"])
        self.degree_var.pack()
        self.degree_var.current(4)

        # Row 3 — CENTER HOTKEY (inline ✓/✕ icons)
        tk.Label(card, text="CENTER HOTKEY", font=(FONT, 7, "bold"),
                 fg=C_LABEL, bg=C_CARD, anchor='w').pack(anchor='w', pady=(0, 3))

        # Fake-entry frame: same bg as entry so it looks like one widget with inline icons
        hotkey_shell = tk.Frame(card, bg=C_PANEL2,
                                highlightbackground=C_BORDER,
                                highlightthickness=1)
        hotkey_shell.pack(fill='x')

        self.hotkey_var = tk.StringVar(value=self.center_hotkey)
        self.hotkey_entry = tk.Entry(hotkey_shell,
                                     textvariable=self.hotkey_var,
                                     font=(FONT_MONO, 9),
                                     bg=C_PANEL2, fg=C_ACCENT,
                                     insertbackground=C_ACCENT,
                                     relief='flat', bd=0,
                                     highlightthickness=0)
        self.hotkey_entry.pack(side='left', fill='x', expand=True,
                               padx=(8, 0), ipady=5)

        # Inline clear button
        clear_lbl = tk.Label(hotkey_shell, text=" ✕ ", font=(FONT, 9),
                             fg=C_LABEL, bg=C_PANEL2, cursor="hand2", pady=0)
        clear_lbl.pack(side='right', padx=(0, 2))
        clear_lbl.bind("<Button-1>", lambda e: self._clear_hotkey())
        clear_lbl.bind("<Enter>", lambda e: clear_lbl.config(fg=C_ERROR))
        clear_lbl.bind("<Leave>", lambda e: clear_lbl.config(fg=C_LABEL))

        # Divider between buttons
        tk.Frame(hotkey_shell, bg=C_BORDER, width=1).pack(
            side='right', fill='y', pady=4)

        # Inline apply button
        apply_lbl = tk.Label(hotkey_shell, text=" ✓ ", font=(FONT, 9, "bold"),
                             fg=C_LABEL, bg=C_PANEL2, cursor="hand2", pady=0)
        apply_lbl.pack(side='right')
        apply_lbl.bind("<Button-1>", lambda e: self._apply_hotkey())
        apply_lbl.bind("<Enter>", lambda e: apply_lbl.config(fg=C_SUCCESS))
        apply_lbl.bind("<Leave>", lambda e: apply_lbl.config(fg=C_LABEL))

        # Hotkey hint
        hint = ("⚠  keyboard module not found — hotkey unavailable"
                if not KEYBOARD_AVAILABLE
                else "Global hotkey — works even when minimized to tray")
        tk.Label(card, text=hint,
                 font=(FONT, 7, "italic"),
                 fg=C_WARNING if not KEYBOARD_AVAILABLE else C_LABEL,
                 bg=C_CARD).pack(anchor='w', pady=(5, 0))

        # ── Separator ─────────────────────────────────────────────────────────
        self._separator()

        # ── Connect / Disconnect button ────────────────────────────────────────
        conn_wrap = tk.Frame(self.window, bg=C_BG, padx=16, pady=10)
        conn_wrap.pack(fill='x')

        self.connect_btn = tk.Button(conn_wrap,
                                     text="▶  CONNECT",
                                     font=(FONT, 11, "bold"),
                                     fg="#000000", bg=C_SUCCESS,
                                     activebackground="#00cc70",
                                     activeforeground="#000000",
                                     relief='flat', bd=0,
                                     pady=10,
                                     command=self.toggle_connection,
                                     cursor="hand2")
        self.connect_btn.pack(fill='x')

        # ── Separator ─────────────────────────────────────────────────────────
        self._separator()

        # ── Unified footer bar ─────────────────────────────────────────────────
        footer = tk.Frame(self.window, bg=C_PANEL, padx=14, pady=8)
        footer.pack(fill='x')

        # Status — far left
        status_left = tk.Frame(footer, bg=C_PANEL)
        status_left.pack(side='left', fill='y')

        self.status_dot = tk.Label(status_left, text="●",
                                   font=(FONT, 9), fg=C_LABEL, bg=C_PANEL)
        self.status_dot.pack(side='left')
        self.status_text = tk.Label(status_left, text="IDLE",
                                    font=(FONT, 9), fg=C_LABEL, bg=C_PANEL, anchor='w')
        self.status_text.pack(side='left', padx=(5, 0))

        # Buttons — far right
        quit_btn = tk.Button(footer, text="✕  Quit",
                             font=(FONT, 9, "bold"),
                             fg=C_ERROR, bg=C_PANEL,
                             activebackground=C_BTN_HOV, activeforeground=C_ERROR,
                             relief='flat', bd=0, padx=10, pady=4,
                             command=self.safe_quit, cursor="hand2")
        quit_btn.pack(side='right', padx=(8, 0))

        tray_btn = tk.Button(footer, text="📍  Tray",
                             font=(FONT, 9),
                             fg=C_LABEL, bg=C_PANEL,
                             activebackground=C_BTN_HOV, activeforeground=C_FG,
                             relief='flat', bd=0, padx=10, pady=4,
                             command=self.minimize_to_tray, cursor="hand2")
        tray_btn.pack(side='right')

        # Final sizing — centre on screen
        self.refresh_ports()
        self.window.update_idletasks()
        w, h = 420, self.window.winfo_reqheight()
        sw   = self.window.winfo_screenwidth()
        sh   = self.window.winfo_screenheight()
        self.window.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── Widget helpers ────────────────────────────────────────────────────────

    def _separator(self):
        tk.Frame(self.window, bg=C_BORDER, height=1).pack(fill='x')

    def _apply_ttk_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox',
                        fieldbackground=C_PANEL2,
                        background=C_BTN_BG,
                        foreground=C_FG,
                        borderwidth=0,
                        focuscolor='none',
                        arrowcolor=C_LABEL)
        style.map('TCombobox',
                  fieldbackground=[('readonly', C_PANEL2)],
                  selectbackground=[('readonly', C_PANEL)],
                  selectforeground=[('readonly', C_FG)])

    # ── LED update ────────────────────────────────────────────────────────────

    def _update_led(self, n, pressed: bool):
        if n not in self.btn_leds:
            return
        canvas, oval, txt = self.btn_leds[n]
        if pressed:
            canvas.itemconfig(oval, fill=C_ACCENT, outline=C_ACCENT, width=2)
            canvas.itemconfig(txt, fill="#000000")
        else:
            canvas.itemconfig(oval, fill=C_PANEL, outline=C_BORDER, width=1)
            canvas.itemconfig(txt, fill=C_LABEL)

    # ── Wheel angle update ────────────────────────────────────────────────────

    def _update_wheel(self, angle_deg: float):
        self.current_angle = angle_deg
        self.wheel_canvas.set_angle(angle_deg)
        sign = "+" if angle_deg >= 0 else ""
        self.angle_label.config(text=f"{sign}{angle_deg:.1f}°")

    # ── Status helpers ────────────────────────────────────────────────────────

    def _set_status(self, msg, color=C_LABEL, dot_color=None):
        self.status_text.config(text=msg, fg=color)
        self.status_dot.config(fg=dot_color or color)

    # ── Port management ───────────────────────────────────────────────────────

    def get_available_ports(self):
        result = []
        for p in serial.tools.list_ports.comports():
            if p.description and p.description != 'n/a':
                result.append(f"{p.device} - {p.description}")
            else:
                result.append(p.device)
        return result

    def refresh_ports(self):
        try:
            ports = self.get_available_ports()
            self.com_combobox['values'] = ports
            if ports:
                cur = self.com_combobox.get()
                if not cur or cur not in ports:
                    self.com_combobox.current(0)
                self._set_status(f"Found {len(ports)} port(s)")
            else:
                self.com_combobox.set("")
                self._set_status("No COM ports found", C_WARNING, C_WARNING)
        except Exception as e:
            self._set_status(f"Scan error: {e}", C_ERROR, C_ERROR)

    # ── Connection toggle ─────────────────────────────────────────────────────

    def toggle_connection(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        if self.running:
            return
        try:
            sel = self.com_combobox.get()
            if not sel:
                messagebox.showerror("Error", "Please select a COM port")
                return
            dev  = int(self.vjoy_combobox.get())
            port = sel.split(" - ")[0] if " - " in sel else sel
            self.ser         = serial.Serial(port, 115200, timeout=1)
            self.vjoy_device = pyvjoy.VJoyDevice(dev)
            self.selected_vjoy_device = dev
            self.running = True

            self._set_status(f"CONNECTED  {port}  →  vJoy {dev}", C_SUCCESS, C_SUCCESS)
            # Muted disconnect button: dark bg, red text — glows red on hover
            self.connect_btn.config(
                text="⏹  DISCONNECT",
                bg=C_ERROR_DIM,
                fg=C_ERROR,
                activebackground=C_ERROR,
                activeforeground="#ffffff"
            )
            threading.Thread(target=self.read_serial, daemon=True).start()
            self._register_hotkey()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self._set_status(f"Error: {e}", C_ERROR, C_ERROR)

    def stop(self):
        if not self.running:
            return
        self.running = False
        time.sleep(0.2)
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.ser = None
        except Exception:
            pass
        if self.vjoy_device:
            for b in range(1, 7):
                self.vjoy_device.set_button(b, 0)
            self.vjoy_device = None

        for n in range(1, 7):
            self._update_led(n, False)
        self._update_wheel(0.0)

        self._set_status("DISCONNECTED", C_ERROR, C_ERROR)
        self.connect_btn.config(
            text="▶  CONNECT",
            bg=C_SUCCESS, fg="#000000",
            activebackground="#00cc70",
            activeforeground="#000000"
        )
        self._unregister_hotkey()

    def trigger_center(self):
        self.request_center = True
        self._set_status("Centering… move wheel to center position", C_WARNING, C_WARNING)

    # ── Hotkey management ─────────────────────────────────────────────────────

    def _register_hotkey(self):
        if not KEYBOARD_AVAILABLE:
            return
        hotkey = self.hotkey_var.get().strip().lower()
        if not hotkey:
            return
        try:
            self._unregister_hotkey()
            keyboard.add_hotkey(hotkey, self._hotkey_triggered)
            self.center_hotkey     = hotkey
            self.hotkey_registered = True
        except Exception as e:
            self._set_status(f"Hotkey error: {e}", C_WARNING, C_WARNING)

    def _unregister_hotkey(self):
        if not KEYBOARD_AVAILABLE or not self.hotkey_registered:
            return
        try:
            keyboard.remove_hotkey(self.center_hotkey)
        except Exception:
            pass
        self.hotkey_registered = False

    def _hotkey_triggered(self):
        self.master.after(0, self.trigger_center)

    def _apply_hotkey(self):
        if not KEYBOARD_AVAILABLE:
            messagebox.showwarning("Hotkey", "The 'keyboard' library is not available.")
            return
        hk = self.hotkey_var.get().strip().lower()
        if not hk:
            messagebox.showwarning("Hotkey", "Please enter a hotkey (e.g. ctrl+shift+c).")
            return
        try:
            keyboard.parse_hotkey(hk)
        except Exception:
            messagebox.showerror("Invalid Hotkey",
                                 f"'{hk}' is not a valid hotkey.\n\n"
                                 "Examples: ctrl+shift+c  |  alt+c  |  f9")
            return
        if self.running:
            self._register_hotkey()
            self._set_status(f"Hotkey active: {hk}", C_ACCENT, C_ACCENT)
        else:
            self.center_hotkey = hk
            self._set_status(f"Hotkey saved: {hk}  (activates on connect)")

    def _clear_hotkey(self):
        self._unregister_hotkey()
        self.hotkey_var.set("")
        self.center_hotkey = ""
        self._set_status("Hotkey cleared")

    # ── Serial reading ────────────────────────────────────────────────────────

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
                self.master.after(0, lambda: messagebox.showerror("Serial Error", str(e)))
            self.master.after(0, self.stop)

    def process_line(self, line):
        mode = self.sensor_type.get()

        # Potentiometer
        if "Smoothed Potentiometer Value:" in line:
            if mode in ["Potentiometer", "Combined (Pot=X, Mag=Y)"]:
                try:
                    value  = int(line.split(":")[1].strip())
                    scaled = int((value / 1023) * 32767)
                    scaled = max(0, min(32767, scaled))
                    self.vjoy_device.set_axis(pyvjoy.HID_USAGE_X, scaled)
                    degrees = int(self.degree_var.get())
                    angle   = ((value / 1023) - 0.5) * degrees
                    self.master.after(0, lambda a=angle: self._update_wheel(a))
                except Exception:
                    pass

        # AS5600 magnetic sensor
        elif "AS5600 Angle:" in line:
            if mode in ["AS5600 Magnetic", "Combined (Pot=X, Mag=Y)"]:
                try:
                    value = int(line.split(":")[1].strip())
                    if self.request_center:
                        self.center_offset  = value
                        self.request_center = False
                        # Use muted green — not neon — so it doesn't clash with cyan
                        self.master.after(0, lambda: self._set_status(
                            "Wheel centered ✓", C_SUCCESS_MUT, C_SUCCESS_MUT))
                    degrees    = int(self.degree_var.get())
                    max_units  = (degrees / 360.0) * 4096
                    half_range = max_units / 2.0
                    adjusted   = value - self.center_offset
                    mapped     = ((adjusted + half_range) / max_units) * 32767
                    scaled     = int(max(0, min(32767, mapped)))
                    if mode == "Combined (Pot=X, Mag=Y)":
                        self.vjoy_device.set_axis(pyvjoy.HID_USAGE_Y, scaled)
                    else:
                        self.vjoy_device.set_axis(pyvjoy.HID_USAGE_X, scaled)
                    angle = (adjusted / 4096.0) * 360.0
                    self.master.after(0, lambda a=angle: self._update_wheel(a))
                except Exception:
                    pass

        # Button states
        for i in range(1, 7):
            if f"Button {i} pressed!" in line:
                self.vjoy_device.set_button(i, 1)
                self.master.after(0, lambda n=i: self._update_led(n, True))
            elif f"Button {i} released!" in line:
                self.vjoy_device.set_button(i, 0)
                self.master.after(0, lambda n=i: self._update_led(n, False))

    # ── Tray icon ─────────────────────────────────────────────────────────────

    def create_tray_icon(self):
        try:
            p = self.get_resource_path("logo.ico")
            if os.path.exists(p):
                img = Image.open(p)
            else:
                raise FileNotFoundError
        except Exception:
            img  = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((4, 4, 60, 60), fill="#0d0d0d", outline="#00d4ff", width=3)
            draw.ellipse((18, 18, 46, 46), outline="#00d4ff", width=2, fill="#141414")

        def on_activate():
            try:
                self.master.after(0, self.open_window_safe)
            except Exception:
                pass

        self.icon = pystray.Icon(
            "COM_to_vJoy", img, "COM to vJoy",
            menu=self.create_tray_menu()
        )
        self.icon.default_action = on_activate
        self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.tray_thread.start()

    def create_tray_menu(self):
        return pystray.Menu(
            item('Open',  self.open_window, default=True),
            item('Start', lambda icon, item: self.master.after(0, self.start)),
            item('Stop',  lambda icon, item: self.master.after(0, self.stop)),
            item('Exit',  lambda icon, item: self.master.after(0, self.force_quit))
        )

    def open_window_safe(self):
        try:
            self.window.deiconify()
            self.window.state('normal')
            self.window.lift()
            self.window.focus_force()
            self.window.attributes('-topmost', True)
            self.window.after(100, lambda: self.window.attributes('-topmost', False))
            if hasattr(self, 'icon') and self.icon:
                self.icon.visible = False
        except Exception as e:
            print(f"Restore error: {e}")

    def open_window(self, icon=None, item=None):
        try:
            self.master.after(0, self.open_window_safe)
        except Exception:
            pass

    def minimize_to_tray(self):
        try:
            self.window.withdraw()
            if self.icon:
                self.icon.visible = True
                try:
                    self.icon.notify('COM to vJoy', 'Running in system tray')
                except Exception:
                    pass
        except Exception as e:
            print(f"Tray minimize error: {e}")

    # ── Quit ──────────────────────────────────────────────────────────────────

    def safe_quit(self):
        try:
            if self.running:
                self.stop()
            res = messagebox.askquestion("Quit",
                                         "Are you sure you want to quit COM to vJoy?",
                                         icon='warning')
            if res == 'yes':
                self.force_quit()
        except Exception:
            self.force_quit()

    def on_close(self):
        self.minimize_to_tray()

    def force_quit(self):
        try:
            self._unregister_hotkey()
            self.stop()
            if self.icon:
                self.icon.visible = False
                self.icon.stop()
            self.window.destroy()
            self.master.destroy()
        except Exception as e:
            print("Quit error:", e)
        finally:
            os._exit(0)


# ─── Single Instance Guard ────────────────────────────────────────────────────

class SingleInstance:
    def __init__(self, app_name="COM_to_vJoy"):
        self.app_name       = app_name
        self.lock_file_path = os.path.join(tempfile.gettempdir(), f"{app_name}.lock")
        self.lock_file      = None

    def __enter__(self):
        try:
            self.lock_file = open(self.lock_file_path, 'w')
            if os.name == 'nt':
                try:
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                except IOError:
                    self.lock_file.close()
                    return False
            else:
                try:
                    fcntl.lockf(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except IOError:
                    self.lock_file.close()
                    return False
            self.lock_file.write(str(os.getpid()))
            self.lock_file.flush()
            atexit.register(self.cleanup)
            return True
        except Exception:
            if self.lock_file:
                self.lock_file.close()
            return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def cleanup(self):
        if self.lock_file:
            try:
                self.lock_file.close()
            except Exception:
                pass
        try:
            if os.path.exists(self.lock_file_path):
                os.remove(self.lock_file_path)
        except Exception:
            pass


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    missing = check_system_requirements()
    if missing:
        show_requirements_dialog(missing)
        sys.exit(1)

    single = SingleInstance()
    if not single.__enter__():
        tmp = tk.Tk()
        tmp.withdraw()
        messagebox.showwarning("Already Running",
                               "COM to vJoy is already running!\nCheck your system tray.")
        tmp.destroy()
        sys.exit(0)

    try:
        root = tk.Tk()
        root.withdraw()
        app = VJoyApp(root)
        root.mainloop()
    finally:
        single.__exit__(None, None, None)
