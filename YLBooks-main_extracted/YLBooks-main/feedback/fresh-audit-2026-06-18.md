# 프레시 학습자 전수 검증 — 2026-06-18

메모리·사전지식 없는 입문자 10명이 "1장부터 순서대로 따라온" 기준으로 전 챕터+부록을 완주 검증. 결과 요약(우선순위순).

## 판정 한눈에
| 파트 | 챕터 | 완주 | 비고 |
|------|------|------|------|
| 도입·도구 | ch00~03+부록 | 대체로 가능 | ch03 실습 arduino-cli 선행 의존 / 없는 저장소 URL |
| 펌웨어 | ch04~08 | 가능(수정점 다수) | Keyboard.h 모순·LED 묘사·프롬프트 baud 누락 |
| **리듬게임** | **ch10~13** | **막힘** | **타이머·노트모델·통합 불일치 → 게임 완성 안 됨** |
| 리듬 마감 | ch14~15 | 가능 | 도구명 Antigravity 누출 |
| 조이스틱 | ch16~17 | 가능 | ch17 `&&`가 ch05 PowerShell 경고와 모순 |
| 슈팅 | ch18~19 | ch19 막힘 | 도구명·해상도·입력(조이스틱→키보드) 단절 |
| 마감·공개 | ch20~22 | 가능 | 없는 저장소 URL 의존(STL·예제·LINKS) |

## A. 치명적 횡단 결함 (책 정체성/완성 직결)

1. **리듬게임 통합 부재 (ch10↔11↔12↔13)** — 최우선.
   - 시계 기준 충돌: ch10 `time.perf_counter()` vs ch11·12 `pygame.time.get_ticks()`. ch11이 "ch10 노트 그리기를 붙여라" 하지만 두 시계가 달라 동기화 깨짐.
   - 노트 데이터모델 3종 비호환: ch10 `Note(time_ms, y())` dataclass / ch11 `chart["notes"]` dict(키 `time`) / ch12 `Note(lane,time,hit)` 일반 클래스. 변환 단계 없음.
   - ch12가 노트를 `(lane,ms)` 튜플로 **다시 하드코딩**, ch11의 `chart.json`/`load_chart`·음악 재생을 버림. "음악+판정"을 합치는 단계가 책 어디에도 없음 → 음악 틀면 전부 즉시 자동 MISS.
   - ch13이 "12장 judge"라며 `judge(press_time, note_time)` + 창 ±45/±90 제시 → 실제 ch12는 `judge(lane,press,notes)`+튜플 반환, 창 ±50/±100. 시그니처·수치 모두 틀림.
   - 화면크기 480×640 vs 480×800, 상수명 `PERFECT_WINDOW(80)` vs `PERFECT_MS(50)` 불일치.

2. **도구명 "Antigravity" 누출 (ch14·15·19·22)** — 책 방향(Claude Code 유지)과 정면 충돌. ch00~13은 Claude Code인데 ch14(10회)·ch19(28회)·ch15(혼용)·ch22가 소개 없이 Antigravity 사용. 프롬프트 전환 때 기존 표기가 남은 것. (ch02의 무료 대안 "antigravity cli" 언급은 정당—유지)

3. **ch18→ch19 단절** — 해상도 480×640→240×320, 입력 조이스틱→키보드(화살표/스페이스). ch19가 조이스틱을 버려 "키링으로 하는 게임" 정체성·18장 결과물 승계가 깨짐.

4. **없는 저장소 `github.com/ylbook/keyring-game` (404)** — ch00/01/20/21/22가 STL·종이도면·rp2040/ble 예제·LINKS·"내려받아 비교"에 의존. 3D프린트 옵션·로드맵·커뮤니티 동선 끊김. **저자 조치(실제 레포 생성) 필요.**

## B. 새 ch03(스킬) 자체 결함
5. 3.6 실습 `/업로드`가 arduino-cli 사용하나 설치는 ch05 → "지금은 파일만 만들고 실행은 5장 이후" 안내 누락.
6. 한글 슬래시명령 `/업로드`(비ASCII) 동작 미보장 → `/upload` 권장 또는 검증.
7. `CLAUDE.local.md` 경로 불일치(3.2 표는 루트 `./`, 3.6 .gitignore는 `.claude/`).
8. ch21.4가 "3장에서 배운 `/올리기`"라 하지만 3장은 `/업로드`만 만듦(git용 명령 없음) → ch21 문구 수정 또는 ch03에 git 스킬 추가.

## C. 프롬프트 과소명세 (AI가 다른 결과 낼 위험)
9. ch06: 프롬프트에 `Serial.begin` 속도 미지정인데 본문은 9600 모니터 + `[SAFE]/[LIVE]` 특정 문자열 단정.
10. ch07: 리팩토링 프롬프트가 SAFETY_MODE 유지를 지시 안 함 → 안전 스위치 증발 가능.
11. ch08: "Keyboard.h는 코어 내장이라 설치 불필요"가 ch05/06/07(`lib install "Keyboard"`)과 모순·사실오류. D10 보조GND 새 요구가 검증 체크리스트에 없음.
12. ch10: 첫 노트가 화면 중간서 튀어나옴(하드코딩 time_ms vs NOTE_SPEED)→"위에서 떨어진다" 그림과 불일치. 조각 덮어쓰기/누적 흐름 불명확.
13. ch18: 게임오버 거리 임계값 미지정, 단계별 변수명(ship_x 등) 미고정.

## D. 설치·운영 갭
14. ch05: Linux 설치 명령 누락(ch04는 Linux 1급 취급), winget 부재 케이스 무대응, SparkFun 코어 URL 미제공.
15. ch09: Windows `python` 미설치 시 MS Store 자동실행 미설명, PowerShell 실행정책 오류가 트러블슈팅 목록에서 빠짐.
16. ch04 vs ch05: 부트로더 LED 묘사 충돌("빠르게 점멸" vs "맥박치듯"). 실제는 맥박(fade)이 정확.
17. ch17: `&&` 한 줄 묶기 단정이 ch05의 PowerShell 경고와 모순. 방법B가 "8장에서 D6·RGB LED 배선" 잘못된 back-ref.

## E. 에셋·준비물
18. 하드웨어 구입처 부재: ch00이 ch01/ch04로 미루나 둘 다 구매처 없음.
19. ch01이 Antigravity를 "필수 SW 3종"으로 선언(설치 안내 없음) — 방향상 필수 아님, 표 수정 필요.
20. 음원/폰트 에셋 외부 의존(freesound 로그인·CC0 필터), ch19 폰트 경로 미명시(ch15는 `assets/fonts/NanumGothic.ttf`).

## 보완 완료 (2026-06-18, 사용자 "전부 보완" 지시)
- **A1 리듬게임 통합**: ch10~13을 공통 규약(시계=`get_ticks()`, 단일 Note(lane/time_ms/hit)+y(), chart.json {lane,time}→load_chart, PERFECT_MS=50/GOOD_MS=100, judge(lane,press,notes))으로 재정합. ch12.7 통합 프롬프트가 load_chart+음악재생+offset+판정을 모두 포함 → "음악에 맞춰 판정되는 게임"이 한 단계로 완성됨. ch13 judge 시그니처·±50/±100 정정. ch11 PERFECT_WINDOW·perf_counter 잔재 제거.
- **A2 Antigravity→Claude Code**: ch14·15·19·22 전부 치환(도구명 0건 확인). ch02의 무료 대안 "antigravity cli"는 유지.
- **A3 ch18→19 연속성**: ch19를 480×640·조이스틱 입력으로 통일, 폰트 경로 `assets/fonts/NanumGothic.ttf` 명시.
- **A4 저장소 URL**: ch00/01/20/22의 `ylbook/keyring-game` 의존을 "준비되면 선택적으로" 완화(없는 URL 단정 제거). **실레포 생성은 여전히 저자 조치.**
- **B ch03**: arduino-cli 선행 의존 안내(파일만 만들고 실행은 5장)·한글 명령명 영문 권장·CLAUDE.local.md 경로 통일. ch21 `/올리기` 문구 정정.
- **C/D/E**: ch04 부트로더 LED(맥박)·ch05 Linux설치/winget/SparkFun URL·ch06 Serial 9600·ch07 SAFETY_MODE 유지·ch08 Keyboard.h 모순·ch09 MS Store/실행정책·ch17 `&&`/backref·ch01 SW표/로드맵/구입처 모두 수정.
- **검증**: 게이트 23/23 PASS, 빌드 코드블록 0, 횡단 정합(perf_counter·PERFECT_WINDOW·±45/90·Antigravity) 0건. `final/book.html` 재생성.
- **남은 저자 조치**: `github.com/ylbook/keyring-game` 실제 생성(STL·예제·LINKS), 그림 캡처.

## (원본) 결론
- **펌웨어·도구 파트는 사소한 수정으로 완주 가능.** 
- **리듬게임 파트(ch10~13)는 통합 설계를 손봐야 실제로 완성됨 — 가장 큰 작업.**
- 도구명 통일(Antigravity→Claude Code)·ch18/19 연속성·ch03 선행의존은 비교적 기계적 수정.
- 저장소 URL은 저자 조치(실레포 생성)라 콘텐츠로 불가.
