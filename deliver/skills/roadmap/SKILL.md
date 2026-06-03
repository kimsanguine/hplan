---
name: roadmap
description: "PRD §6(Now/Next/Later) 기반 로드맵 자동 생성 + RICE 우선순위화. --mode generate(Mermaid gantt + ROADMAP.md), --mode rice(백로그 RICE 점수 계산), --mode prioritize(Now/Next/Later 재분류). Use when a PM needs to visualize the roadmap or prioritize backlog items."
argument-hint: "[--mode generate|rice|prioritize]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

## Core Goal

PRD §6와 백로그를 시각적 로드맵과 우선순위 데이터로 변환한다.

| 모드 | 입력 | 출력 |
|---|---|---|
| generate | PRD §6 | docs/ROADMAP.md (Mermaid gantt) |
| rice | 백로그 항목 | docs/rice-scores.md |
| prioritize | RICE 결과 | PRD §6 Now/Next/Later 갱신 제안 |

## Rule 5 준수 경계

| 작업 | LLM | 근거 |
|---|---|---|
| Mermaid gantt 코드 생성 | ✅ | 자연어 → 구조화 코드 변환 |
| RICE 수치 계산 | ❌ 결정론 | Reach × Impact × Confidence ÷ Effort 공식 |
| 우선순위 재분류 기준 | ❌ 결정론 | RICE 점수 임계치 lookup |

## RICE 공식 (결정론)

```
RICE = (Reach × Impact × Confidence) / Effort

Reach: 월간 영향받는 유저 수 (PM 입력)
Impact: 0.25(최소) / 0.5(낮음) / 1(중간) / 2(높음) / 3(대규모)
Confidence: 50%(낮음) / 80%(중간) / 100%(높음)
Effort: 사람-주(person-week) 단위
```

## Instructions

### mode: generate
1. harness/PRD.md §6 읽기 → Now/Next/Later 항목 파싱 (결정론 grep)
2. 각 항목의 예상 기간을 PRD 또는 backlog에서 읽기
3. Mermaid gantt 다이어그램 생성 (LLM):
   - Now = 현재~4주
   - Next = 4~12주
   - Later = 12주+
4. docs/ROADMAP.md 저장 (기존 파일 있으면 diff 기반 업데이트 제안)

### mode: rice
1. 백로그 항목 파싱 (harness/backlog.md 또는 $ARGUMENTS)
2. 각 항목에 대해 Reach/Impact/Confidence/Effort를 PM에게 물어봄 (AskUserQuestion)
3. RICE 점수 공식으로 계산 (결정론)
4. docs/rice-scores.md 저장

### mode: prioritize
1. docs/rice-scores.md 로드 → RICE 점수 기준 정렬 (결정론)
2. 임계치 기준 분류:
   - RICE > 50: Now 후보
   - RICE 20-50: Next 후보
   - RICE < 20: Later 후보
3. 현재 PRD §6 Now/Next/Later와 비교 → 불일치 항목 표시
4. PRD §6 갱신 제안 (확인 게이트 후 반영)

## Quality Gate
- [ ] RICE 계산 = 공식 그대로 (LLM 조정 0)
- [ ] gantt에 날짜 추측 0 (PRD/backlog 인용 또는 PM 입력)
- [ ] 로드맵 갱신은 확인 게이트 후에만
