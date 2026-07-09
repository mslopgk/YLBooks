#!/usr/bin/env python3
"""rich로 마크다운을 터미널에서 예쁘게 렌더링.

사용법:
    python3 view_book.py                    # book.md 전체 (페이저)
    python3 view_book.py chapters/ch04.md   # 특정 파일
    python3 view_book.py --no-pager ch04    # 페이저 없이 stdout
    python3 view_book.py --ch 4             # ch04.md 단축
"""
import argparse
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown


def resolve_path(arg: str | None, ch: int | None) -> Path:
    if ch is not None:
        return Path(f"chapters/ch{ch:02d}.md")
    if arg is None:
        return Path("book.md")
    p = Path(arg)
    if p.exists():
        return p
    if not arg.endswith(".md"):
        candidate = Path(f"chapters/{arg}.md")
        if candidate.exists():
            return candidate
    raise SystemExit(f"파일을 찾을 수 없습니다: {arg}")


def main() -> None:
    parser = argparse.ArgumentParser(description="rich로 md 렌더링")
    parser.add_argument("path", nargs="?", help="md 파일 경로 (기본: book.md)")
    parser.add_argument("--ch", type=int, help="챕터 번호 (예: --ch 4 → chapters/ch04.md)")
    parser.add_argument("--no-pager", action="store_true", help="페이저 없이 한 번에 출력")
    args = parser.parse_args()

    path = resolve_path(args.path, args.ch)
    text = path.read_text(encoding="utf-8")
    md = Markdown(text, code_theme="monokai")

    console = Console()
    if args.no_pager:
        console.print(md)
    else:
        with console.pager(styles=True):
            console.print(md)


if __name__ == "__main__":
    main()
