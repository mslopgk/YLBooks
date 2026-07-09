#!/usr/bin/env python3
"""그림/표를 등장 순서로 재번호 + FIG 마커 삽입 + images.yaml 생성.

규약: FORMAT_SPEC.md §2, §3
- 각 챕터에서 `> **그림 N.M — ...` / `> **표 N.M — ...` 캡션을 등장 순서로 스캔
- 등장 순서대로 새 번호(1..n) 부여 (그림·표가 하나의 시퀀스 공유)
- 본문의 `그림 N.M` / `표 N.M` 참조를 동시 치환(단일 re.sub로 충돌 없음)
- 그림 타입(촬영/스크린샷/일러스트/기타)에는 FIG 마커 삽입, 표는 placeholder 유지
- 그림 타입을 모아 images.yaml 생성 (표 제외)

사용법:
    python tools/renumber_figs.py            # ch00~ch22 전부
    python tools/renumber_figs.py 1 2        # 특정 챕터만
    python tools/renumber_figs.py --dry      # 미리보기(파일 미수정)
"""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

CH_DIR = Path("chapters")
OUT_YAML = Path("images.yaml")

CAPTION_RE = re.compile(r'^> \*\*(그림|표)\s*(\d+)\.(\d+)\s*[—–-]\s*(.*?)\*\*\s*$')
FIG_MARKER_RE = re.compile(r'^<!--\s*FIG:.*-->\s*$')


def infer_type(indicator: str) -> str:
    """캡션 아래 지시문 한 줄에서 그림 종류를 추론한다."""
    s = indicator.strip().lstrip('>').strip()
    s = s.lstrip('*').strip()
    if s.startswith('촬영'):
        return '촬영'
    if s.startswith('[스크린샷') or s.startswith('스크린샷'):
        return '스크린샷'
    if s.startswith('[일러스트') or s.startswith('[도식'):
        return '일러스트'
    if s.startswith('[표'):
        return '표'
    return '기타'


def find_indicator(lines, caption_idx):
    """캡션 줄 다음의 지시문(`> *...*`) 줄을 찾아 반환."""
    for j in range(caption_idx + 1, min(caption_idx + 5, len(lines))):
        t = lines[j].strip()
        if t in ('', '>'):
            continue
        if t.startswith('>'):
            return t
        break
    return ''


def process_chapter(path: Path, dry: bool):
    chap = int(re.match(r'ch(\d+)\.md', path.name).group(1))
    raw = path.read_text(encoding='utf-8')
    # 1) 기존 FIG 마커 제거 (재실행 가능하게 정규화)
    lines = [ln for ln in raw.split('\n') if not FIG_MARKER_RE.match(ln)]

    # 2) 캡션 등장 순서 스캔 → (원접두사, old_M, 타입)
    seq = []  # (orig_prefix, old_M, type)
    for i, ln in enumerate(lines):
        m = CAPTION_RE.match(ln)
        if not m:
            continue
        prefix, cN, cM = m.group(1), int(m.group(2)), int(m.group(3))
        if cN != chap:
            print(f"  [경고] ch{chap}: 캡션이 다른 챕터 번호 참조 - {ln.strip()}")
        typ = '표' if prefix == '표' else infer_type(find_indicator(lines, i))
        seq.append((prefix, cM, typ))

    if not seq:
        return None

    # 3) 별도 시퀀스 매핑: 그림(촬영/스크린샷/일러스트/기타)과 표를 각각 1..n
    #    key=(원접두사, old_M) -> (새접두사, 새번호)  ※ 표는 그림→표로 접두사 교정
    old2new = {}
    fig_n = tbl_n = 0
    for prefix, old_M, typ in seq:
        if typ == '표':
            tbl_n += 1
            old2new[(prefix, old_M)] = ('표', tbl_n)
        else:
            fig_n += 1
            old2new[(prefix, old_M)] = ('그림', fig_n)

    # 4) 단일 re.sub로 캡션+본문 참조 동시 치환 (이 챕터의 그림/표 참조만)
    text = '\n'.join(lines)
    ref_re = re.compile(r'(그림|표)(\s*)' + str(chap) + r'\.(\d+)')

    def repl(mo):
        prefix, sp, old_M = mo.group(1), mo.group(2), int(mo.group(3))
        key = (prefix, old_M)
        if key in old2new:
            np, nn = old2new[key]
        else:
            # 접두사 불일치 폴백: 같은 old_M을 가진 항목이 유일하면 사용
            cands = [v for (p, m), v in old2new.items() if m == old_M]
            if len(cands) == 1:
                np, nn = cands[0]
            else:
                print(f"  [경고] ch{chap}: 모호/누락 참조 {mo.group(0)} - 유지")
                return mo.group(0)
        return f"{np}{sp}{chap}.{nn}"

    text = ref_re.sub(repl, text)

    # 다른 챕터 그림 참조 경고
    for mo in re.finditer(r'(그림|표)\s*(\d+)\.(\d+)', text):
        if int(mo.group(2)) != chap:
            print(f"  [참고] ch{chap}: 타 챕터 참조 유지 — {mo.group(0)}")

    # 5) 재스캔(새 번호) → FIG 마커 삽입 + manifest 수집
    lines = text.split('\n')
    out = []
    figures = []
    for i, ln in enumerate(lines):
        m = CAPTION_RE.match(ln)
        if m:
            kind, cN, cM = m.group(1), int(m.group(2)), int(m.group(3))
            typ = '표' if kind == '표' else infer_type(find_indicator(lines, i))
            if typ != '표':  # 표는 마커/이미지 제외 (마크다운 표로 처리)
                fid = f"ch{chap:02d}-f{cM:02d}"
                fpath = f"images/ch{chap:02d}/{fid}.png"
                out.append(f"<!-- FIG: id={fid} | type={typ} | file={fpath} -->")
                figures.append({
                    'id': fid, 'chapter': chap, 'type': typ,
                    'caption': m.group(4).strip().strip('"'),
                    'file': fpath,
                })
        out.append(ln)

    new_text = '\n'.join(out)
    if not dry:
        path.write_text(new_text, encoding='utf-8')

    # 리포트
    changed = {o: n for o, n in old2new.items() if o != n}
    print(f"ch{chap:02d}: 그림/표 {len(seq)}개, 그림 {len(figures)}개 마커, 재번호 {len(changed)}건 {changed if changed else ''}")
    return figures


def render_yaml(all_figs):
    out = [
        "# 그림 캡처 매니페스트 — Layout ↔ Capture 에이전트 계약서",
        "# 규약: FORMAT_SPEC.md §2",
        "# 자동 생성: tools/renumber_figs.py (직접 편집 시 capture 라우팅만 채울 것)",
        "#",
        "# status: pending | captured | manual-todo | failed",
        "# capture.kind: terminal | window | device-manager | web | manual",
        "",
        "figures:",
    ]
    cur_ch = None
    for f in all_figs:
        if f['chapter'] != cur_ch:
            cur_ch = f['chapter']
            out.append(f"  # ── {cur_ch}장 ──")
        if f['type'] == '스크린샷':
            cap = "{ kind: null }   # TODO: terminal|window|device-manager|web 라우팅"
            status = "pending"
        else:  # 촬영 / 일러스트 / 기타
            cap = "{ kind: manual }"
            status = "manual-todo"
        out.append(f"  - id: {f['id']}")
        out.append(f"    chapter: {f['chapter']}")
        out.append(f"    type: {f['type']}")
        out.append(f"    caption: \"{f['caption']}\"")
        out.append(f"    file: {f['file']}")
        out.append(f"    capture: {cap}")
        out.append(f"    status: {status}")
        out.append("")
    return '\n'.join(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry' in sys.argv
    if args:
        targets = [CH_DIR / f"ch{int(a):02d}.md" for a in args]
    else:
        targets = sorted(CH_DIR.glob("ch*.md"))

    all_figs = []
    for p in targets:
        if not p.exists():
            print(f"  [건너뜀] {p} 없음")
            continue
        figs = process_chapter(p, dry)
        if figs:
            all_figs.extend(figs)

    # images.yaml는 전체 챕터 대상일 때만 새로 씀
    if not dry and not args:
        OUT_YAML.write_text(render_yaml(all_figs), encoding='utf-8')
        from collections import Counter
        print(f"\nimages.yaml: 그림 {len(all_figs)}개")
        print("타입:", dict(Counter(f['type'] for f in all_figs)))
    elif args:
        print("\n(특정 챕터 모드 — images.yaml 갱신 생략)")


if __name__ == '__main__':
    main()
