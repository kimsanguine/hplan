---
name: agent-instructions
description: "Unified agent instruction design skill — draft (PM-perspective prompt design: CRISP framework, intent/outcome focus, 7 failure patterns) and full (complete agent spec: System Prompt + 7-element instruction set + tool list + memory_config). Default --level full. Use when designing new agents, debugging underperforming agents, or standardizing agent design across a portfolio."
argument-hint: "[--level draft|full] [agent name, purpose, or prompt to optimize]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

## Core Goal

두 레벨의 에이전트 지시 설계를 단일 인터페이스로 통합한다:

| level | 책임 | 출력 |
|---|---|---|
| `--level draft` | PM 관점 프롬프트 설계 — CRISP 프레임워크, 의도·결과 중심 | 검토 가능한 프롬프트 초안 |
| `--level full` | System Prompt + tool list + memory_config 완전 명세 | 즉시 배포 가능한 완전 Instruction 세트 |

> **기본값**: `--level full` — 대부분의 경우 완전 명세가 필요하다.

---

## Trigger Gate

### Use This Skill When
- 새 에이전트 설계 → `--level full`
- 기존 프롬프트 최적화·디버깅 → `--level draft`
- System Prompt + tool list + memory_config 완전 명세 작성 → `--level full`
- PM이 의도를 기술자에게 전달하기 전 draft 검토 → `--level draft`
- 에이전트 포트폴리오 표준화 → `--level full`

### Route to Other Skills When
- 컨텍스트 윈도우 예산 계획 → `deliver/ctx-budget`
- PRD 공식 문서화 → `deliver/prd`
- 판단 기준 구체화 → `learn/pm-engine`

### Boundary Checks
- --level 미명시 → full 기본값 진입 + 사용자 안내
- Anti-Goals 없으면 draft/full 모두 경고 (Anti-Goals는 에이전트 설계 필수)
- Tool 목록에 사용 조건 없으면 경고 (도구 남용 방지)

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| `--level` | `$ARGUMENTS` | draft/full 분기 |
| target | `$ARGUMENTS` (level 이후 나머지) | 에이전트명, 목적, 또는 최적화할 프롬프트 |
| `.claude/MEMORY.md` | 프로젝트 루트 (있을 때) | 프로젝트 컨텍스트 자동 참조 |
| `agents/*/INSTRUCTION.md` | 프로젝트 루트 (있을 때) | 기존 에이전트 인스트럭션 자동 참조 |

---

## Instructions

You are designing agent instructions with arguments: **$ARGUMENTS**

### 공통 Step 0 — level 파싱

```
args = parse("$ARGUMENTS")
level = args.get("--level", "full")   # 기본값: full
target = args remainder after --level value
```

level 미명시 시:
> "--level 미명시 — `--level full` 기본값으로 진입합니다. 사용 가능: `--level draft|full`"

---

### level: draft

**draft의 역할**: PM 관점에서 의도·결과 중심으로 프롬프트 설계. 기술적 최적화가 아닌 판단 기준 명확화.

**Step 1 — CRISP 5요소 채우기**

| 요소 | 내용 |
|---|---|
| **C** Context | 에이전트가 알아야 할 배경 (누가, 어떤 상황) |
| **R** Role | 에이전트 전문성·페르소나 |
| **I** Instruction | 구체적 행동 지시 — 무엇을, 어떻게, 순서대로 |
| **S** Scope | 포함/제외/제한 (Anti-Goals) |
| **P** Parameters | 출력 형식, 길이, 톤, 채널 |

- 최소 4요소 명시 (Scope·Parameters는 선택 아님)
- 각 지시마다 "왜(Why)" 1줄 추가 (Why-First 원칙)

**Step 2 — 판단 기준 명시화**
```
[상황 A]이면 → [행동 X]  이유: ...
[상황 B]이면 → [행동 Y]  이유: ...
판단 어려우면 → [에스컬레이션]
```

**Step 3 — Anti-Goals 추가 (최소 3개)**
- 절대 하지 말아야 할 것, 구체적 시나리오로

**Step 4 — 실패 처리 추가**
- 데이터 없음 / API 실패 / 판단 불확실 케이스

**Step 5 — 7가지 실패 패턴 체크**

| 패턴 | 확인 |
|---|---|
| 목표 모호성 | 측정 가능한 목표인가 |
| Anti-Goals 누락 | 최소 3개 명시됐는가 |
| 출력 형식 미명시 | 채널·형식·길이 있는가 |
| 컨텍스트 과부하 | 핵심 섹션만 추출했는가 |
| 판단 기준 부재 | 정량적 기준 또는 예시 있는가 |
| 실패 처리 누락 | 4가지 실패 시나리오 있는가 |
| 역할 충돌 | 상충 요구사항 없는가 (우선순위 명시) |

**Step 6 — Why-First 검토**
- 에이전트가 "왜 이 작업을 하는지"가 주요 지시마다 녹아 있는가

**Step 7 — 최종 프롬프트 출력**

---

### level: full (기본값)

**full의 역할**: System Prompt + 7요소 + tool list + memory_config 완전 명세. "신입 직원 온보딩 문서" 수준.

**Step 1 — Role 작성 (요소 1)**
- 에이전트 역할, 대상 사용자, 전문성 범위 1~3문장
- 구체적 도메인 명시 (일반 어시스턴트 X)

**Step 2 — Context 정리 (요소 2)**
- 사용자 프로필 (역할, 언어, 기술 수준)
- 실행 환경 (cron / 대화형 / 이벤트 트리거)
- 접근 가능한 데이터 소스 목록

**Step 3 — Objective 계층 설계 (요소 3)**
- Primary Goal 1개 (측정 가능)
- Secondary Goals 우선순위 순 나열
- Anti-Goals 최소 3개 (구체적 시나리오)

**Step 4 — Tools 목록 작성 (요소 4)**
```
| 도구 | 용도 | 사용 조건 | 제한 |
```
- 최소 권한 원칙: 필요한 도구만
- 비용이 큰 도구 호출 횟수 명시
- 도구별 "사용하면 안 되는 경우" 명시

**Step 5 — Memory Strategy 설계 (요소 5)**
```
단기 (컨텍스트 윈도우): 현재 세션에서만 필요한 정보
장기 (파일):            세션 간 유지해야 할 정보 + 파일 경로
절차적 (SKILL.md):      반복 판단 패턴 외부화
```
- 컨텍스트 윈도우 예산 계획
- 외부화 가능한 판단 패턴 → SKILL.md 분리 여부 판단

**Step 6 — Output Format 정의 (요소 6)**
```
채널:   [Telegram / 파일 / stdout / Notion]
형식:   [Markdown / Plain / JSON]
길이:   [최대 N줄]
언어:   [한국어 / 영어]
톤:     [간결 / 상세]
```

**Step 7 — Failure Handling 작성 (요소 7)**
```
| 실패 시나리오 | 감지 방법 | 행동 |
```
- 4가지 이상 실패 시나리오별 행동 정의
- Human-in-the-loop 개입 조건 명시

**Step 8 — 초안 검토**
- Anti-Goals 구체적 시나리오인가
- 도구 남용 방지 조건 있는가
- 출력 포맷 채널에 맞는가
- 실패 처리 완전한가

**Step 9 — 다음 권장 액션**
- `deliver/prd`로 공식 문서화 연결
- `deliver/ctx-budget`으로 토큰 예산 계획

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| --level 미명시 | 미입력 | full 기본값 진입 + 안내 |
| Anti-Goals 추상적 | "하지 않기" 수준만 | 구체적 시나리오로 재작성 권유 |
| Tool 사용 조건 없음 | 조건 컬럼 비어있음 | 각 도구에 "사용 조건" + "사용 금지 경우" 추가 권유 |
| Memory Strategy 없음 | 요소 5 누락 | `deliver/ctx-budget` 연계 권유 |
| Output Format 채널 불일치 | 예: Telegram에 테이블 | 채널 특성에 맞는 포맷 재정의 권유 |

---

## Quality Gate

### draft
- [ ] CRISP 5요소 중 최소 4개 명시
- [ ] Anti-Goals 최소 3개 (구체적 시나리오)
- [ ] 판단 기준 정량적 또는 구체적 예시
- [ ] 7가지 실패 패턴 모두 체크
- [ ] Why-First 원칙 적용 (주요 지시마다 "왜")

### full
- [ ] 7요소 모두 포함 (Role/Context/Objective/Tools/Memory/Output/Failure)
- [ ] Anti-Goals 최소 3개 (구체적 시나리오)
- [ ] 각 Tool 사용 조건 + 제한 명시
- [ ] Memory 3계층 (단기/장기/절차적) 정의
- [ ] Failure Handling 4가지 이상

---

## Examples

### Good Example
**입력:** `--level draft "아침 뉴스 요약 프롬프트 최적화"`

**기대 동작:**
1. CRISP 5요소 채우기
2. 판단 기준 테이블 (상황 → 행동)
3. Anti-Goals 3개 이상 (구체적)
4. 7가지 패턴 체크
5. Why-First 검토 → 최종 프롬프트

### Good Example
**입력:** `--level full "news-summarizer 에이전트"`

**기대 동작:**
1. Role: PM 담당자 정보 수집 파트너 (구체적 도메인)
2. Context: cron 자동 실행, 기술 수준 높음
3. Objective: Primary Goal + Anti-Goals 3개
4. Tools: web_search (조건/제한 명시), write_file 등
5. Memory: 단기/장기/절차적 3계층
6. Output: Telegram, Markdown, 최대 500자
7. Failure: 4가지 시나리오 + Human-in-the-loop 조건

### Bad Example
**입력:** `--level full "뭔가 에이전트"`

**기대 동작:** "에이전트 목적이 불명확합니다. 구체적인 에이전트명 또는 목적을 입력해주세요." fail loud

---

## Project Context (auto-loaded)

**프로젝트 메모리:**
!`cat .claude/MEMORY.md 2>/dev/null || echo "프로젝트 메모리 없음"`

**기존 에이전트 인스트럭션:**
!`ls -1 agents/*/INSTRUCTION.md 2>/dev/null || ls -1 instructions/*.md 2>/dev/null || echo "기존 인스트럭션 파일 없음"`

## Contextual Knowledge (auto-loaded)

### CRISP Framework Reference
!`cat references/crisp-framework.md 2>/dev/null || echo ""`

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`
