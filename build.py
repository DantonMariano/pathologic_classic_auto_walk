"""
Build script — creates a single autowalk.exe for Windows.

Requirements (install on your Windows machine):
    pip install pyinstaller pynput pywin32

Usage:
    python build.py
"""

import PyInstaller.__main__

PyInstaller.__main__.run([
    "autowalk.py",
    "--onefile",
    "--windowed",
    "--name=PathologicAutoWalk",
    "--icon=icon.ico",
    "--add-data=icon.ico;.",
    "--noupx",
])
