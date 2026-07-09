#!/usr/bin/env python3
"""최종본 폴더 생성: book.md를 하나의 self-contained HTML(book.html)로 렌더 + 이미지 복사.

눈으로 확인용. admonition(아이콘 코너)·표·코드블록·이미지 폭 속성을 모두 렌더.
"""
import shutil
import sys
from pathlib import Path
import markdown

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "final"
BOOK_MD = ROOT / "book.md"
IMG_SRC = ROOT / "docs" / "images"

CSS = """
:root{--fg:#1a1a1a;--muted:#666;--line:#e3e3e3}
*{box-sizing:border-box}
body{font-family:'Malgun Gothic','Apple SD Gothic Neo','Noto Sans KR',system-ui,sans-serif;
 line-height:1.75;color:var(--fg);max-width:820px;margin:0 auto;padding:48px 24px 120px;background:#fff}
h1{font-size:2em;border-bottom:3px solid #3949ab;padding-bottom:.3em;margin-top:2.4em}
h2{font-size:1.5em;border-bottom:1px solid var(--line);padding-bottom:.2em;margin-top:2em}
h3{font-size:1.2em;margin-top:1.6em}
code{background:#f3f3f5;padding:.1em .35em;border-radius:4px;font-size:.92em}
pre{background:#1e1e2e;color:#e6e6e6;padding:14px 16px;border-radius:8px;overflow:auto;font-size:.88em;line-height:1.5}
pre code{background:none;color:inherit;padding:0}
img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:6px;display:block;margin:10px 0}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:.95em}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left}
th{background:#f5f5f7}
blockquote{border-left:4px solid #bbb;margin:12px 0;padding:6px 16px;color:#444;background:#fafafa}
blockquote strong{color:#3949ab}
hr{border:none;border-top:1px solid var(--line);margin:2.5em 0}
/* admonition (아이콘 코너) */
.admonition{border:1px solid var(--line);border-left:5px solid #607d8b;border-radius:6px;
 padding:10px 16px;margin:16px 0;background:#fafbfc}
.admonition-title{font-weight:700;margin:.2em 0 .5em}
.admonition.note{border-left-color:#42a5f5;background:#f3f9ff}
.admonition.tip{border-left-color:#26a69a;background:#f1fbf9}
.admonition.warning{border-left-color:#ffa726;background:#fff8ef}
.admonition.abstract{border-left-color:#7e57c2;background:#f7f4fc}
.admonition.question{border-left-color:#66bb6a;background:#f3fbf3}
.admonition.info{border-left-color:#29b6f6;background:#f0faff}
.admonition.example{border-left-color:#ec407a;background:#fdf2f6}
.toc{background:#f7f7f9;border:1px solid var(--line);border-radius:8px;padding:8px 24px;font-size:.92em}
"""


def main():
    if not BOOK_MD.exists():
        sys.exit("book.md 없음 — 먼저 python build_book.py")
    FINAL.mkdir(exist_ok=True)
    # 이미지 복사
    if IMG_SRC.exists():
        dst = FINAL / "images"
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(IMG_SRC, dst)
    # book.md 사본
    shutil.copy(BOOK_MD, FINAL / "book.md")

    text = BOOK_MD.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        text,
        extensions=["admonition", "tables", "fenced_code", "attr_list",
                    "toc", "sane_lists", "footnotes", "md_in_html"],
        extension_configs={"toc": {"title": "목차"}},
    )
    html = (f"<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>바이브코딩 키링 게임기 — 최종본</title><style>{CSS}</style></head>"
            f"<body>{html_body}</body></html>")
    (FINAL / "book.html").write_text(html, encoding="utf-8")

    pngs = list((FINAL / "images").rglob("*.png")) if (FINAL / "images").exists() else []
    print(f"final/ 생성 완료")
    print(f"  - final/book.html  (눈으로 확인용, {len(html):,}자)")
    print(f"  - final/book.md    (합본 마크다운)")
    print(f"  - final/images/    (캡처된 이미지 {len(pngs)}개)")


if __name__ == "__main__":
    main()
