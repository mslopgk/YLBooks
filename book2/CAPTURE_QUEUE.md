# CAPTURE_QUEUE — 그림 현황 (2026-07-09 갱신)

## ✅ 실제 캡처 완료 (docx에 임베드됨, 10종)
| 파일 | 내용 | 방법 |
|---|---|---|
| images/game/game_start·difficulty·play1·play2·play3.png | 리듬게임 시작·난이도·플레이 3컷 | 예시 게임 실제 실행(Playwright, Expo Web) |
| images/c02/c02-f01·f02·f03·f05·f06.png | Claude Code 문서·Codex·OpenCode·Node 다운로드·Expo | 헤드리스 크롬 |
| images/c03/c03_ps_open·c03_ps_help.png | 파워셸 창·첫 명령 결과 | winshot(PrintWindow, 창만) |
| images/c05/c05_node_check.png | node -v / npm -v 확인 | winshot |
| images/c06/c06_claude_version.png | claude --version | winshot |

## ⏳ 저자 촬영 필요 (자동 캡처 불가/부적합)
| id | 내용 | 이유 · 소스 |
|---|---|---|
| c02-f04 | Antigravity 공식 사이트 | 애니메이션 SPA라 헤드리스서 본문 미렌더 → 브라우저서 쿠키 동의 후 수동 |
| c03-f01 | Win+X 메뉴 | 시스템 팝업(투명·transient) — 수동 |
| c04-f01/f02 | 파일 탐색기 창·새 폴더 | **Win11 탐색기=WinUI → PrintWindow 검정**. 전체화면 캡처는 포그라운드 잠금으로 IDE 노출 위험 → 수동(개인 핀 가린 상태) |
| c05-f02 | Node 설치 마법사 각 단계 | Node 이미 설치돼 재설치 없음 → 블로그(urmaru.com/9, 11컷) 출처표기 또는 수동 |
| c06-f02 | Claude Code 첫 로그인 화면 | 계정 노출 → 계정 가린 수동 촬영 |
| 사진(manual) | 키링 실물·플레이 사진(c00-f01, c01-f03) | 실물 촬영 |
| 4마당~ 게임 단계 | 노트 낙하·판정·점수 진행 컷 | 예시 게임 재실행으로 추가 캡처 가능(자동) |

## 🛠 확보된 캡처 도구 (book2/tools/)
- `winshot.py` — **창 하나만** PrintWindow 캡처(개인정보 안전). 예: `python tools/winshot.py --out x.png --launch app.exe --title T --match-class CLS`
- `cap_terminal.py` — 실제 파워셸(conhost) 창 캡처 + 여백 자동 크롭. 터미널 샷 양산용.
- `cap_game.py`(capture_game.py) — Expo 게임 실행 후 화면 캡처(Playwright).
- (스킬) `.claude/skills/tutorial-screenshots` — web_capture/term_render/build_docx 등.

## ⚠️ 캡처 원칙 (사고 방지)
- **전체화면 캡처 금지**(이 PC엔 다른 프로젝트 창이 떠 있어 유출됨). 반드시 **창 단위 PrintWindow**(winshot) 사용.
- WinUI 앱(Win11 탐색기/설정)은 PrintWindow가 안 되니 **저자 수동**으로.
- 블루투스 설정·로그인 등 **개인정보 노출 창은 자동 캡처 제외**.
