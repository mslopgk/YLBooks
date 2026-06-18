# 포맷 스펙 — 키링 책 장 템플릿 & 그림 자동화 계약서

이 문서는 두 가지를 정의합니다.

1. **장(章) 템플릿** — 모든 챕터가 공유하는 형식 (교수님 docx 포맷을 mkdocs에 맞게 적용)
2. **그림 자동화 계약** — Layout 에이전트와 Capture 에이전트가 `images.yaml`로 소통하는 규약

> 출처: 교수님 `00_CHA0_각파트별.docx`의 "형식"만 차용. 책의 **내용**은 기존 키링 게임기(5부 22장)를 유지합니다.

---

## 1. 장 템플릿

각 장은 아래 순서·형식을 따릅니다.

```markdown
# N장 제목

!!! note "이 장에서 배우는 것"
    - 배우는 것 1
    - 배우는 것 2
    - 배우는 것 3

---

## N.1 절 제목

도입 → 개념 설명 → 구체적 예시 → 직접 해보기(실습) 흐름.

<!-- FIG: id=chNN-fXX | type=스크린샷 | file=images/chNN/chNN-fXX.png -->
> **그림 N.1 — 캡션 텍스트**
>
> *[스크린샷: 캡처 지시문]*

... 본문 ...

!!! tip "💡 팁"
    흐름상 알맞은 자리에 분산 배치. 장 끝에 몰아넣지 않는다.

---

## N.마지막 — 마무리

!!! abstract "📌 핵심 요약"
    - 요점 1
    - 요점 2

!!! question "🤔 생각해보기"
    Q1. 질문?

    ✍️ ____________________________________________

    ✍️ ____________________________________________

!!! example "✏️ 연습 문제"
    1. 문제 1
    2. 문제 2

!!! info "🔎 더 찾아보기"
    본문에서 이미 설명한 개념은 빼고, **새로 확장되는 키워드만** 제시.

    - `키워드` — 한 줄 설명

> **다음 장 예고** — 다음 장에서 무엇을 하는지 한 단락.
```

### 1.1 코너(박스) 6종 → admonition 매핑

교수님 docx의 아이콘 체계를 mkdocs `admonition`으로 1:1 매핑합니다. 제목에 이모지를 포함해 docx의 색/아이콘 느낌을 살립니다.

| docx 아이콘 | 용도 | mkdocs 표기 |
|---|---|---|
| 💡 팁 | 알아두면 좋은 요령·배경 | `!!! tip "💡 팁"` |
| ⚠️ 주의 | 실수하기 쉬운 부분·안전 경고 | `!!! warning "⚠️ 주의"` |
| 📌 핵심 요약 | 장 끝 핵심 정리 | `!!! abstract "📌 핵심 요약"` |
| 🤔 생각해보기 | 스스로 점검하는 질문(+워크북 칸) | `!!! question "🤔 생각해보기"` |
| 🔎 더 찾아보기 | 추가 학습 키워드·링크 | `!!! info "🔎 더 찾아보기"` |
| ✏️ 연습 문제 | 이해도 확인 문제 | `!!! example "✏️ 연습 문제"` |
| (장 상단) | 이 장에서 배우는 것 | `!!! note "이 장에서 배우는 것"` |

> 코너는 **필요한 것만** 흐름상 알맞은 자리에 분산 배치합니다. 장 끝에 전부 몰아 나열하지 않습니다(핵심 요약·생각해보기·연습 문제·더 찾아보기·다음 장 예고만 장 끝에 모입니다).

### 1.2 워크북 칸 (독자가 책에 직접 쓰는 빈칸)

`🤔 생각해보기` 안에서 질문 뒤에 빈 줄을 제공합니다. 인쇄·PDF에서 필기선이 되도록 아래 형식을 씁니다.

```markdown
✍️ ____________________________________________

✍️ ____________________________________________
```

### 1.3 각주

어려운 용어 보충 + 출처는 mkdocs `footnotes` 확장으로 처리합니다. `용어[^1]` … 문서 하단 `[^1]: 설명/출처`.

### 1.4 분량

장당 5쪽 이상.

---

## 2. 그림 자동화 계약 (Layout ↔ Capture)

### 2.1 인라인 그림 마커 (단일 진실 공급원)

모든 그림 자리에는 **HTML 주석 마커**를 답니다. 렌더링에는 보이지 않지만 기계가 파싱할 수 있는 앵커입니다.

```markdown
<!-- FIG: id=ch02-f04 | type=스크린샷 | file=images/ch02/ch02-f04.png -->
> **그림 2.4 — node -v 버전 확인 결과**
>
> *[스크린샷: 터미널에 `node -v` 입력 후 v20.x.x 출력. 글자 크게]*
```

- `id` — 전역 유일. `chNN-fXX` 형식 (chapter zero-pad 2자리, fig seq 2자리). **캡처·치환·매니페스트의 키.**
- `type` — `촬영` / `스크린샷` / `일러스트` / `표` / `기타` 중 하나.
- `file` — 캡처 결과가 저장될 상대 경로 (`docs/` 기준).

### 2.2 `images.yaml` — Capture 에이전트가 읽는 매니페스트

Layout 에이전트가 전 챕터의 FIG 마커를 스캔해 생성합니다. 캡처에 필요한 `target`/`steps`는 본문을 어지럽히지 않도록 **여기에만** 둡니다.

```yaml
- id: ch02-f04
  chapter: 2
  type: 스크린샷
  caption: "node -v 버전 확인 결과"
  file: images/ch02/ch02-f04.png
  capture:
    kind: terminal          # terminal | window | device-manager | web | manual
    command: "node -v"      # kind=terminal일 때
    window_title: null      # kind=window일 때 (예: "장치 관리자")
    steps: []               # UIAutomation 조작 단계 (kind=window/device-manager)
    crop: window            # full | window | region:x,y,w,h
  status: pending           # pending | captured | manual-todo | failed
```

`capture.kind` 종류:

| kind | 대상 | 캡처 방법 |
|---|---|---|
| `terminal` | Claude Code 세션, `arduino-cli` 출력, 명령 결과 | Windows Terminal에서 `command` 실행 → 창 영역 캡처 |
| `window` | 로컬 앱 창 | `Start-Process` 실행 → UIAutomation 포커스·`steps` 조작 → 창 캡처 |
| `device-manager` | 장치 관리자(`devmgmt.msc`) | 실행 → 트리에서 장치 노드 펼침 → 캡처 |
| `web` | (예외, 극소수) 공개 페이지 | Playwright headed 캡처 |
| `manual` | 물리 하드웨어 사진·게임플레이·계정 화면 | 자동 불가 → 촬영 체크리스트로 분리 |

### 2.3 캡처 후 치환 규약

Capture 에이전트가 `id`로 캡처에 성공하면, 인라인 블록(`<!-- FIG ... -->` ~ 지시 블록쿼트)을 아래로 치환하고 `images.yaml`의 `status`를 `captured`로 바꿉니다.

```markdown
![그림 2.4 — node -v 버전 확인 결과](images/ch02/ch02-f04.png){ width="600" }
```

`type`이 `촬영`/`일러스트`이거나 `kind: manual`이면 **건드리지 않고** placeholder를 유지, `status: manual-todo`로 표시합니다.

### 2.4 분류 통계 출처

원본 그림 인벤토리는 `image-shots.md`(350장). 단, 도구 변경(Arduino IDE → **arduino-cli**)에 따라 해당 항목은 재작성 대상입니다. Claude Code는 유지합니다.

---

## 3. 그림 번호 표기

책 전체 일관성을 위해 **점(`.`) 표기**를 씁니다: `그림 0.1`, `그림 2.4`, `표 0.1`. (docx는 `그림 0-1` 대시였으나 기존 책이 점이므로 점으로 통일.)
