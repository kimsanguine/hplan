---
name: stakeholder-update
description: "PM이 이해관계자(임원/팀/외부 파트너)에게 보내는 업데이트 보고서를 자동 생성. --mode exec-summary(임원 1-pager), --mode weekly-update(팀 주간 업데이트), --mode partner-brief(외부 파트너 요약), --mode confluence-export(Confluence 업로드용 포맷 변환). PROGRESS.md + decision_log + sprint actual_log를 소비해 각 대상에 맞는 산문을 생성. Use when a PM needs to communicate project status to different stakeholders, or when a team uses Confluence as the standard documentation platform."
argument-hint: "[--mode exec-summary|weekly-update|partner-brief|confluence-export] [--source exec-summary|weekly-update|partner-brief]"
allowed-tools: ["Read", "Write", "mcp__notion__notion-create-pages", "mcp__notion__notion-fetch"]
model: sonnet
---

## Core Goal

PM이 작성해야 하는 4종 업데이트 보고서를 자동 생성한다. 수치 집계는 결정론, 서술 생성만 LLM.

| 모드 | 대상 | 입력 | 출력 |
|---|---|---|---|
| exec-summary | 임원 | PROGRESS.md + decision_log | docs/exec-summary.md (1쪽) |
| weekly-update | 팀 | actual_log + PROGRESS.md | docs/weekly-update.md |
| partner-brief | 외부 파트너 | PRD §1-§6 + PROGRESS.md | docs/partner-brief.md |
| confluence-export | Confluence 업로드 담당자 | docs/{source}.md | docs/{source}-confluence.md |

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
- "Confluence에 올릴 수 있는 형식으로 변환해줘" → confluence-export
- "사내 위키에 붙여넣을 수 있게 정리해줘" → confluence-export

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

#### Gate 상태 결정 (결정론 — LLM 0)

harness 파일에서 수치를 읽어 Gate 색상을 자동 계산한다:

```bash
# 블로커 수
BLOCKERS=$(grep -c '"event":"blocker"' .track/actual_log.jsonl 2>/dev/null || echo 0)
# 완료율
TOTAL=$(grep -c '"event":"task_start"' .track/actual_log.jsonl 2>/dev/null || echo 0)
DONE=$(grep -c '"event":"complete"' .track/actual_log.jsonl 2>/dev/null || echo 0)
COMPLETION=$([ "$TOTAL" -gt 0 ] && echo "$((DONE * 100 / TOTAL))" || echo 0)
# COGS 결과
COGS_STATUS=$(python3 -c "import json; d=json.load(open('harness/build-gate/cogs_result.json')); print(d.get('status','UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
```

**Gate 결정 규칙** (우선순위 순서, 결정론 lookup):

| 조건 | Gate |
|---|---|
| BLOCKERS ≥ 3 | 🔴 RED |
| COGS_STATUS = RED | 🔴 RED |
| BLOCKERS ≥ 1 OR COGS_STATUS = CONDITIONAL_GO OR COMPLETION < 50 | 🟡 CONDITIONAL_GO |
| COMPLETION ≥ 80 AND BLOCKERS = 0 AND COGS_STATUS = GREEN | 🟢 GREEN |
| 그 외 | 🟡 CONDITIONAL_GO |

> 데이터 파일이 없으면 "UNKNOWN — actual_log 또는 cogs_result.json 없음"으로 표시. 임의 판단 금지.
> PM이 Gate 색상을 수동으로 바꾸고 싶으면 `--gate-override RED|GREEN|CONDITIONAL_GO` 플래그 사용.

### mode: weekly-update
팀 주간 업데이트. 포맷:
- 이번 주 완료 (actual_log 인용)
- 진행 중 (current_task 기준)
- 블로커 (실제 발생한 것만)
- 다음 주 계획 (implementation-plan 기준)

### mode: partner-brief
외부 파트너 요약. 포함 항목: 제품 목적, 현재 단계, 기대하는 것, 다음 연락 시점.
기술 세부사항 제외. 마케팅 문구 제외.

### mode: confluence-export

Confluence 페이지에 붙여넣거나 업로드하기 위한 포맷 변환 모드. **Confluence API를 직접 호출하지 않는다** — 자격증명 불필요.

**사용 방법:**
1. 먼저 다른 모드로 보고서를 생성한다 (exec-summary / weekly-update / partner-brief).
2. 그 다음 `--mode confluence-export --source exec-summary` (또는 weekly-update/partner-brief)를 실행한다.

**Step 1 — 소스 파일 확인 (결정론)**
- `--source` 인자로 지정된 파일 읽기 (기본값: exec-summary → `docs/exec-summary.md`)
- `--source` 미지정 시 fail loud: "어떤 파일을 변환할지 명시하세요 (`--source exec-summary|weekly-update|partner-brief`)"

**Step 2 — Confluence 마크업으로 변환 (LLM)**

Confluence Wiki Markup 또는 Confluence Markdown 형식으로 변환:
- `##` 헤딩 → Confluence `h2.` / `h3.` 형식
- 마크다운 표 → Confluence `||` 테이블 문법
- bullet → `*` (Confluence 목록)
- 코드 블록 → `{code}...{code}` (언어 명시 가능)
- 줄바꿈 규칙: Confluence는 빈 줄 1개 = 단락 구분

**Step 3 — 출력**

`docs/{source}-confluence.md` 에 저장. 원본 파일은 변경하지 않는다.

파일 상단에 업로드 안내를 prepend한다:
```
<!-- Confluence Upload Guide
     1. Confluence 페이지 편집 모드 진입
     2. "..." 메뉴 → Insert → Markup → Confluence Wiki Markup
     3. 아래 내용을 붙여넣기
     4. 저장 후 렌더링 확인
     이 파일은 hplan stakeholder-update --mode confluence-export가 생성한 변환 산출물입니다.
     원본: docs/{source}.md
-->
```

> **정보보안 참고:** hplan은 Confluence 자격증명(API token, username)을 수집하거나 저장하지 않는다. 실제 업로드는 PM이 직접 Confluence UI에서 수행한다.

### mode: confluence-export (Notion publish)

> Confluence가 없는 환경에서 PRD를 Notion 페이지로 publish하는 대체 경로.
> Confluence MCP가 있는 환경에서는 직접 publish.

1. harness/PRD.md를 읽어 15섹션을 Notion 페이지 계층 구조로 변환 (LLM)
2. **확인 게이트**: 변환 결과 + 대상 Notion 워크스페이스를 보여주고 승인받는다
3. 승인 후 `mcp__notion__notion-create-pages`로 PRD 페이지 생성
4. 팀 공유: 생성된 Notion 페이지 URL을 `harness/prd-share-url.txt`에 기록

Confluence MCP 연결 시 (mcp__confluence__create_page 도구가 있으면):
```
allowed-tools 확인 → Confluence MCP 사용 → Confluence에 직접 publish
```

> 출력: 팀이 접근 가능한 PRD URL. 로컬 파일 의존 탈피.

## Quality Gate
- [ ] 모든 수치 = 파일 인용 (생성 0)
- [ ] exec-summary 1쪽 이하
- [ ] partner-brief에 내부 코드명/기술 용어 미포함
- [ ] confluence-export: 원본 파일 변경 0 (새 파일만 생성)
- [ ] confluence-export: 업로드 안내 주석 포함
