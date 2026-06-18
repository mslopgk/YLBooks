#!/usr/bin/env python3
"""스크린샷 라우팅 분류기 — images.yaml의 type=스크린샷 항목에 capture.kind를 채운다.

각 그림의 챕터 본문에서 FIG 지시문(`> *[스크린샷: ...]*`)과 캡션을 읽어
키워드 휴리스틱으로 kind(terminal/window/device-manager/web/manual)와
명령/URL을 추정한다. **시스템을 변경하지 않는다(메타데이터만 기록).**

자동 캡처(status: pending) 대상은 '읽기 전용' 터미널 명령과 장치 관리자뿐이다.
설치/업로드 등 시스템 변경 명령, 유료 로그인, 게임플레이, 하드웨어 사진은
status: manual-todo로 두어 사람이 직접 찍게 한다.

사용법:
    python tools/classify_shots.py --dry   # 분류 결과 미리보기
    python tools/classify_shots.py          # images.yaml에 반영
"""
import json
import re
import sys
from pathlib import Path

import yaml

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
YAML = ROOT / "images.yaml"
CH = ROOT / "chapters"

# 읽기 전용(자동 캡처 안전) 명령 패턴
SAFE_CMD = re.compile(
    r"^(node\s+-v|node\s+--version|npm\s+-v|npm\s+--version|"
    r"claude\s+--version|arduino-cli\s+version|arduino-cli\s+board\s+list|"
    r"arduino-cli\s+board\s+listall.*|arduino-cli\s+core\s+list|arduino-cli\s+lib\s+list|"
    r"arduino-cli\s+help|python\s+--version|py\s+--version|pip\s+list|git\s+--version|"
    r"where\s+\w+|which\s+\w+)\s*$"
)
# 시스템 변경/네트워크/대화형 → 자동 금지(수동)
UNSAFE_HINT = re.compile(r"install|irm |iex|curl |upload|compile|core\s+install|"
                         r"update-index|config\s+init|monitor|brew\s+install")

CAPTION_RE = re.compile(r'^> \*\*(?:그림|표)\s*\d+\.\d+\s*[—–-]\s*(.*?)\*\*')


def fig_instruction(fid, chapter):
    """챕터에서 FIG 마커 다음의 캡션·지시문 텍스트를 추출."""
    chp = CH / f"ch{chapter:02d}.md"
    if not chp.exists():
        return "", ""
    lines = chp.read_text(encoding="utf-8").split("\n")
    marker = re.compile(r"^<!--\s*FIG:\s*id=" + re.escape(fid) + r"\b")
    for i, ln in enumerate(lines):
        if marker.match(ln):
            cap = ind = ""
            for j in range(i + 1, min(i + 5, len(lines))):
                t = lines[j].strip()
                if t.startswith("> **"):
                    m = CAPTION_RE.match(lines[j])
                    cap = m.group(1) if m else ""
                elif t.startswith("> *"):
                    ind = t.lstrip(">").strip().strip("*")
            return cap, ind
    return "", ""


def extract_cmd(text):
    """백틱 명령 중 첫 번째 CLI 호출을 추출."""
    for m in re.finditer(r"`([^`]+)`", text):
        c = m.group(1).strip()
        if re.match(r"^(node|npm|npx|claude|arduino-cli|winget|irm|curl|brew|"
                    r"python|py|pip|git|where|which)\b", c):
            return c
    return None


def classify(cap, ind):
    """(kind, extra, auto) 반환. extra=command/url/launch 등 dict."""
    text = f"{cap} {ind}"
    low = text.lower()

    # 장치 관리자
    if "장치 관리자" in text or "devmgmt" in low or "포트(com" in low or "포트 (com" in low:
        return "device-manager", {}, True

    # 웹 페이지
    if re.search(r"https?://|\.com|\.org|github|랜딩|페이지|사이트|브라우저|pricing|플랜 비교", text, re.I):
        url = None
        m = re.search(r"(https?://[^\s\]`]+)", text)
        if m:
            url = m.group(1)
        return "web", ({"url": url} if url else {}), False  # 웹은 기본 수동(URL 확인 필요)

    # 터미널 명령
    cmd = extract_cmd(text)
    if cmd:
        if UNSAFE_HINT.search(cmd) or UNSAFE_HINT.search(low):
            return "terminal", {"command": cmd}, False        # 시스템 변경 → 수동
        if SAFE_CMD.match(cmd):
            return "terminal", {"command": cmd}, True          # 읽기 전용 → 자동
        return "terminal", {"command": cmd}, False             # 그 외 터미널 → 수동 확인

    # 로컬 설정 창
    if re.search(r"환경\s*변수|시스템 속성|PATH 편집|제어판|joy\.cpl|설정 창|작업 관리자", text):
        return "window", {"launch": "TODO", "window_title": "TODO"}, False

    # Claude Code 세션/프롬프트(대화형) → 수동
    if "claude code" in low or "프롬프트" in text or "대화" in text or "터미널" in text:
        return "terminal", {"command": "claude"}, False

    return "manual", {}, False


def render(figs):
    out = [
        "# 그림 캡처 매니페스트 — Layout ↔ Capture 에이전트 계약서",
        "# 규약: FORMAT_SPEC.md §2  / 라우팅: tools/classify_shots.py",
        "#",
        "# status: pending(자동 캡처 대상) | captured | manual-todo | failed",
        "# capture.kind: terminal | window | device-manager | web | manual",
        "",
        "figures:",
    ]
    cur = None
    for f in figs:
        if f["chapter"] != cur:
            cur = f["chapter"]
            out.append(f"  # ── {cur}장 ──")
        out.append(f"  - id: {f['id']}")
        out.append(f"    chapter: {f['chapter']}")
        out.append(f"    type: {f['type']}")
        out.append(f"    caption: \"{f['caption']}\"")
        out.append(f"    file: {f['file']}")
        cap = f["capture"]
        if len(cap) == 1 and "kind" in cap:
            out.append(f"    capture: {{ kind: {cap['kind']} }}")
        else:
            out.append("    capture:")
            out.append(f"      kind: {cap['kind']}")
            for k, v in cap.items():
                if k == "kind":
                    continue
                val = "null" if v is None else json.dumps(v, ensure_ascii=False)
                out.append(f"      {k}: {val}")
        out.append(f"    status: {f['status']}")
        out.append("")
    return "\n".join(out)


def main():
    dry = "--dry" in sys.argv
    data = yaml.safe_load(YAML.read_text(encoding="utf-8"))
    figs = data["figures"]
    from collections import Counter
    stats = Counter()
    auto = 0
    for f in figs:
        if f.get("type") != "스크린샷":
            continue
        if f.get("status") == "captured":
            stats["captured"] += 1
            continue
        cap, ind = fig_instruction(f["id"], f["chapter"])
        kind, extra, is_auto = classify(cap or f.get("caption", ""), ind)
        f["capture"] = {"kind": kind, **extra}
        f["status"] = "pending" if is_auto else "manual-todo"
        stats[f"{kind}/{'auto' if is_auto else 'manual'}"] += 1
        if is_auto:
            auto += 1

    print("분류 결과(스크린샷):")
    for k, v in sorted(stats.items()):
        print(f"  {k:24} {v}")
    print(f"  → 자동 캡처 대상(pending): {auto}")

    if not dry:
        YAML.write_text(render(figs), encoding="utf-8")
        print("images.yaml 갱신 완료")
    else:
        print("(dry-run: 파일 미수정)")


if __name__ == "__main__":
    main()
