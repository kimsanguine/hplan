---
name: stakeholder-update
description: "PM이 이해관계자(임원/팀/외부 파트너)에게 보내는 업데이트 보고서를 자동 생성. --mode exec-summary(임원 1-pager), --mode weekly-update(팀 주간 업데이트), --mode partner-brief(외부 파트너 요약). PROGRESS.md + decision_log + sprint actual_log를 소비해 각 대상에 맞는 산문을 생성. Use when a PM needs to communicate project status to different stakeholders."
argument-hint: "[--mode exec-summary|weekly-update|partner-brief]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

## Core Goal

PM이 작성해야 하는 3종 업데이트 보고서를 자동 생성한다. 수치 집계는 결정론, 서술 생성만 LLM.

| 모드 | 대상 | 입력 | 출력 |
|---|---|---|---|
| exec-summary | 임원 | PROGRESS.md + decision_log | docs/exec-summary.md (1쪽) |
| weekly-update | 팀 | actual_log + PROGRESS.md | docs/weekly-update.md |
| partner-brief | 외부 파트너 | PRD §1-§6 + PROGRESS.md | docs/partner-brief.md |

## Rule 5 준수 경계

| 작업 | LLM | 근거 |
|---|---|---|
| 완료/진행중/블로커 수 집계 | ❌ 결정론 | actual_log grep, PROGRESS.md 파싱 |
| 보고서 산문 생성 | ✅ | Rule 5 허용: 자연어 생성 |
| 수치 수정·조정 | ❌ 금지 | 원본 데이터 인용만 |

## Trigger Gate

### Use This Skill When
- "진행 상황 임원 보고서 만들어줘" → exec-summary
- "이번 주 팀 업데이트 작성해줘" → weekly-update
- "파트너에게 진행상황 요약 보내야 해" → partner-brief

### Route to Other Skills When
- 진행 데이터 수집 → sprint --step status
- 티켓에 상태 코멘트 → ticket-bridge --mode status
- 팀원에게 직접 전달 → ask-team

## Instructions

### 공통 Step 0 — 데이터 수집 (결정론)
```bash
# 완료 태스크 수
DONE=$(grep -c "complete" .track/actual_log.jsonl 2>/dev/null || echo 0)
# 블로커 수
BLOCKED=$(grep -c "blocker" .track/actual_log.jsonl 2>/dev/null || echo 0)
# PRD §1 목표
grep -A3 "^## 1" harness/PRD.md 2>/dev/null | head -5 || echo "PRD 없음"
```

### mode: exec-summary
임원용 1페이지 요약. 포맷:
- 제품명 + 현재 단계 (1줄)
- 완료된 것 (bullet 3개 이하)
- 다음 2주 계획 (bullet 3개 이하)
- 리스크/의사결정 필요 항목 (있는 경우만)
- Gate 상태: GREEN/CONDITIONAL_GO/RED

### mode: weekly-update
팀 주간 업데이트. 포맷:
- 이번 주 완료 (actual_log 인용)
- 진행 중 (current_task 기준)
- 블로커 (실제 발생한 것만)
- 다음 주 계획 (implementation-plan 기준)

### mode: partner-brief
외부 파트너 요약. 포함 항목: 제품 목적, 현재 단계, 기대하는 것, 다음 연락 시점.
기술 세부사항 제외. 마케팅 문구 제외.

## Quality Gate
- [ ] 모든 수치 = 파일 인용 (생성 0)
- [ ] exec-summary 1쪽 이하
- [ ] partner-brief에 내부 코드명/기술 용어 미포함
