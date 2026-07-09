#!/usr/bin/env python3
"""검수에서 추가된 그림의 임시 번호(`그림 C.X`)와 중복 번호를 유니크 숫자로 정리.

재번호(renumber_figs.py)는 캡션 번호가 '숫자·유니크'여야 (접두사,번호)→새번호 매핑이
정확하다. 검수 에이전트가 쓴 리터럴 X나 우연한 중복(예: 10.10 두 번)을 임시 유니크
숫자(80+)로 바꿔 둔다. 캡션과 그 본문참조(`(그림 C.X 참조)`)는 같은 임시 번호로 짝짓는다.
이후 renumber_figs.py가 등장순 최종 번호로 다시 매긴다.
"""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CH = Path(__file__).resolve().parents[1] / "chapters"
CAP = re.compile(r"^> \*\*그림\s*(\d+)\.([0-9A-Za-z]+)\s*[—–-]")


def fix(chap):
    p = CH / f"ch{chap:02d}.md"
    lines = p.read_text(encoding="utf-8").split("\n")
    # 1) 캡션 스캔: 유니크 보장 위해 (문제 캡션 = 리터럴X 또는 중복)에 임시번호 부여
    seen = set()
    temp = 80
    fixes = []  # (line_idx, old_token 'C.M', new_token 'C.temp')
    for i, ln in enumerate(lines):
        m = CAP.match(ln)
        if not m:
            continue
        c, sub = m.group(1), m.group(2)
        key = f"{c}.{sub}"
        is_x = not sub.isdigit()
        is_dup = key in seen
        if is_x or is_dup:
            newtok = f"{c}.{temp}"
            lines[i] = ln.replace(f"그림 {key}", f"그림 {newtok}", 1)
            fixes.append((i, c, sub, temp))
            seen.add(newtok)
            temp += 1
        else:
            seen.add(key)
    # 2) 각 fix된 캡션의 본문참조(같은 'C.sub' 리터럴) 동기화: 가장 가까운(앞쪽 우선) 참조
    for (cap_i, c, sub, t) in fixes:
        if sub.isdigit():
            continue  # 중복 숫자 캡션은 본문참조가 어느 것을 가리키는지 모호 → 건드리지 않음(renumber가 처리 못하면 후속 점검)
        token = f"그림 {c}.{sub}"   # 리터럴 X 참조
        newtok = f"그림 {c}.{t}"
        # 캡션 근처(앞 8줄~뒤 2줄) 본문참조 1개를 같은 임시번호로
        for j in list(range(cap_i - 8, cap_i)) + list(range(cap_i + 1, cap_i + 3)):
            if 0 <= j < len(lines) and j != cap_i and token in lines[j] and "**그림" not in lines[j]:
                lines[j] = lines[j].replace(token, newtok, 1)
                break
    p.write_text("\n".join(lines), encoding="utf-8")
    return fixes


def main():
    total = 0
    for chap in range(0, 23):
        fixes = fix(chap)
        if fixes:
            total += len(fixes)
            print(f"ch{chap:02d}: {len(fixes)}개 임시번호 부여 " + ", ".join(f"{c}.{s}->{c}.{t}" for _, c, s, t in fixes))
    # 잔존 리터럴 X 점검
    rem = 0
    for chap in range(0, 23):
        rem += (CH / f"ch{chap:02d}.md").read_text(encoding="utf-8").count(".X")
    print(f"총 {total}개 정리. 잔존 '.X' 토큰: {rem}")


if __name__ == "__main__":
    main()
