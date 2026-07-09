# -*- coding: utf-8 -*-
"""Capture File Explorer reliably: MAXIMIZE the window (so nothing else is visible),
real screenshot, then crop off the left nav pane (author's personal pins) + taskbar.
Maximized-window capture is privacy-safe because a maximized window fully covers the
desktop; PrintWindow can't render Win11 Explorer's WinUI chrome, so we screenshot."""
import sys, time, subprocess, ctypes
from pathlib import Path
import pyautogui
sys.path.insert(0, r"C:\Users\user\YLBooks\book2\tools")
import winshot

OUT = Path(r"C:\Users\user\YLBooks\book2\images\c04")
OUT.mkdir(parents=True, exist_ok=True)
FOLDER = r"C:\Users\user\Desktop\rhythm-game"

def cap(folder, title, name, nav=360, taskbar=56, topkeep=True):
    subprocess.Popen(["explorer.exe", folder]); time.sleep(3.0)
    c = winshot.find(title, "CabinetWClass")
    if not c:
        print("  ! not found", title); return
    hwnd = c[0][0]
    ctypes.windll.user32.ShowWindow(hwnd, 3)   # SW_MAXIMIZE
    try: ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception: pass
    time.sleep(1.6)
    img = pyautogui.screenshot()
    W, H = img.size
    img = img.crop((nav, 0, W, H - taskbar))   # drop nav pane + taskbar
    p = str(OUT / name); img.save(p)
    print("  + saved", name, img.size)

if __name__ == "__main__":
    cap(FOLDER, "rhythm-game", "c04_explorer_folder.png")
    print("explorer shot done")
