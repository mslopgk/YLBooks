# -*- coding: utf-8 -*-
"""Privacy-safe single-window capture (Windows PrintWindow).

Captures ONLY the target window's own pixels via PrintWindow(PW_RENDERFULLCONTENT),
so overlapping/other windows never leak into the image (unlike full-screen grab+crop).

Usage:
  python winshot.py --out img.png --title "탐색기" [--class CabinetWClass]
  python winshot.py --out img.png --launch "explorer.exe" --args "C:\\path" --match-class CabinetWClass --wait 2.5
  python winshot.py --list            # list visible window titles+classes (debug)
"""
import argparse, sys, time, subprocess, ctypes
from ctypes import wintypes
from pathlib import Path
from PIL import Image

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
try: ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try: user32.SetProcessDPIAware()
    except Exception: pass

PW_RENDERFULLCONTENT = 0x00000002

def enum_windows():
    out = []
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def cb(h, l):
        if not user32.IsWindowVisible(h):
            return True
        n = user32.GetWindowTextLengthW(h)
        title = ""
        if n:
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(h, buf, n + 1); title = buf.value
        cbuf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(h, cbuf, 256)
        out.append((h, title, cbuf.value))
        return True
    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return out

def find(title=None, cls=None):
    cands = []
    for h, t, c in enum_windows():
        if title and title.lower() not in (t or "").lower():
            continue
        if cls and cls.lower() != (c or "").lower():
            continue
        if not t:  # skip untitled shells
            continue
        cands.append((h, t, c))
    return cands

def capture(hwnd, out):
    rect = wintypes.RECT()
    # DwmGetWindowAttribute(9=EXTENDED_FRAME_BOUNDS) gives a tight rect w/o shadow
    try:
        f = wintypes.RECT()
        ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(f), ctypes.sizeof(f))
        rect = f if (f.right - f.left) > 0 else rect
    except Exception:
        pass
    if (rect.right - rect.left) <= 0:
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w, h = rect.right - rect.left, rect.bottom - rect.top
    if w <= 0 or h <= 0:
        sys.exit("bad window size")
    hwndDC = user32.GetWindowDC(hwnd)
    mfcDC = gdi32.CreateCompatibleDC(hwndDC)
    bmp = gdi32.CreateCompatibleBitmap(hwndDC, w, h)
    gdi32.SelectObject(mfcDC, bmp)
    ok = user32.PrintWindow(hwnd, mfcDC, PW_RENDERFULLCONTENT)
    # BITMAPINFO for 32-bit top-down DIB
    class BMIH(ctypes.Structure):
        _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG),
                    ("biHeight", wintypes.LONG), ("biPlanes", wintypes.WORD),
                    ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
                    ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG),
                    ("biYPelsPerMeter", wintypes.LONG), ("biClrUsed", wintypes.DWORD),
                    ("biClrImportant", wintypes.DWORD)]
    bmi = BMIH(); bmi.biSize = ctypes.sizeof(BMIH); bmi.biWidth = w
    bmi.biHeight = -h; bmi.biPlanes = 1; bmi.biBitCount = 32; bmi.biCompression = 0
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(mfcDC, bmp, 0, h, buf, ctypes.byref(bmi), 0)
    img = Image.frombuffer("RGB", (w, h), buf, "raw", "BGRX", 0, 1)
    gdi32.DeleteObject(bmp); gdi32.DeleteDC(mfcDC); user32.ReleaseDC(hwnd, hwndDC)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"  + saved {out}  {img.size}  printwindow_ok={bool(ok)}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out"); ap.add_argument("--title"); ap.add_argument("--class", dest="cls")
    ap.add_argument("--launch"); ap.add_argument("--args", default="")
    ap.add_argument("--match-class"); ap.add_argument("--wait", type=float, default=2.0)
    ap.add_argument("--activate", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for h, t, c in enum_windows():
            if t: print(f"  [{c}] {t}")
        return
    if a.launch:
        subprocess.Popen([a.launch] + ([a.args] if a.args else []))
        time.sleep(a.wait)
    cands = find(a.title, a.cls or a.match_class)
    if not cands:
        sys.exit(f"window not found (title={a.title!r} class={a.cls or a.match_class!r})")
    hwnd, t, c = cands[0]
    print(f"  target: [{c}] {t}")
    if a.activate:
        try:
            user32.ShowWindow(hwnd, 9); user32.SetForegroundWindow(hwnd); time.sleep(0.6)
        except Exception: pass
    capture(hwnd, a.out)

if __name__ == "__main__":
    main()
