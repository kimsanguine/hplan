---
name: agent-setup
description: "에이전트 환경 설정 통합 — 7요소 인스트럭션 작성(agent-instructions)과 CLAUDE.md/AGENTS.md 구성(claude-md) 통합. 에이전트 정체성·도구·제약·실패 모드 정의부터 프로젝트 메모리 파일까지 한 스킬로. Use when setting up a new agent or updating agent instructions."
argument-hint: "[agent name] [--focus instructions|claude-md|both]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

## Core Goal

두 영역을 단일 인터페이스로 통합한다:

| focus | 책임 | 출력 |
|---|---|---|
| `--focus instructions` | System Prompt + 7요소 + tool list + memory_config 완전 명세 | 즉시 배포 가능한 완전 Instruction 세트 |
| `--focus claude-md` | 프로젝트 스캔 → CLAUDE.md / AGENTS.md 생성·개선 | 프로젝트 메모리 파일 (9룰 구조 적용) |
| `--focus both` | 인스트럭션 먼저, 그 결과를 CLAUDE.md/AGENTS.md에 반영 | 통합 에이전트 환경 세팅 |

> **기본값**: `--focus both` — 새 에이전트 세팅에는 둘 다 필요하다.

---

## Trigger Gate

### Use This Skill When
- 새 에이전트 환경 전체 세팅 → `--focus both`
- 에이전트 System Prompt + 7요소만 설계 → `--focus instructions`
- 프로젝트 CLAUDE.md / AGENTS.md 생성·개선만 → `--focus claude-md`
- 기존 인스트럭션 최적화·디버깅 → `--focus instructions --level draft`
- 팀원 온보딩을 위한 프로젝트 컨텍스트 공유 → `--focus claude-md`

### Route to Other Skills When
- 컨텍스트 윈도우 예산 계획 → `deliver/prd` Section 9 (메모리 설계)
- PRD 공식 문서화 → `deliver/prd`
- 에이전트 설계 구현 전 4축 검증 → `deliver/conductor` (Spec Compliance 게이트)

### Boundary Checks
- `--focus` 미명시 → `both` 기본값 진입 + 사용자 안내
- Anti-Goals 없으면 instructions/both 모두 경고 (Anti-Goals는 에이전트 설계 필수)
- Tool 목록에 사용 조건 없으면 경고 (도구 남용 방지)
- CLAUDE.md는 **프로젝트 레벨 컨텍스트 문서**이지 에이전트 Instruction이 아님

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| `--focus` | `$ARGUMENTS` | instructions/claude-md/both 분기 |
| `--level draft\|full` | `$ARGUMENTS` (instructions focus에만 적용) | draft: PM 관점 초안, full: 완전 명세 |
| target | `$ARGUMENTS` (옵션 이후 나머지) | 에이전트명, 목적, 또는 프로젝트 경로 |
| `.claude/MEMORY.md` | 프로젝트 루트 (있을 때) | 프로젝트 컨텍스트 자동 참조 |
| `agents/*/INSTRUCTION.md` | 프로젝트 루트 (있을 때) | 기존 에이전트 인스트럭션 자동 참조 |

---

## Instructions

You are setting up the agent environment with arguments: **$ARGUMENTS**

### 공통 Step 0 — focus 파싱

```
args = parse("$ARGUMENTS")
focus = args.get("--focus", "both")   # 기본값: both
level = args.get("--level", "full")   # instructions focus 시 기본값: full
target = args remainder after options
```

focus 미명시 시:
> "--focus 미명시 — `--focus both` 기본값으로 진입합니다. 사용 가능: `--focus instructions|claude-md|both`"

---

### focus: instructions

**instructions의 역할**: System Prompt + 7요소 + tool list + memory_config 완전 명세. "신입 직원 온보딩 문서" 수준.

#### --level draft (PM 관점 프롬프트 설계)

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

#### --level full (완전 명세, 기본값)

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

---

### focus: claude-md

**claude-md의 역할**: 프로젝트 디렉토리를 스캔하여 CLAUDE.md 및 AGENTS.md를 생성·개선한다.

**Phase 1 — 프로젝트 스캔 (Scan)**

1. **기술 스택 감지**: 설정 파일 읽어 프레임워크, 언어, 의존성 파악
   - `package.json` → dependencies, devDependencies, scripts
   - `pyproject.toml` / `requirements.txt` → Python 패키지
   - `tsconfig.json` → TypeScript 설정
2. **아키텍처 분석**: 디렉토리 구조 탐색
3. **컨벤션 추론**: 실제 코드에서 패턴 추출
4. **기존 CLAUDE.md 확인**: 있으면 "개선 모드"로 전환

**Phase 2 — CLAUDE.md 생성 (Build)**

9룰 구조 적용:
```markdown
# CLAUDE.md

## 프로젝트 개요
[1~2문장]

## 기술 스택
[프레임워크, 언어, 주요 라이브러리 — 버전 포함]

## 빌드 & 실행
[실제 동작하는 명령어만]

## 코드 컨벤션
[네이밍, 디렉토리, 스타일]

## 아키텍처
[디렉토리 구조 + 데이터 흐름]

## 주의사항 (Anti-Goals)
[Claude Code가 하면 안 되는 것]
```

설계 원칙:
- 온보딩 문서 수준의 완성도 (새 팀원이 첫날 읽는 문서)
- 구체적 > 일반적 (Next.js 14 App Router vs "React 사용")
- 실행 가능한 명령어만 기록
- Anti-Goals 포함 필수
- 목표: 1,500~3,000 tokens

**Phase 3 — AGENTS.md 생성 (에이전트 프로젝트일 때)**

`agents/` 디렉토리 또는 `instructions/` 디렉토리가 있을 때:
```markdown
# AGENTS.md

## 에이전트 구조
[에이전트 목록 + 각 역할]

## 인스트럭션 7요소 표준
[프로젝트 표준 인스트럭션 패턴]

## 에이전트 간 의존성
[오케스트레이션 흐름]

## 주의사항
[에이전트 수정 시 지켜야 할 규칙]
```

---

### focus: both (기본값)

**Step 1** → `--focus instructions --level full` 실행하여 7요소 완전 명세 생성

**Step 2** → 생성된 인스트럭션 결과를 컨텍스트로 받아 `--focus claude-md` 실행

> 두 단계 순서 고정: instructions 먼저, claude-md 나중 (에이전트 정체성이 확정된 후 메모리 파일 작성).

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| --focus 미명시 | 미입력 | both 기본값 진입 + 안내 |
| Anti-Goals 추상적 | "하지 않기" 수준만 | 구체적 시나리오로 재작성 권유 |
| Tool 사용 조건 없음 | 조건 컬럼 비어있음 | 각 도구에 "사용 조건" + "사용 금지 경우" 추가 권유 |
| 프로젝트 디렉토리 비어있음 | ls 결과 empty | "프로젝트 경로 확인" + 수동 입력 모드 |
| 기술 스택 자동 감지 실패 | 설정 파일 없음 | 사용자에게 기술 스택 직접 질문 |
| 에이전트 목적 불명확 | target 1단어 이하 | "에이전트 목적이 불명확합니다" fail loud |

---

## Quality Gate

### instructions (draft)
- [ ] CRISP 5요소 중 최소 4개 명시
- [ ] Anti-Goals 최소 3개 (구체적 시나리오)
- [ ] 판단 기준 정량적 또는 구체적 예시
- [ ] 7가지 실패 패턴 모두 체크
- [ ] Why-First 원칙 적용 (주요 지시마다 "왜")

### instructions (full)
- [ ] 7요소 모두 포함 (Role/Context/Objective/Tools/Memory/Output/Failure)
- [ ] Anti-Goals 최소 3개 (구체적 시나리오)
- [ ] 각 Tool 사용 조건 + 제한 명시
- [ ] Memory 3계층 (단기/장기/절차적) 정의
- [ ] Failure Handling 4가지 이상

### claude-md
- [ ] 프로젝트 기술 스택 정확히 식별됨
- [ ] 빌드/테스트/린트 명령어가 실제 동작하는 명령어임
- [ ] Anti-Goals(주의사항) 포함
- [ ] 1,500~3,000 tokens 범위
- [ ] 에이전트 프로젝트이면 AGENTS.md도 생성됨

---

## Examples

### Good Example
**입력:** `--focus both "news-summarizer 에이전트"`

**기대 동작:**
1. instructions/full: Role(PM 정보 수집 파트너) → 7요소 완전 명세
2. claude-md: 프로젝트 스캔 → CLAUDE.md + AGENTS.md 생성

### Good Example
**입력:** `--focus instructions --level draft "아침 뉴스 요약 프롬프트 최적화"`

**기대 동작:**
1. CRISP 5요소 채우기
2. 판단 기준 테이블 (상황 → 행동)
3. Anti-Goals 3개 이상 (구체적)
4. 7가지 패턴 체크 → 최종 프롬프트

### Bad Example
**입력:** `--focus instructions "뭔가 에이전트"`

**기대 동작:** "에이전트 목적이 불명확합니다. 구체적인 에이전트명 또는 목적을 입력해주세요." fail loud

---

## Project Context (auto-loaded)

**프로젝트 메모리:**
!`cat .claude/MEMORY.md 2>/dev/null || echo "프로젝트 메모리 없음"`

**기존 에이전트 인스트럭션:**
!`ls -1 agents/*/INSTRUCTION.md 2>/dev/null || ls -1 instructions/*.md 2>/dev/null || echo "기존 인스트럭션 파일 없음"`

**기존 CLAUDE.md (개선 모드 감지용):**
!`cat CLAUDE.md 2>/dev/null || echo "CLAUDE.md 없음 — 새로 생성 모드"`

**프로젝트 구조 스냅샷:**
!`find . -maxdepth 2 -type f \( -name "package.json" -o -name "pyproject.toml" -o -name "tsconfig.json" -o -name "Dockerfile" \) 2>/dev/null | head -10 || echo "설정 파일 없음"`
