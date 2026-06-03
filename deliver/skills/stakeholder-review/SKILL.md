---
name: stakeholder-review
description: "PRD 스테이크홀더 리뷰 프로세스 관리 — 리뷰어 배정, 코멘트 수집, Signoff 기록. --mode assign(리뷰어 배정 + 리뷰 요청 초안), --mode collect(코멘트 수집 + 버전 기록), --mode signoff(승인 상태 추적 + audit trail 생성). Use when a PM needs to manage PRD review workflow with multiple stakeholders."
argument-hint: "[--mode assign|collect|signoff] [PRD version]"
allowed-tools: ["Read", "Write", "mcp__notion__notion-create-pages", "mcp__notion__notion-update-page",
  "mcp__gmail__create_draft", "mcp__github__create_or_update_file"]
model: sonnet
---

## Core Goal

다수 이해관계자의 PRD 리뷰를 추적하고 Signoff를 audit trail로 기록한다.

| 모드 | 책임 | 출력 |
|---|---|---|
| assign | 리뷰어 배정 + 요청 초안 생성 | harness/review-request.md + Gmail draft |
| collect | 코멘트 수집 + PRD 버전 변경 기록 | harness/review-log.md |
| signoff | 승인 상태 집계 + audit trail | harness/signoff-record.md |

## harness/signoff-record.md 형식

```
# PRD Signoff Record — v{VERSION}

| 리뷰어 | 역할 | 상태 | 날짜 | 코멘트 참조 |
|---|---|---|---|---|
| 이서연 | Product | ✅ APPROVED | 2026-06-03 | review-log.md#L12 |
| 법무팀 | Legal | ⏳ PENDING | — | — |

Signoff 기준: 모든 필수 리뷰어 APPROVED → Gate 통과
```

## Instructions

### mode: assign
1. harness/PRD.md에서 §14(실패 모드), §7(Anti-goals)를 읽어 필수 리뷰어 역할을 추론 (LLM)
2. harness/team-map.json에서 리뷰어 연락처 lookup (결정론)
3. 리뷰 요청 메일 초안 생성 (LLM) → Gmail create_draft (확인 게이트 후)
4. harness/review-request.md에 리뷰어 목록 + 기한 기록

### mode: collect
1. 리뷰어로부터 받은 코멘트를 harness/review-log.md에 기록
   포맷: {날짜, 리뷰어, 변경 대상 섹션, 코멘트, 반영여부}
2. PRD 섹션 변경 시 → harness/review-log.md에 변경 이력 append
   포맷: {날짜, 변경 섹션, 변경 전→후, 변경 이유}
3. collect는 WRITE하지 않는다 — PM이 코멘트를 직접 전달하면 기록만 함

### mode: signoff
1. harness/review-log.md에서 리뷰어별 상태 집계 (결정론 grep)
2. harness/signoff-record.md 생성/업데이트
3. 모든 필수 리뷰어 APPROVED → "Signoff 완료 — Gate 진행 가능" 출력
4. PENDING 있으면 → "미완료 리뷰어 X명 — Gate 차단" 출력 (Rule 8)

## Quality Gate
- [ ] signoff-record.md에 모든 리뷰어 상태 명시
- [ ] 자동 Signoff 처리 0 (사람이 승인 확인 후 기록)
- [ ] 코멘트 요약 = 원문 기반 (생성 0)
