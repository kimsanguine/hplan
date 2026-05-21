# Research Automation System — Agent PRD

**Prometheus-Atlas-Worker 멀티에이전트 아키텍처**

---

## Section 1 — Overview

```
에이전트 이름:  ResearchOS (Research Orchestration System)
버전:          0.1
작성일:        2026-03-06
작성자:        Claude (Agent PRD)
상태:          Draft

한 줄 정의:
리서치 주제를 입력받아, Prometheus가 전략을 수립하고
Atlas가 Worker 군을 조율하며 멀티소스 정보를 수집·분석해
구조화된 리포트를 자동 생성하는 멀티에이전트 시스템

배경 / 만드는 이유:
리서치는 "어디서 찾을지 결정" → "수집" → "종합" 세 단계가
서로 다른 인지 부하를 요구한다. 단일 에이전트로 처리하면
컨텍스트 낭비·품질 저하·병렬화 불가 문제가 발생한다.
역할을 Prometheus(전략) / Atlas(조율) / Worker(실행)로 분리하면
각 계층이 자신의 전문성에 집중하고, Worker는 수평 확장된다.
```

---

## Section 2 — Instruction Design (에이전트별)

### 2-A. Prometheus — 전략가

```
Role:
리서치 주제를 분석하고 전체 조사 전략을 수립하는 플래너.
무엇을 조사할지, 어떤 소스가 필요한지, 어떤 순서로 진행할지 결정한다.
Atlas에게 실행 계획(Research Plan)을 전달하고 최종 리포트를 검수한다.

Primary Goal:
리서치 주제를 실행 가능한 서브태스크 트리로 분해한다.

Secondary Goals:
1. 소스 우선순위 결정 (신뢰도·관련성·최신성 기준)
2. 최종 리포트의 품질 기준(논리 흐름, 누락 여부) 검수

Anti-Goals:
1. 직접 웹 검색하거나 데이터를 수집하지 않는다
2. 리포트 문장을 직접 작성하지 않는다 (구조 설계만)
3. Worker에게 직접 지시하지 않는다 (반드시 Atlas 경유)
```

---

### 2-B. Atlas — 조율자

```
Role:
Prometheus의 Research Plan을 받아 Worker를 스케줄링하고,
수집된 원시 데이터를 집계·정제해 합성 결과를 만드는 조율자.

Primary Goal:
Worker 실행 결과를 모아 일관된 중간 보고서(Synthesis)를 생성한다.

Secondary Goals:
1. Worker 병렬/순차 실행 스케줄 최적화
2. 중복 데이터 제거, 소스 신뢰도 가중치 적용
3. 실패한 Worker 재시도 또는 대체 전략 실행

Anti-Goals:
1. 리서치 전략(무엇을 조사할지)을 스스로 결정하지 않는다
2. 사용자에게 직접 출력하지 않는다 (Prometheus 경유)
3. Worker 결과를 임의로 버리지 않는다 (항상 로그 보존)
```

---

### 2-C. Worker — 실행자 (역할별 특화)

```
Role:
단일 수집·분석 태스크를 전문적으로 수행하는 실행 에이전트.
종류: WebSearchWorker / DocumentWorker / DataWorker / SummaryWorker

Primary Goal:
할당된 태스크 하나를 완수하고 구조화된 결과를 Atlas에 반환한다.

Secondary Goals:
1. 출처(URL, 문서명, 날짜)를 항상 포함한다
2. 신뢰도 점수(0.0~1.0)를 자체 평가해 첨부한다

Anti-Goals:
1. 태스크 범위를 스스로 확장하지 않는다
2. 다른 Worker에게 직접 지시하지 않는다
3. 부분 결과를 "완료"로 보고하지 않는다
```

---

## Section 3 — Tools & Integrations

| 에이전트 | 도구/API | 용도 | 사용 조건 | 호출 제한 |
|---|---|---|---|---|
| Prometheus | `Read` | Research Plan 템플릿 로드 | 실행 시작 시 | 1회 |
| Prometheus | `Write` | Research Plan 파일 저장 | 전략 확정 후 | 1회 |
| Atlas | `Read` | Research Plan 수신 | Worker 배분 전 | 1회 |
| Atlas | `Write` | Synthesis 중간 결과 저장 | Worker 완료마다 | N회 |
| Atlas | `Task` | Worker 에이전트 spawn | 태스크당 1회 | 최대 10개 동시 |
| WebSearchWorker | `web_search` | 웹 정보 수집 | 외부 정보 필요 시 | 최대 5회/Worker |
| DocumentWorker | `Read` | 로컬 문서 분석 | 파일 경로 지정 시 | 제한 없음 |
| DataWorker | `Bash` | 데이터 스크립트 실행 | 수치 분석 필요 시 | 명시된 경우만 |
| SummaryWorker | _(LLM only)_ | 수집 데이터 요약·분석 | Atlas 집계 후 | 1회/사이클 |
| Prometheus | `message` | 최종 리포트 전달 | 검수 완료 후 | 1회 |

**최소 권한 원칙:** Prometheus는 검색 불가, Worker는 타 Worker spawn 불가, Atlas는 외부 메시지 전송 불가.

---

## Section 4 — Memory Strategy

```
Working Memory (컨텍스트):

  Prometheus:
  - 항상 로드: research_plan_template.md, quality_rubric.md
  - 컨텍스트 예산: ~4,000 토큰

  Atlas:
  - 항상 로드: research_plan.json (Prometheus 생성)
  - 조건부 로드: synthesis_partial.json (재시작 시)
  - 컨텍스트 예산: ~8,000 토큰 (Worker 결과 집계)

  Worker:
  - 할당된 태스크 명세만 로드 (최소화)
  - 컨텍스트 예산: ~2,000 토큰/Worker

Long-term Memory (파일):

  읽기:
  - research_plan.json      → Atlas가 태스크 목록 수신
  - source_blacklist.txt    → Worker가 제외할 소스 확인
  - past_reports/{topic}/   → Prometheus가 중복 리서치 감지

  쓰기:
  - research_plan.json      → Prometheus가 전략 확정 시
  - worker_results/{id}.json → 각 Worker 완료 즉시
  - synthesis.json           → Atlas 집계 완료 시
  - final_report.md          → Prometheus 검수 완료 시

  저장 트리거:
  - Research Plan: Prometheus가 전략 확정 직후
  - Worker 결과: 각 Worker 태스크 완료 즉시 (원자적 저장)
  - Synthesis: Atlas가 모든 Worker 수신 완료 후
  - Final Report: Prometheus 검수 통과 후

Procedural Memory (Skills):
  - agent-instruction-design
  - memory-architecture
  - agent-kpi
```

---

## Section 5 — Trigger & Execution

```
트리거 유형:
☑ Manual  — 사용자가 리서치 주제 + 옵션(깊이, 소스 범위) 입력

실행 흐름:

  [Phase 1 — Prometheus: 전략 수립]
  Step 1: 주제 파싱 → 핵심 질문 3~5개 추출
  Step 2: 소스 유형 결정 (웹/문서/DB/혼합)
  Step 3: 서브태스크 트리 생성 → research_plan.json 저장
  Step 4: 품질 기준(rubric) 첨부 → Atlas에 전달

  [Phase 2 — Atlas: 수집 조율]
  Step 5: research_plan.json 파싱 → Worker 타입별 분류
  Step 6: 독립 태스크 병렬 spawn (최대 10 Worker 동시)
  Step 7: 순차 의존 태스크는 선행 Worker 완료 후 실행
  Step 8: 각 Worker 결과 수신 → synthesis.json 점진적 갱신

  [Phase 3 — Worker: 실행]
  Step 9: 단일 태스크 수행 (검색/분석/요약 중 1개)
  Step 10: 결과 + 출처 + 신뢰도 점수 구조화
  Step 11: worker_results/{id}.json 저장 → Atlas에 완료 신호

  [Phase 4 — Atlas: 합성]
  Step 12: 전체 Worker 완료 확인
  Step 13: 중복 제거, 신뢰도 가중 집계
  Step 14: 구조화된 synthesis → Prometheus에 전달

  [Phase 5 — Prometheus: 검수 & 리포트]
  Step 15: rubric 기준 검수 (누락 질문, 논리 흐름)
  Step 16: 부족 시 → Atlas에 보강 태스크 재요청 (최대 2회)
  Step 17: 최종 리포트 생성 → 사용자 전달

예상 실행 시간: 2~8분 (주제 깊이·Worker 수에 따라)
타임아웃 설정: Worker 90초 / Atlas 300초 / 전체 600초
```

---

## Section 6 — Output Specification

```
출력 채널: stdout / 파일(final_report.md) / 선택적 Telegram
출력 형식: Markdown 구조화 텍스트
출력 길이: 최대 3,000자 (Executive Summary 포함 시 +500자)
언어: 입력 언어 자동 감지 (기본 한국어)
톤: 간결·객관적, 출처 명시, 불확실성 표기

출력 예시:
---
# 리서치 리포트: 생성형 AI와 저작권 분쟁 현황

**작성일:** 2026-03-06
**신뢰도 평균:** 0.82 / 1.0
**소스 수:** 12개 (웹 8 / 문서 4)

## Executive Summary
생성형 AI 저작권 분쟁은 2025년을 기점으로 ...

## 1. 핵심 질문별 조사 결과
### Q1. 현재 주요 소송 현황은?
...
### Q2. 각국 법원의 판단 경향은?
...

## 2. 주요 출처
| # | 출처 | 신뢰도 | URL |
|---|---|---|---|
| 1 | Reuters (2025-11) | 0.91 | ... |

## 3. 불확실성 및 한계
- 2026년 1월 이후 판결은 미반영
- 일부 학술 논문 접근 제한

## 4. 후속 리서치 추천
- [ ] EU AI Act 저작권 조항 심층 분석
---
```

---

## Section 7 — Failure Handling & Success Metrics

### 실패 시나리오

| 시나리오 | 감지 방법 | 대응 행동 |
|---|---|---|
| Worker 타임아웃 | 90초 초과 응답 없음 | 1회 재시도 → 실패 시 Atlas가 대체 Worker spawn |
| 검색 결과 0건 | 빈 배열 반환 | 쿼리 재구성 후 재시도 (최대 3회) |
| 소스 신뢰도 전체 낮음 | 평균 < 0.4 | Prometheus에 경고, 리포트에 한계 명시 |
| 컨텍스트 초과 | 토큰 85%+ | Atlas가 Worker 결과 청킹 후 SummaryWorker에 선요약 위임 |
| 순환 의존 태스크 | DAG 사이클 감지 | Prometheus에 에스컬레이션, 플랜 재수립 요청 |
| 판단 불확실 (주제 모호) | Prometheus 질문 3개 이상 미해결 | Human-in-the-loop: 사용자에게 주제 구체화 요청 |
| Worker 전체 실패 (>50%) | Atlas 완료율 < 50% | 전체 중단, 부분 결과 보존 후 실패 리포트 전송 |

**Human-in-the-loop 트리거:**
- 리서치 주제가 3개 이상의 해석 가능 시 (Prometheus → 사용자 질문)
- 수집된 소스 간 심각한 사실 충돌 발생 시 (Atlas 감지 → Prometheus 에스컬레이션)
- 최종 검수 2회 후에도 핵심 질문 미해결 시

### 성공 지표

```
정확도 목표:     핵심 질문 커버율 ≥ 90%
비용 목표:       리서치 1회당 ≤ $0.15 (Haiku Worker 기준)
레이턴시 목표:   일반 주제 ≤ 3분, 심층 주제 ≤ 8분
신뢰성 목표:     완료율 ≥ 95% (부분 실패 포함 시 ≥ 99%)
품질 목표:       출처 명시율 100%, 신뢰도 평균 ≥ 0.65
```

---

## 아키텍처 요약도

```
사용자 입력 (리서치 주제)
        │
        ▼
┌─────────────────────────────────────────┐
│  PROMETHEUS (Sonnet 4.6)                │
│  - 주제 분석 & 질문 분해               │
│  - Research Plan 생성                   │
│  - 최종 리포트 검수                     │
└──────────────────┬──────────────────────┘
                   │ research_plan.json
                   ▼
┌─────────────────────────────────────────┐
│  ATLAS (Sonnet 4.6)                     │
│  - Worker 스케줄링 (병렬/순차)          │
│  - 결과 집계 & 합성                     │
│  - 실패 Worker 복구                     │
└──┬──────────┬──────────┬───────────────┘
   │          │          │
   ▼          ▼          ▼
┌──────┐  ┌──────┐  ┌──────┐  (최대 10개 동시)
│Web   │  │Doc   │  │Data  │  ...
│Search│  │Worker│  │Worker│
│Worker│  │      │  │      │
│Haiku │  │Haiku │  │Haiku │
└──────┘  └──────┘  └──────┘
   │          │          │
   └──────────┴──────────┘
              │ worker_results/*.json
              ▼
         synthesis.json
              │
              ▼
         final_report.md → 사용자
```

---

**설계 노트:**
- Worker는 **Haiku** (비용 최소화), Atlas·Prometheus는 **Sonnet** (판단 품질)
- Atlas의 DAG 스케줄러가 핵심 구현 난이도 — 순환 의존 방지 필수
- `research_plan.json`이 에이전트 간 유일한 공유 계약(Contract) — 스키마 버전 관리 권장