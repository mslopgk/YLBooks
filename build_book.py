#!/usr/bin/env python3
"""ch01~ch22를 모아 book.md 한 파일로 합치는 스크립트.

사용법:
    python3 build_book.py
    python3 build_book.py --src chapters --out book.md
"""
import argparse
import re
from pathlib import Path

BOOK_TITLE = "바이브코딩으로 만드는 내 키링 게임기"
BOOK_SUBTITLE = "AI랑 같이 펌웨어 짜고, 내가 만든 키링으로 리듬게임까지 — 22장 DIY 코딩 교재"

PARTS = [
    ("1부 — 바이브코딩 첫걸음", range(1, 4)),
    ("2부 — 키링이 살아나는 순간", range(4, 9)),
    ("3부 — 내 손으로 만드는 리듬게임", range(9, 16)),
    ("4부 — 조이스틱으로 확장", range(16, 20)),
    ("5부 — 마무리와 자랑", range(20, 23)),
    ("부록", range(23, 25)),
]

PAGE_BREAK = "\n<!-- 페이지 나눔 -->\n\n"


def chapter_title(text: str) -> str:
    m = re.search(r"^# (\d+장 .+)$", text, re.MULTILINE)
    if m:
        return m.group(1)
    m = re.search(r"^# (부록 .+)$", text, re.MULTILINE)
    return m.group(1) if m else "(제목 없음)"


def build_toc(sources: dict[int, str]) -> str:
    lines = ["## 목차", ""]
    if 0 in sources:
        lines.append(f"**{chapter_title(sources[0])}**")
        lines.append("")
    for part_name, ch_range in PARTS:
        lines.append(f"**{part_name}**")
        for ch in ch_range:
            if ch in sources:
                lines.append(f"- {chapter_title(sources[ch])}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="챕터 마크다운을 한 책으로 합칩니다.")
    parser.add_argument("--src", default="chapters", help="챕터 .md가 들어 있는 폴더 (기본: chapters)")
    parser.add_argument("--out", default="book.md", help="출력 파일 경로 (기본: book.md)")
    args = parser.parse_args()

    src_dir = Path(args.src)
    out_path = Path(args.out)

    chapters = {}
    for fp in sorted(src_dir.glob("ch*.md")):
        m = re.match(r"ch(\d+)\.md", fp.name)
        if not m:
            continue
        chapters[int(m.group(1))] = fp.read_text(encoding="utf-8")

    if not chapters:
        raise SystemExit(f"챕터 파일이 {src_dir}에 없습니다.")

    parts = [
        f"# {BOOK_TITLE}",
        "",
        f"**{BOOK_SUBTITLE}**",
        "",
        build_toc(chapters),
    ]
    for ch in sorted(chapters):
        parts.append(PAGE_BREAK)
        parts.append(chapters[ch])

    out_path.write_text("\n".join(parts), encoding="utf-8")
    total_chars = sum(len(t) for t in chapters.values())
    print(f"[OK] {len(chapters)}개 챕터 -> {out_path} ({total_chars:,}자)")


if __name__ == "__main__":
    main()
