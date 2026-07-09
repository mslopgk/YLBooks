# -*- coding: utf-8 -*-
"""Drive the real Expo-Web rhythm game and capture actual game screens.
Uses on-screen button CLICKS (deterministic) + arrow keys for gameplay."""
import sys, time, re
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://localhost:8081"
OUT = Path(r"C:\Users\user\YLBooks\book2\images\game")
OUT.mkdir(parents=True, exist_ok=True)
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

def shot(page, name):
    page.screenshot(path=str(OUT / f"{name}.png")); print("  +", name)

def click_text(page, pat):
    try:
        page.get_by_text(re.compile(pat)).first.click(timeout=4000)
        print("  click:", pat); return True
    except Exception as e:
        print("  click FAIL:", pat, str(e)[:60]); return False

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=2)
    page = ctx.new_page()
    print("navigating…")
    page.goto(URL, wait_until="domcontentloaded", timeout=180000)
    for _ in range(90):
        try:
            if len((page.evaluate("document.body.innerText||''")).strip()) > 3: break
        except Exception: pass
        time.sleep(2)
    time.sleep(4)
    shot(page, "game_start")

    # open difficulty modal via the PLAY button
    click_text(page, "PLAY"); time.sleep(1.4); shot(page, "game_difficulty")

    # choose a difficulty (click NORMAL); many rhythm UIs confirm on tap
    if not click_text(page, "NORMAL"):
        page.mouse.click(640, 300)  # fallback center
    time.sleep(0.8)
    # some modals need an explicit start/confirm; try Enter + a center click too
    try: page.keyboard.press("Enter")
    except Exception: pass
    time.sleep(3.0); shot(page, "game_play1")
    time.sleep(2.5); shot(page, "game_play2")

    # hit some notes with arrows during play
    for k in ["ArrowLeft","ArrowDown","ArrowUp","ArrowRight","ArrowRight","ArrowDown"]:
        try: page.keyboard.press(k)
        except Exception: pass
        time.sleep(0.3)
    time.sleep(0.8); shot(page, "game_play3")

    ctx.close(); b.close()
print("done ->", OUT)
