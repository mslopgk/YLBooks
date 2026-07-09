 # ABR Delivery Plan: Semi-Automatic First, Orchestration Later

  ## Summary

  개발 순서를 반자동 제작 워크플로 검증 -> 자율 오케스트레이션 확장으로 고정한다.

  핵심 목표:

  - v1에서는 Code Agent + skills + MCP + 로컬 실행기만으로 교재 한 챕터를 안정적으로 만든다.
  - 이 단계에서 품질, 재현성, 검증 루프가 충분히 확인되면 v2에서 멀티에이전트 오케스트레이션과 장시간 자율 운용으로 확장한다.

  ## Key Changes

  ### 1. 제품 단계 재정의

  - Phase 1은 완전 자율 시스템이 아니라 반자동 교재 작성 시스템으로 정의한다.
  - 단일 Code Agent 세션이 Planner, Writer, Critic, Controller 역할을 순차 수행한다.
  - 인간은 초기 brief 제공과 최종 QA만 담당한다.

  ### 2. v1 범위 고정

  - 입력:
      - Golden Code
      - 챕터 주제
      - 대상 독자
      - 학습 목표
      - 출력 언어
  - 출력:
      - MDX 챕터 초안
      - 컴포넌트 태그 포함 본문
      - placeholder 태그
      - 로컬 검증 결과
      - 수정 피드백
  - 검증:
      - 책 전체 예제 프로젝트 기준 build/test/run
      - 실패 시 retry
      - 성공 시 Critic 점수로 비교

  ### 3. v1 성공 기준 명시

  - 최소 1개 챕터를 사람이 큰 재작성 없이 사용할 수 있어야 한다.
  - 같은 입력에서 반복 실행 시 출력 구조가 안정적이어야 한다.
  - 코드 검증과 문서 구조 검증이 재현 가능해야 한다.
  - 인간 QA에서 “실무적으로 쓸 만하다”는 판단을 받아야 한다.

  ### 4. v2 진입 조건 고정

  - 아래 조건이 충족될 때만 자율 오케스트레이션 개발로 넘어간다:
      - 챕터 생성 품질이 안정적임
      - retry 루프가 수동 개입 없이 대부분 복구 가능함
      - 점수 체계가 채택/폐기 판단에 실제로 유효함
      - MDX 산출물 계약이 고정됨
      - 장시간 실행 제어
      - 병렬 챕터/실험 처리
      - 외부 샌드박스 및 원격 실행

  ## Public Interfaces

  - ChapterBrief
      - topic, audience, golden_code, learning_objectives, language
      - build_status, test_status, run_status, error_summary
  - CritiqueResult
      - clarity, flow, structure, revision_notes

  - 코드 실패 시 retry가 실제로 수정 방향을 만들어내는지 확인
  - 성공한 챕터가 MDX 규약과 디자인 컴포넌트 규약을 지키는지 확인
  - 사람이 최종 검수했을 때 수정량이 허용 범위인지 확인
  - 동일한 워크플로를 다른 챕터에도 반복 적용할 수 있는지 확인
  - skills와 MCP는 v1에서 충분한 작업 보조 수단이다.
  - 오케스트레이션은 v1 성공 후 붙이는 확장 단계이며, 선행 구현 대상이 아니다.
  - 챕터 단위 생산과 검증이 전체 책 단위 자동화의 선행 조건이다.