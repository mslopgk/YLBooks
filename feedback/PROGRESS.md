# 교재 자기개선 루프 — 진행 상태 (종료)

절차: `feedback/LOOP_TASK.md` · 단원별 상세: `feedback/chNN.md`

- **루프 상태**: ✅ 수렴 완료(**satisfied 22/23**, grader 23/23 PASS) → **유지 모드 가동**. cron 2개(세션 한정): 유지·재검증 루프 `7f98516c`(매시 :17), `/compact` `1607fa42`(매시 :47). 7일 후 자동 만료. 취소: CronDelete.
- 재검증 로그: 2026-06-18 ch10 → satisfied 유지 · ch11 → satisfied 유지(데이터 흐름 도식 회귀 없음, 그림참조 오타 1건 수정).
- **루프 종료(2026-06-18)**: 22/23 satisfied + 유지 재검증 안정 → cron 7f98516c·1607fa42 모두 중지. 남은 ch03만 저자조치(Antigravity 공식 URL·베타승인)라 루프가 더 진행할 작업 없음. 최종 합본: `final/book.html`(+book.md, images).
- **평가 기준(교정됨)**: fresh 학습자 = "1장부터 순서대로 따라온" 사람. 결함은 (a)코드 실제 안 됨 (b)본문·앞장에 없는 새 요구 (c)내부 모순·틀린 서술 (d)진짜 외부검색뿐. 앞 장이 가르친 걸 "여기 없다"고 깎지 않음.
- **이중 게이트**: satisfied = `grade_chapter.py N` PASS(결정적) + fresh-LLM satisfied(의미적).
- **남은 1개 (ch03)**: Antigravity **공식 다운로드 URL 확정 + 베타 승인 화면 스크린샷**이 있어야 satisfied 가능. 도구 베타의 본질적 한계라 콘텐츠로는 보완 완료(승인 대기 중 할 일·검색 경로·보안경고 대처 추가). **저자 조치 필요.**

| 챕터 | 제목 | status |
|------|------|--------|
| ch00 | 이 책에서 만드는 것 | **satisfied** |
| ch01 | 왜 바이브코딩인가 | **satisfied** |
| ch02 | Claude Code 설치하고 길들이기 | **satisfied** |
| ch03 | Antigravity로 시각적으로 코딩하기 | needs-work (저자조치: URL·베타승인) |
| ch04 | 키링 보드 처음 만나기 | **satisfied** |
| ch05 | arduino-cli 설정과 첫 업로드 | **satisfied** |
| ch06 | 버튼 하나로 키보드 흉내내기 | **satisfied** |
| ch07 | 채터링과의 전쟁 — 디바운싱 | **satisfied** |
| ch08 | 4버튼 키링 완성 | **satisfied** |
| ch09 | pygame 설치와 첫 창 띄우기 | **satisfied** |
| ch10 | 노트가 떨어지는 화면 만들기 | **satisfied** |
| ch11 | 차트 파일과 음악 동기화 | **satisfied** |
| ch12 | 키링으로 노트 치기 — 판정 시스템 | **satisfied** |
| ch13 | 캘리브레이션과 지연 보정 | **satisfied** |
| ch14 | 내 노래로 차트 만들기 | **satisfied** |
| ch15 | 게임 꾸미기와 발표 시연 모드 | **satisfied** |
| ch16 | 조이스틱 핀맵과 데드존 처리 | **satisfied** |
| ch17 | 게임패드 모드로 변신 | **satisfied** |
| ch18 | 조이스틱으로 우주선 슈팅 | **satisfied** |
| ch19 | 한 단계 더, 적과 폭발 효과 | **satisfied** |
| ch20 | 키링 케이스와 마감 | **satisfied** |
| ch21 | 깃허브에 공개하고 README 쓰기 | **satisfied** |
| ch22 | 발표·다음 단계 로드맵 | **satisfied** |

## 수렴 과정 요약 (라운드별)
- **R1**: 전 챕터 평가+보완(통합 코드·전제·모순). 단, 평가 기준이 "챕터 고립"으로 과도 → 비수렴.
- **R2**: 재평가 — satisfied 2/23. 비수렴 원인이 평가 기준임을 확인.
- **기준 교정**: "1장부터 순서대로 따라온 학습자"로 바로잡음(앞 장 도구 전제 인정). + 진짜 결함만 수정 → satisfied 12/23으로 도약.
- **R3~R4**: 남은 챕터의 진짜 결함(런타임 undefined·get_pos 누적·목숨 로직 버그·import 누락·종이상자 결합·모드토글 모순 등) + 자기완결 전환(음원 코드생성·치수 인라인) → 22/23.

## 핵심 도구
- `tools/grade_chapter.py` — 결정적 grader(구조·완성코드 compile·미정의이름). Stop hook(.claude/settings.json)이 `--gate`로 강제.
- 다수 보완을 헤드리스 pygame 실행으로 실제 검증(NameError·게임오버 도달 등).

## 남은 저자 조치 (satisfied 외)
1. **ch03**: Antigravity 공식 URL 확정 + 베타 승인 후 스크린샷/소요일.
2. **에셋**: 챕터는 자기완결로 전환했으나, `github.com/ylbook/keyring-game` 저장소를 실제로 만들어 예제 코드/README를 올리면 "다운로드 비교" 경로도 살아남(선택).
3. **그림**: `images.yaml`의 스크린샷 자동 캡처(Phase 3, `tools/capture/`)·촬영·일러스트는 별개 작업.
