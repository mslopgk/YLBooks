#!/usr/bin/env python3
"""images.yaml + 챕터 FIG 지시문 → CAPTURE_GUIDE.md(캡처 런북) 생성.

사용자가 실제 셋업(arduino-cli+키링+계정)에서 그림을 만들 수 있게, 그림을
'어떻게 만드는가'로 분류해 챕터별로 정리한다. 촬영/일러스트는 지시문 포함.
"""
import re
import sys
from pathlib import Path
import yaml

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "chapters"
YAML = ROOT / "images.yaml"
OUT = ROOT / "CAPTURE_GUIDE.md"

CAP_RE = re.compile(r"^> \*\*(?:그림|표)\s*\d+\.\d+\s*[—–-]\s*(.*?)\*\*")


def fig_instruction(fid, chapter):
    p = CH / f"ch{chapter:02d}.md"
    if not p.exists():
        return ""
    lines = p.read_text(encoding="utf-8").split("\n")
    marker = re.compile(r"^<!--\s*FIG:\s*id=" + re.escape(fid) + r"\b")
    for i, ln in enumerate(lines):
        if marker.match(ln):
            for j in range(i + 1, min(i + 6, len(lines))):
                t = lines[j].strip()
                if t.startswith("> *") and not t.startswith("> **"):
                    return t.lstrip(">").strip().strip("*").strip()
    return ""


def main():
    figs = yaml.safe_load(YAML.read_text(encoding="utf-8"))["figures"]
    # 분류
    cats = {"auto": [], "window": [], "manual_shot": [], "web": [], "photo": [], "illust": [], "etc": []}
    for f in figs:
        cap = f.get("capture") or {}
        kind, typ, st = cap.get("kind"), f.get("type"), f.get("status")
        f["_instr"] = fig_instruction(f["id"], f["chapter"])
        if typ == "촬영":
            cats["photo"].append(f)
        elif typ == "일러스트":
            cats["illust"].append(f)
        elif typ == "기타":
            cats["etc"].append(f)
        elif kind == "terminal" and st == "pending":
            cats["auto"].append(f)
        elif kind in ("window", "device-manager"):
            cats["window"].append(f)
        elif kind == "web":
            cats["web"].append(f)
        else:
            cats["manual_shot"].append(f)

    L = []
    w = L.append
    w("# 그림 캡처 런북 (CAPTURE_GUIDE)\n")
    w("`images.yaml`에서 자동 생성. 그림을 '어떻게 만드는가'로 분류했습니다. 캡처 도구: `tools/capture/capture.py`.\n")
    w("> ⚠️ 스크린샷 자동 캡처는 **포그라운드 데스크톱**에서만 동작하며, 실행 중 마우스·키보드를 건드리지 마세요.\n")
    tot = sum(len(v) for v in cats.values())
    w(f"**총 {tot}장** — 자동 {len(cats['auto'])} · 창/장치관리자 {len(cats['window'])} · 수동 스크린샷 {len(cats['manual_shot'])} · 웹 {len(cats['web'])} · 촬영 {len(cats['photo'])} · 일러스트 {len(cats['illust'])} · 기타 {len(cats['etc'])}\n")

    def by_ch(items):
        out = {}
        for f in items:
            out.setdefault(f["chapter"], []).append(f)
        return out

    w("\n---\n## A. 자동 캡처 — 실제 셋업에서 `capture.py --id <id>` (읽기 전용 명령)\n")
    w("arduino-cli·키링이 연결된 사용자 머신에서 실행하면 됩니다. 예: `python tools/capture/capture.py --id ch05-f09`\n")
    for ch, items in sorted(by_ch(cats["auto"]).items()):
        w(f"\n**{ch}장**")
        for f in items:
            cmd = (f.get("capture") or {}).get("command", "")
            done = " ✅이미 캡처됨" if f.get("status") == "captured" else ""
            w(f"- `{f['id']}` — {f['caption']} → `{cmd}`{done}")

    w("\n---\n## B. 창 / 장치 관리자 — `capture.py --id <id>` (창 자동 포커스·캡처)\n")
    w("`images.yaml`의 `capture.launch`/`window_title`을 채운 뒤 실행. 장치 관리자는 키링 연결 상태에서.\n")
    for ch, items in sorted(by_ch(cats["window"]).items()):
        w(f"\n**{ch}장**")
        for f in items:
            w(f"- `{f['id']}` ({(f.get('capture') or {}).get('kind')}) — {f['caption']}")

    w("\n---\n## C. 수동 스크린샷 — 실제 작업 중 직접 캡처\n")
    w("설치/업로드/컴파일/시리얼/게임플레이 등 시스템 변경·하드웨어·계정·실행 화면. 작업하며 PrtSc로 직접 찍으세요.\n")
    for ch, items in sorted(by_ch(cats["manual_shot"]).items()):
        w(f"\n**{ch}장**")
        for f in items:
            instr = f" — _{f['_instr']}_" if f["_instr"] else ""
            w(f"- `{f['id']}` — {f['caption']}{instr}")

    w("\n---\n## D. 웹 페이지 — 브라우저 열고 캡처(또는 Playwright)\n")
    for ch, items in sorted(by_ch(cats["web"]).items()):
        w(f"\n**{ch}장**")
        for f in items:
            url = (f.get("capture") or {}).get("url", "")
            instr = f" — _{f['_instr']}_" if f["_instr"] else ""
            w(f"- `{f['id']}` — {f['caption']} {('('+url+')') if url else ''}{instr}")

    w("\n---\n## E. 촬영 (사진 — 알바/저자)\n")
    for ch, items in sorted(by_ch(cats["photo"]).items()):
        w(f"\n**{ch}장**")
        for f in items:
            w(f"- `{f['id']}` — {f['caption']}\n  - {f['_instr']}")

    w("\n---\n## F. 일러스트 (그림 작업)\n")
    for ch, items in sorted(by_ch(cats["illust"]).items()):
        w(f"\n**{ch}장**")
        for f in items:
            w(f"- `{f['id']}` — {f['caption']}\n  - {f['_instr']}")

    if cats["etc"]:
        w("\n---\n## G. 기타 (수동 검토)\n")
        for ch, items in sorted(by_ch(cats["etc"]).items()):
            w(f"\n**{ch}장**")
            for f in items:
                w(f"- `{f['id']}` — {f['caption']} — _{f['_instr']}_")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"CAPTURE_GUIDE.md 생성: 총 {tot}장")
    for k, v in cats.items():
        print(f"  {k}: {len(v)}")


if __name__ == "__main__":
    main()
