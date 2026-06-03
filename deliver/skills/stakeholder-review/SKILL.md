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

## 정보보안 / 접근 제어 정책

이 스킬이 다루는 PRD와 Signoff 기록은 조직 내 민감 문서다. 다음 원칙을 따른다:

| 원칙 | 구체 행동 |
|---|---|
| **저장 위치 제어** | harness/signoff-record.md · harness/review-log.md는 **로컬 repo에만** 기록. 외부 서비스(Notion 등) write는 PM 명시 승인 후에만 실행. |
| **전송 전 확인 게이트** | Gmail draft 생성, Notion 페이지 write 등 모든 외부 전송 전 코멘트 전문을 PM에게 보여주고 명시적 승인 수령. 자동 발송 0. |
| **리뷰어 연락처 분리** | harness/team-map.json은 .gitignore 권장 대상. 공개 repo push 전 PM이 직접 확인해야 함. hplan은 경고만 출력, 강제 삭제 0. |
| **Confluence 연동 부재** | 사내 Confluence를 사용하는 조직은 `signoff-record.md`를 수동으로 Confluence에 업로드하거나 `stakeholder-update --mode confluence-export` 출력물을 복사하는 방식을 사용. hplan은 Confluence API를 직접 호출하지 않아 자격증명 노출 위험 없음. |
| **role-based 접근** | Git host의 branch protection / access control이 실제 권한 관리를 담당. hplan은 권한을 관리하지 않으며 기존 IAM에 위임. |

**공개 repo 사용 시 권고:**
```
# .gitignore에 추가
harness/signoff-record.md
harness/review-log.md
harness/review-request.md
harness/team-map.json
```

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
- [ ] 외부 write(Gmail/Notion) 전 확인 게이트 통과
- [ ] team-map.json이 공개 repo에 노출되지 않도록 .gitignore 여부 확인 (경고 출력)
