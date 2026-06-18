#!/usr/bin/env python3
"""결정적 챕터 grader — LLM 판정과 별개로 '코드로' 검증하는 골든 게이트.

확률적 fresh-학습자 평가를 보완한다. 여기서 FAIL이면 LLM이 satisfied라고 해도
satisfied로 인정하지 않는다(test-gate). 환각 불가능한 결정적 규칙만 검사한다.

검사 항목:
  [STRUCT] FORMAT_SPEC 필수 요소: 이 장에서 배우는 것 / 핵심 요약 / 생각해보기 / (마지막 장 외)다음 장 예고
  [FIG]    <!-- FIG --> 마커 무결성: id 유일, 캡션 동반, images.yaml과 대조
  [CODE]   ```python``` 블록 중 '완성형'은 반드시 compile 성공(발췌/학습용 표시는 면제)

사용법:
  python tools/grade_chapter.py            # 전체, 리포트
  python tools/grade_chapter.py 5 13       # 특정 챕터
  python tools/grade_chapter.py --gate     # 하드 결함 있으면 exit 2 (Stop hook용)
"""
import ast
import builtins
import re
import sys
from pathlib import Path

BUILTINS = set(dir(builtins)) | {"__name__", "__file__"}

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "chapters"
YAML = ROOT / "images.yaml"

FIG_RE = re.compile(r"^<!--\s*FIG:\s*id=(ch\d{2}-f\d{2})\s*\|\s*type=([^|]+)\|\s*file=([^\s]+)\s*-->")
CAP_RE = re.compile(r"^> \*\*(?:그림|표)\s*\d+\.\d+")
# 발췌/학습용이라 compile 면제할 신호
FRAGMENT_HINT = re.compile(r"(컴파일하지|빌드하지|학습용|발췌|예시일 뿐|그대로 치지|일부만|개념 설명용|의사 ?코드)")


def py_blocks(text):
    """(시작줄, 코드, 직전 5줄) 리스트. ```python / ```py 블록."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        m = re.match(r"^```(python|py)\s*$", lines[i].strip())
        if m:
            start = i
            body = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            pre = "\n".join(lines[max(0, start - 5):start])
            out.append((start + 1, "\n".join(body), pre))
        i += 1
    return out


def collect_bound(tree):
    """모듈에서 바인딩되는(정의되는) 이름 전부 + star-import 여부."""
    bound, star = set(), False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            a = node.args
            for arg in a.posonlyargs + a.args + a.kwonlyargs:
                bound.add(arg.arg)
            if a.vararg:
                bound.add(a.vararg.arg)
            if a.kwarg:
                bound.add(a.kwarg.arg)
        if isinstance(node, ast.Import):
            for al in node.names:
                bound.add((al.asname or al.name).split(".")[0])
        if isinstance(node, ast.ImportFrom):
            for al in node.names:
                if al.name == "*":
                    star = True
                else:
                    bound.add(al.asname or al.name)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            bound.add(node.id)
        if isinstance(node, ast.arg):
            bound.add(node.arg)
        if isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            bound.update(node.names)
        if isinstance(node, ast.NamedExpr) and isinstance(node.target, ast.Name):
            bound.add(node.target.id)
    return bound, star


def collect_used(tree):
    return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def looks_complete(code):
    """완성형 프로그램/모듈로 보이면 True(=compile 필수)."""
    has_def_or_import = ("import " in code) or re.search(r"^\s*def \w", code, re.M) or re.search(r"^\s*class \w", code, re.M)
    full_signal = ("pygame.init()" in code or "__main__" in code or
                   ("def setup" not in code and has_def_or_import and code.count("\n") > 8))
    return bool(full_signal)


def load_yaml_ids():
    if not YAML.exists():
        return {}
    ids = {}
    cur = None
    for ln in YAML.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"\s*- id:\s*(ch\d{2}-f\d{2})", ln)
        if m:
            cur = m.group(1)
            ids[cur] = True
    return ids


def grade(chap_num, yaml_ids):
    p = CH / f"ch{chap_num:02d}.md"
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8")
    errors, warns = [], []

    # [STRUCT]
    if '!!! note "이 장에서 배우는 것"' not in text:
        errors.append("STRUCT: '이 장에서 배우는 것' note 박스 없음")
    if "📌 핵심 요약" not in text:
        errors.append("STRUCT: '핵심 요약' 박스 없음")
    if "🤔 생각해보기" not in text:
        errors.append("STRUCT: '생각해보기' 박스 없음")
    if chap_num != 22 and "다음 장 예고" not in text:
        warns.append("STRUCT: '다음 장 예고' 없음")

    # [FIG]
    lines = text.split("\n")
    seen = set()
    for i, ln in enumerate(lines):
        m = FIG_RE.match(ln)
        if not m:
            continue
        fid = m.group(1)
        if fid in seen:
            errors.append(f"FIG: 중복 id {fid}")
        seen.add(fid)
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if not CAP_RE.match(nxt):
            errors.append(f"FIG: {fid} 다음 줄에 그림/표 캡션 없음")
        if yaml_ids and fid not in yaml_ids:
            warns.append(f"FIG: {fid} images.yaml에 없음")

    # [CODE] 1차: compile + 정의 이름 수집(챕터 전체 union)
    parsed, defined, star = [], set(), False
    for lineno, code, pre in py_blocks(text):
        if not code.strip():
            continue
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            if FRAGMENT_HINT.search(pre):
                continue
            if looks_complete(code):
                errors.append(f"CODE: 완성형 python 블록 구문오류 (line ~{lineno}): {e.msg}")
            else:
                warns.append(f"CODE: python 조각 구문오류 (line ~{lineno}): {e.msg}")
            continue
        b, has_star = collect_bound(tree)
        defined |= b
        star = star or has_star
        parsed.append((lineno, code, pre, tree))

    # [CODE] 2차: 완성형 블록의 미정의 이름(런타임 NameError 클래스) — star-import 있으면 생략
    if not star:
        for lineno, code, pre, tree in parsed:
            if FRAGMENT_HINT.search(pre) or not looks_complete(code):
                continue
            undef = sorted(n for n in (collect_used(tree) - defined - BUILTINS) if not n.startswith("_"))
            if undef:
                errors.append(f"CODE: 미정의 이름 {undef[:6]} (line ~{lineno}) — 챕터 내 정의 없음(NameError)")

    return {"chapter": chap_num, "errors": errors, "warns": warns, "pass": not errors}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    gate = "--gate" in sys.argv
    nums = [int(a) for a in args] if args else list(range(0, 23))
    yaml_ids = load_yaml_ids()

    results = [r for n in nums if (r := grade(n, yaml_ids))]
    hard_fail = []
    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        line = f"ch{r['chapter']:02d}: {status}"
        if r["errors"]:
            line += "  | " + " ; ".join(r["errors"])
        if r["warns"]:
            line += f"  (warn {len(r['warns'])})"
        print(line)
        if not r["pass"]:
            hard_fail.append(r["chapter"])

    n_pass = sum(1 for r in results if r["pass"])
    print(f"\n[grade] {n_pass}/{len(results)} PASS, 하드결함 챕터: {hard_fail or '없음'}")

    if gate and hard_fail:
        print(f"GATE FAIL: 구조/코드 하드 결함 챕터 {hard_fail} — 수정 필요", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
