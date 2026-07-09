# -*- coding: utf-8 -*-
"""Drive the simulated rhythm game and capture actual game screens.
Uses file:/// scheme locally for fast and deterministic screenshot generation."""
import sys, time
from pathlib import Path
# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright

HTML_PATH = Path(r"C:\Users\shain\Documents\GitHub\YLBooks\book2\tools\game_simulator.html")
URL = f"file:///{HTML_PATH.as_posix()}"
OUT = Path(r"C:\Users\shain\Documents\GitHub\YLBooks\book2\images\game")
OUT.mkdir(parents=True, exist_ok=True)

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

def shot(page, name):
    page.screenshot(path=str(OUT / f"{name}.png"))
    print("  + captured:", f"{name}.png")

with sync_playwright() as pw:
    print("Starting browser and capturing simulated screens...")
    b = pw.chromium.launch(headless=True)
    # 1920x1080 resolution viewport for premium looking images
    ctx = b.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    page = ctx.new_page()

    # 1. Game Start Screen
    page.goto(f"{URL}?mode=start", wait_until="networkidle")
    time.sleep(1.0)
    shot(page, "game_start")

    # 2. Difficulty Modal Screen
    page.goto(f"{URL}?mode=difficulty", wait_until="networkidle")
    time.sleep(1.0)
    shot(page, "game_difficulty")

    # 3. Pure Play Screen (12th lesson - no MISS text, score 0, combo 0)
    page.goto(f"{URL}?mode=play1", wait_until="networkidle")
    time.sleep(1.0)
    shot(page, "game_play1")

    # 4. Play Screen with MISS and score 0, combo 0 (13th lesson)
    page.goto(f"{URL}?mode=play2", wait_until="networkidle")
    time.sleep(1.0)
    shot(page, "game_play2")

    # 5. Play Screen with SCORE: 1000 and COMBO: 0 (14th lesson)
    page.goto(f"{URL}?mode=play3", wait_until="networkidle")
    time.sleep(1.0)
    shot(page, "game_play3")

    ctx.close()
    b.close()
print("done ->", OUT)
