#!/usr/bin/env python3
"""
Pathologic Classic HD - Auto-Walk Mod (Windows)
Only sends W when the Pathologic window is focused.
Includes a settings GUI for changing hotkeys.

Requirements:
    pip install pynput pywin32
"""

import os
import sys
import ctypes
import ctypes.wintypes
import threading
import tkinter as tk
from tkinter import ttk
from pynput.keyboard import Key, Controller, Listener, KeyCode

# --- Win32 focus detection ---
user32 = ctypes.windll.user32
GetForegroundWindow = user32.GetForegroundWindow
GetWindowThreadProcessId = user32.GetWindowThreadProcessId

psapi = ctypes.windll.psapi
kernel32 = ctypes.windll.kernel32

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
GAME_EXE = "game.exe"


def get_foreground_exe():
    """Return the lowercase .exe name of the currently focused window."""
    hwnd = GetForegroundWindow()
    if not hwnd:
        return ""
    pid = ctypes.wintypes.DWORD()
    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return ""
    buf = ctypes.create_unicode_buffer(260)
    psapi.GetModuleFileNameExW(handle, None, buf, 260)
    kernel32.CloseHandle(handle)
    return buf.value.split("\\")[-1].lower()


def game_is_focused():
    return get_foreground_exe() == GAME_EXE


# --- Key mappings ---
SPECIAL_KEYS = {
    "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
    "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
    "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
}


def parse_key(s):
    s = s.strip().lower()
    if s in SPECIAL_KEYS:
        return SPECIAL_KEYS[s]
    if len(s) == 1 and s.isalnum():
        return KeyCode.from_char(s)
    return None


def key_name(k):
    for name, val in SPECIAL_KEYS.items():
        if k == val:
            return name.upper()
    if isinstance(k, KeyCode):
        return k.char.upper()
    return str(k)


# --- State ---
kb = Controller()
walking = False
toggle_key = Key.f9
quit_key = Key.f10
walk_char = "w"
app_quit = threading.Event()


def set_walking(state):
    global walking
    if state == walking:
        return
    walking = state
    if walking and game_is_focused():
        kb.press(walk_char)
    else:
        kb.release(walk_char)


# --- Focus monitor thread ---
def focus_monitor():
    was_focused = False
    while not app_quit.is_set():
        focused = game_is_focused()
        if walking:
            if focused and not was_focused:
                kb.press(walk_char)
            elif not focused and was_focused:
                kb.release(walk_char)
        was_focused = focused
        app_quit.wait(0.25)


# --- Keyboard listener ---
def on_press(key):
    if key == toggle_key:
        set_walking(not walking)
        root.after(0, update_status)
    elif key == quit_key:
        set_walking(False)
        app_quit.set()
        root.after(0, root.destroy)
        return False


def update_status():
    if not status_label.winfo_exists():
        return
    if walking:
        status_label.config(text="Auto-Walk: ON", foreground="#4CAF50")
        focus_info.config(text="(only active in Pathologic window)")
    else:
        status_label.config(text="Auto-Walk: OFF", foreground="#f44336")
        focus_info.config(text="")


def apply_settings():
    global toggle_key, quit_key, walk_char
    new_toggle = parse_key(toggle_entry.get())
    new_quit = parse_key(quit_entry.get())
    new_walk = walk_entry.get().strip().lower()
    if not new_toggle or not new_quit or len(new_walk) != 1:
        result_label.config(text="Invalid key — use a letter or f1-f12", foreground="#f44336")
        return
    was_walking = walking
    if was_walking:
        set_walking(False)
    toggle_key = new_toggle
    quit_key = new_quit
    walk_char = new_walk
    if was_walking:
        set_walking(True)
    result_label.config(text="Applied!", foreground="#4CAF50")
    toggle_hint.config(text=f"Press {key_name(toggle_key)} to toggle, {key_name(quit_key)} to quit")


# --- GUI ---
root = tk.Tk()
root.title("Pathologic Classic HD — Auto-Walk")
root.resizable(False, False)

# Set window icon
icon_path = os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(__file__)), "icon.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

frame = ttk.Frame(root, padding=16)
frame.grid()

status_label = ttk.Label(frame, text="Auto-Walk: OFF", font=("", 14, "bold"), foreground="#f44336")
status_label.grid(row=0, column=0, columnspan=2, pady=(0, 2))

focus_info = ttk.Label(frame, text="", foreground="gray")
focus_info.grid(row=1, column=0, columnspan=2, pady=(0, 10))

toggle_hint = ttk.Label(frame, text=f"Press {key_name(toggle_key)} to toggle, {key_name(quit_key)} to quit")
toggle_hint.grid(row=2, column=0, columnspan=2, pady=(0, 12))

sep = ttk.Separator(frame, orient="horizontal")
sep.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 12))

ttk.Label(frame, text="Toggle key:").grid(row=4, column=0, sticky="e", padx=(0, 8), pady=2)
toggle_entry = ttk.Entry(frame, width=10)
toggle_entry.insert(0, "f9")
toggle_entry.grid(row=4, column=1, pady=2)

ttk.Label(frame, text="Quit key:").grid(row=5, column=0, sticky="e", padx=(0, 8), pady=2)
quit_entry = ttk.Entry(frame, width=10)
quit_entry.insert(0, "f10")
quit_entry.grid(row=5, column=1, pady=2)

ttk.Label(frame, text="Walk key:").grid(row=6, column=0, sticky="e", padx=(0, 8), pady=2)
walk_entry = ttk.Entry(frame, width=10)
walk_entry.insert(0, "w")
walk_entry.grid(row=6, column=1, pady=2)

ttk.Button(frame, text="Apply", command=apply_settings).grid(row=7, column=0, columnspan=2, pady=(12, 4))

result_label = ttk.Label(frame, text="")
result_label.grid(row=8, column=0, columnspan=2)

ttk.Label(
    frame,
    text=f"W key is only sent when Game.exe is focused.",
    foreground="gray",
).grid(row=9, column=0, columnspan=2, pady=(8, 0))

# --- Start ---
listener = Listener(on_press=on_press)
listener.daemon = True
listener.start()

monitor_thread = threading.Thread(target=focus_monitor, daemon=True)
monitor_thread.start()

root.protocol("WM_DELETE_WINDOW", lambda: (set_walking(False), app_quit.set(), root.destroy()))
root.mainloop()
