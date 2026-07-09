#!/usr/bin/env python3
"""스크린샷 캡처 파이프라인 — Capture 에이전트.

images.yaml을 읽어 type=스크린샷 그림을 실제 윈도우 제어로 캡처하고,
PNG를 docs/images/chNN/에 저장한 뒤 챕터 마크다운의 <!-- FIG --> placeholder를
![](경로)로 치환하고 images.yaml status를 captured로 갱신한다.

⚠️ 포그라운드 데스크톱 세션에서만 동작(백그라운드/서비스 세션은 화면 없음).
   실행 중에는 마우스·키보드를 건드리지 말 것(창 포커스/캡처 충돌).

사용법:
    python tools/capture/capture.py --id ch02-f04          # 단일 그림
    python tools/capture/capture.py --kind terminal         # 해당 kind 전부(pending)
    python tools/capture/capture.py --id ch02-f04 --keep    # 캡처 후 창 유지(디버그)
    python tools/capture/capture.py --list                  # 캡처 가능 항목만 표시
"""
import argparse
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml
import win32con
import win32gui
from PIL import ImageGrab

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]   # H:\YLBook
YAML = ROOT / "images.yaml"
DOCS = ROOT / "docs"
CH = ROOT / "chapters"
MAX_WIDTH = 760   # 마크다운 렌더 폭 상한


# ──────────────────────────── 매니페스트 ────────────────────────────
def load_figs():
    data = yaml.safe_load(YAML.read_text(encoding="utf-8"))
    return data["figures"]


def set_status(fid, status):
    """images.yaml에서 해당 id 블록의 status 줄만 교체(포맷·주석 보존)."""
    lines = YAML.read_text(encoding="utf-8").split("\n")
    in_block = False
    for i, ln in enumerate(lines):
        if re.match(r"\s*- id:\s*" + re.escape(fid) + r"\s*$", ln):
            in_block = True
            continue
        if in_block:
            if re.match(r"\s*- id:\s", ln):   # 다음 블록 시작
                break
            if re.match(r"\s*status:\s", ln):
                indent = ln[: len(ln) - len(ln.lstrip())]
                lines[i] = f"{indent}status: {status}"
                break
    YAML.write_text("\n".join(lines), encoding="utf-8")


# ──────────────────────────── 창 캡처 기본기 ────────────────────────────
def find_window_by_title(title, timeout=25):
    end = time.time() + timeout
    while time.time() < end:
        hwnd = win32gui.FindWindow(None, title)
        if hwnd:
            return hwnd
        time.sleep(0.3)
    return 0


def grab_window(hwnd, settle=0.5):
    """창을 앞으로 가져와 창 영역을 캡처해 PIL Image 반환(저장은 호출부에서)."""
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass
    time.sleep(settle)
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    return ImageGrab.grab((l, t, r, b))


def crop_terminal(im, right_ignore=30, gap_break=34, margin=20, thresh=70):
    """터미널 캡처를 '제목+명령 출력' 블록까지만 남기고 잘라 낸다.

    상단부터 훑어, 내용이 시작된 뒤 처음으로 gap_break행 이상 연속 공백이
    나오면 그 직전까지를 내용으로 보고 자른다. 창 하단에 비치는 다른 창
    (데스크톱 bleed)은 큰 검은 공백 뒤에 있으므로 자연스럽게 제외된다.
    오른쪽 스크롤바/모서리 비침은 약간 인셋해 제거한다.
    """
    g = im.convert("L")
    w, h = g.size
    px = g.load()

    def has_ink(y):
        # 좌측 12px(다른 창 비침)와 우측 스크롤바/모서리는 무시하고 중앙 본문만 검사
        for x in range(12, max(13, w - right_ignore), 2):
            if px[x, y] > thresh:
                return True
        return False

    seen, empties, bottom = False, 0, h
    for y in range(h):
        if has_ink(y):
            seen, empties = True, 0
        else:
            empties += 1
            if seen and empties >= gap_break:
                bottom = (y - empties + 1) + margin
                break
    return im.crop((8, 0, max(9, w - 8), min(h, max(bottom, 1))))


# ──────────────────────────── 핸들러 ────────────────────────────
def capture_terminal(fig, keep=False):
    """클래식 콘솔(conhost)에 명령을 실행하고 창을 캡처."""
    cmd = (fig.get("capture") or {}).get("command")
    if not cmd:
        raise ValueError(f"{fig['id']}: capture.command 없음")
    tag = "CAPSHOT_" + fig["id"].replace("-", "_")
    done = tag + "_DONE"
    rows = int((fig.get("capture") or {}).get("rows", 16))
    ps = f"""$ErrorActionPreference='Continue'
$env:Path="$env:USERPROFILE\\.local\\bin;"+$env:Path
$h=$Host.UI.RawUI
try{{$b=$h.BufferSize;$b.Width=90;$b.Height=600;$h.BufferSize=$b;$w=$h.WindowSize;$w.Width=90;$w.Height={rows};$h.WindowSize=$w}}catch{{}}
try{{$h.WindowTitle='{tag}'}}catch{{}}
Write-Host 'PS C:\\> {cmd}' -ForegroundColor DarkGray
{cmd}
Write-Host ''
try{{$h.WindowTitle='{done}'}}catch{{}}
Start-Sleep -Seconds 180
"""
    tf = Path(tempfile.gettempdir()) / f"{tag}.ps1"
    tf.write_text(ps, encoding="utf-8")
    # conhost로 강제해 제목 기반 창 검색을 안정화(Win11 기본 Windows Terminal 회피)
    proc = subprocess.Popen(
        ["conhost.exe", "powershell.exe", "-NoProfile",
         "-ExecutionPolicy", "Bypass", "-File", str(tf)]
    )
    try:
        hwnd = find_window_by_title(done)
        if not hwnd:
            raise RuntimeError(f"{fig['id']}: 터미널 창을 찾지 못함(제목 '{done}')")
        # 핸드셰이크용 제목을 깔끔한 이름으로 교체(책에 노출되지 않게)
        try:
            win32gui.SetWindowText(hwnd, "Windows PowerShell")
        except Exception:
            pass
        im = crop_terminal(grab_window(hwnd))
    finally:
        if not keep:
            try:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            except Exception:
                pass
            proc.kill()
    return im


def capture_window(fig, keep=False):
    """로컬 앱 창: capture.launch로 실행 → capture.window_title로 검색 → 캡처."""
    cap = fig.get("capture") or {}
    launch = cap.get("launch")
    wtitle = cap.get("window_title")
    if not launch or not wtitle:
        raise ValueError(f"{fig['id']}: capture.launch/window_title 필요")
    proc = subprocess.Popen(launch, shell=True)
    try:
        hwnd = find_window_by_title(wtitle)
        if not hwnd:
            raise RuntimeError(f"{fig['id']}: 창 '{wtitle}' 못 찾음")
        im = grab_window(hwnd)
    finally:
        if not keep:
            try:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            except Exception:
                pass
    return im


def capture_device_manager(fig, keep=False):
    """장치 관리자 실행 후 캡처(노드 펼침은 추후 pywinauto로 확장)."""
    subprocess.Popen(["mmc.exe", "devmgmt.msc"])
    hwnd = find_window_by_title("장치 관리자") or find_window_by_title("Device Manager")
    if not hwnd:
        raise RuntimeError(f"{fig['id']}: 장치 관리자 창 못 찾음")
    return grab_window(hwnd)


HANDLERS = {
    "terminal": capture_terminal,
    "window": capture_window,
    "device-manager": capture_device_manager,
}


# ──────────────────────────── 마크다운 치환 ────────────────────────────
def rewrite_md(fig):
    chp = CH / f"ch{fig['chapter']:02d}.md"
    lines = chp.read_text(encoding="utf-8").split("\n")
    marker = re.compile(r"^<!--\s*FIG:\s*id=" + re.escape(fig["id"]) + r"\b")
    capnum = re.compile(r"^>\s*\*\*((?:그림|표)\s*\d+\.\d+)")
    out, i, hit = [], 0, False
    while i < len(lines):
        if marker.match(lines[i]):
            hit = True
            # 캡션 번호 추출
            num = ""
            if i + 1 < len(lines):
                m = capnum.match(lines[i + 1])
                if m:
                    num = m.group(1)
            i += 1
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                i += 1
            alt = (num + " — " if num else "") + fig["caption"]
            w = min(fig.get("_w", MAX_WIDTH), MAX_WIDTH)
            out.append(f'![{alt}]({fig["file"]}){{ width="{w}" }}')
            continue
        out.append(lines[i])
        i += 1
    if hit:
        chp.write_text("\n".join(out), encoding="utf-8")
    return hit


# ──────────────────────────── 오케스트레이션 ────────────────────────────
def runnable(fig):
    cap = fig.get("capture") or {}
    return fig.get("type") == "스크린샷" and cap.get("kind") in HANDLERS


def process(fig, keep=False):
    kind = (fig.get("capture") or {}).get("kind")
    handler = HANDLERS[kind]
    im = handler(fig, keep=keep)
    out = DOCS / fig["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    fig["_w"] = min(im.size[0], MAX_WIDTH)
    rewrite_md(fig)
    set_status(fig["id"], "captured")
    print(f"  ✔ {fig['id']} ({kind}) {im.size} -> {fig['file']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id")
    ap.add_argument("--kind", choices=list(HANDLERS))
    ap.add_argument("--keep", action="store_true", help="캡처 후 창 유지(디버그)")
    ap.add_argument("--list", action="store_true", help="캡처 가능 항목만 출력")
    args = ap.parse_args()

    figs = load_figs()

    if args.list:
        from collections import Counter
        c = Counter((f.get("capture") or {}).get("kind") for f in figs if f.get("type") == "스크린샷")
        print("스크린샷 kind 분포:", dict(c))
        for f in figs:
            if runnable(f) and f.get("status") != "captured":
                print(f"  {f['id']:12} {(f['capture'] or {}).get('kind'):14} {f['caption']}")
        return

    if args.id:
        targets = [f for f in figs if f["id"] == args.id]
    elif args.kind:
        # 안전: 자동 배치는 status=pending(읽기 전용으로 분류된 것)만. 설치/업로드 등 manual-todo는 제외.
        targets = [f for f in figs if (f["capture"] or {}).get("kind") == args.kind and f.get("status") == "pending"]
    else:
        ap.error("--id 또는 --kind 또는 --list 필요")

    if not targets:
        print("대상 없음")
        return
    print(f"{len(targets)}개 캡처 시작 ...")
    for f in targets:
        try:
            process(f, keep=args.keep)
        except Exception as e:
            print(f"  �’ {f['id']} 실패: {e}")
            set_status(f["id"], "failed")


if __name__ == "__main__":
    main()
