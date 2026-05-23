# hplan 재설계 철학 — v1.0 방향

> 작성일: 2026-05-22
> 배경: 실제 사용 후 만족도 매우 낮음. 인터뷰 강제 + 게이트 일회성 구조 → 재설계 논의.

---

## 핵심 철학 3가지

### 1. Signal Gate (인터뷰 강제 → 문서 품질로)

**기존 문제**: 인터뷰 5명 강제, 루브릭 8축 점수 → 방법론 준수가 게이트가 됨
**새 원칙**: 4개 인풋 문서 존재 여부로 판단. 인터뷰는 권장이지 강제가 아님.

| 문서 | 내용 |
|------|------|
| `pain.md` | 누가, 어떤 상황에서, 뭘 못하는가 |
| `cogs.md` | p50/p90 단위 경제성 시뮬레이션 |
| `market.md` | 시장 규모 + 진입 시점 근거 |
| `competitors.md` | 직접 경쟁사 2개 + 대체재 1개 |

4개 문서가 있으면 시작 가능. gate_guard.py는 이 4개가 없으면 PRD 작성을 차단.

---

### 2. HITL — 최소 3개 옵션 → 사람이 선택 → 기록

**기존 문제**: AI가 판단하고 사람이 override하는 구조.
**새 원칙**: AI는 옵션 생성기. 사람이 항상 결정한다.

- 모든 결정 지점에서 **최소 3개 이상 옵션** 제시
- 사람이 선택
- 선택 + 이유가 `harness/decisions.jsonl`에 기록
- 이전 결정이 다음 옵션 생성의 컨텍스트가 됨

**반응형 HITL(기존)**: 오류·신뢰도 임계값 초과 시 에스컬레이션
**선제형 HITL(신규)**: 모든 결정 지점에서 먼저 옵션 제시

---

### 3. PRD — 살아있는 Single Source of Truth

**기존 문제**: Gate 통과 후 한 번 작성하는 정적 문서.
**새 원칙**: 전 과정에 걸쳐 점진적으로 채워지는 문서.

```
PRD v0.1  ← Signal Gate 직후 (4개 문서 기반)
PRD v0.2  ← architect 결정 반영 (설계 섹션 추가)
PRD v0.3  ← operate 피드백 반영 (실사용자 신호)
PRD v0.4  ← 다음 이터레이션 ...
```

모든 버전에서 무엇을 골랐고 왜인지가 decisions.jsonl에 연결됨.

---

## 4 플러그인 구조 (유지)

```
hplan (gate)
    ↓ Signal Gate 통과
discover  →  architect  →  build  →  operate
                                        ↓
                              실사용자 피드백
                                        ↓
                              discover로 재진입 (다음 이터레이션)
```

### discover — 기회 탐색 + 피드백 재진입

진입점 A: 새 아이디어
- opportunity mapping → 3개 프레이밍 → 선택 → 기록
- assumptions → 3개 검증 방법 → 선택 → 기록
- cost sim → 3개 시나리오 → 선택 → 기록
- build-or-buy → 3개 옵션 → 선택 → 기록

진입점 B: operate에서 실사용자 피드백 유입
- 기회 재프레이밍 3개 제시 → 선택 → PRD 업데이트 버전 기록

### architect — 설계 결정 기록

- orchestration: 4개 패턴 → 선택 → 기록 (이유 포함)
- 3-tier: 3가지 tier 구성 변형 → 선택 → 기록
- memory: 3가지 메모리 전략 → 선택 → 기록
- model routing: 3가지 라우팅 전략 → 선택 → 기록
- **Architecture Doc이 PRD 섹션 7-11과 연결** (현재는 분리됨)

### build — PRD가 개발의 기준선

- PRD 각 섹션: 3개 접근법 → 선택 → 기록
- 개발 중 design과의 일관성 체크
- 각 마일스톤마다 Maker 컨펌 후 다음 진행
- HARD-GATE: Signal Gate 미통과 시 PRD/OKR/Sprint 작성 차단

### operate — 피드백 수집 + 재진입 트리거

- KPI 모니터링, 비용 리뷰 (기존 유지)
- 실사용자 피드백 유입 → 3가지 대응 옵션 → 선택 → 기록
  - A) PRD 수정 (특정 섹션 업데이트)
  - B) 재설계 (architect로 재진입)
  - C) 현행 유지 (이유 기록 후 계속)
- 선택에 따라 discover 또는 architect로 재진입

---

## Decision Log 구조 (전 과정 뼈대)

**파일**: `harness/decisions.jsonl`
**역할**: "왜 이 제품이 이렇게 생겼는가"의 완전한 답

```jsonl
{"ts": "...", "phase": "signal",    "q": "핵심 고통 프레이밍",     "options": ["A","B","C"], "chosen": "A", "why": "..."}
{"ts": "...", "phase": "discover",  "q": "Top 기회 선택",          "options": ["A","B","C"], "chosen": "B", "why": "..."}
{"ts": "...", "phase": "architect", "q": "오케스트레이션 패턴",     "options": ["Sequential","Parallel","Router"], "chosen": "Sequential", "why": "..."}
{"ts": "...", "phase": "architect", "q": "메모리 전략",             "options": ["A","B","C"], "chosen": "A", "why": "..."}
{"ts": "...", "phase": "build",     "q": "스프린트 1 우선순위",     "options": ["A","B","C"], "chosen": "C", "why": "..."}
{"ts": "...", "phase": "operate",   "q": "실사용자 피드백 대응",    "options": ["PRD 수정","재설계","유지"], "chosen": "PRD 수정", "why": "..."}
{"ts": "...", "phase": "operate",   "type": "user_feedback",        "source": "...", "signal": "...", "prd_version": "v0.3"}
```

`decision_log.py`에 필요한 서브커맨드:
- `log` — 결정 추가 (기존)
- `list` — 전체 또는 phase별 조회 (신규, Codex 지적)
- `update` — 결정 수정 (기존)
- `audit` — 감사 로그 (기존)

---

## 현재 구조에서 유지할 것

| 항목 | 유지 이유 |
|------|----------|
| WHETHER 게이트 개념 | 핵심 가치. Signal Gate로 경량화만. |
| COGS 시뮬레이션 | 단위 경제성 확인은 반드시 필요 |
| 경쟁사 + 제외 레지스트리 | 킬했던 아이디어 재방문 방지 |
| gate_guard.py + hook | PRD 작성 차단 기능 유지 |
| 4 플러그인 구조 | discover → architect → build → operate |

---

## 현재 Codex 지적 3개 (즉시 수정 필요)

1. **[high] `decision_log.py list` 없음** → `list` 서브커맨드 추가
2. **[high] `--step prd` HARD-GATE 없음** → Phase 4 상단에 checkpoint 검증 추가
3. **[medium] `hplan.md`가 삭제된 커맨드 참조** → `/hplan-build --step ...` 형식으로 업데이트

---

## 구현 우선순위

```
1단계 (Codex 지적 수정)
  ├── decision_log.py에 list 서브커맨드 추가
  ├── hplan-build.md Phase 4 HARD-GATE 추가
  └── hplan.md 다음 액션 블록 업데이트

2단계 (Signal Gate)
  ├── hplan.md Evidence Gate → Signal Gate 교체
  ├── 4개 문서 체크 로직 (gate_guard.py 또는 신규 스크립트)
  └── generate_report.py 인터뷰 강제 조건 제거

3단계 (HITL 패턴)
  ├── 각 커맨드에 "3개 옵션 → 선택 → 기록" 패턴 추가
  └── decision_log.py log 호출을 각 phase에 통합

4단계 (PRD 버전 관리 + 피드백 루프)
  ├── PRD 버전 관리 구조 (v0.1, v0.2...)
  └── operate → discover 재진입 경로
```
