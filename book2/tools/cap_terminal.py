# -*- coding: utf-8 -*-
"""Capture REAL PowerShell (legacy conhost) windows via PrintWindow — window-only,
no desktop leak. Forces conhost so PrintWindow returns real pixels (Windows Terminal
is GPU-rendered and prints black)."""
import sys, time, subprocess, ctypes
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"C:\Users\user\YLBooks\book2\tools")
import winshot

OUT = Path(r"C:\Users\user\YLBooks\book2\images")
DESK = r"C:\Users\user\Desktop\rhythm-game"
TITLE = "Windows PowerShell"

# (out_relpath, powershell_body)
SHOTS = [
    ("c03/c03_ps_open.png",      f"Set-Location '{DESK}'; Clear-Host"),
    ("c03/c03_ps_help.png",      f"Set-Location '{DESK}'; Clear-Host; Write-Output 'Hello, PowerShell!'"),
    ("c05/c05_node_check.png",   f"Set-Location '{DESK}'; Clear-Host; node -v; npm -v"),
    ("c06/c06_claude_version.png", f"Set-Location '{DESK}'; Clear-Host; claude --version"),
]

def crop_terminal(path):
    im = Image.open(path).convert("RGB"); w, h = im.size
    px = im.load(); last = 0
    for y in range(h):
        for x in range(0, w - 18, 4):
            r, g, b = px[x, y]
            if r + g + b > 120:
                last = y; break
    bottom = min(h, last + 26)
    im.crop((0, 0, w - 4, bottom)).save(path)

def run():
    for rel, body in SHOTS:
        cmd = (f"$host.ui.RawUI.WindowTitle='{TITLE}'; "
               f"try{{$b=New-Object System.Management.Automation.Host.Size(90,40); "
               f"$host.ui.RawUI.BufferSize=$b; "
               f"$w=New-Object System.Management.Automation.Host.Size(90,14); "
               f"$host.ui.RawUI.WindowSize=$w}}catch{{}}; {body}")
        subprocess.Popen(["conhost.exe", "powershell.exe", "-NoLogo", "-NoExit", "-Command", cmd])
        hwnd = None
        for _ in range(20):
            time.sleep(0.5)
            c = winshot.find(TITLE, "ConsoleWindowClass")
            if c:
                hwnd = c[0][0]; break
        if not hwnd:
            print("  ! window not found for", rel); continue
        try: ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception: pass
        time.sleep(1.2)
        winshot.capture(hwnd, str(OUT / rel))
        try: crop_terminal(str(OUT / rel))
        except Exception as e: print("  crop skip:", e)
        print("    cropped", rel)
        try: ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
        except Exception: pass
        time.sleep(0.5)

if __name__ == "__main__":
    run()
    print("terminal shots done")
