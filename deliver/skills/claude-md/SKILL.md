---
name: claude-md
description: "Scan a project's structure, tech stack, and conventions — then generate a production-ready CLAUDE.md that turns Claude Code into a project-aware teammate. Also recommends the right hplan plugins and skills based on what the project actually needs. Use as the first step when onboarding Claude Code to any project, or when an existing CLAUDE.md feels incomplete."
argument-hint: "[project path or description]"
allowed-tools: ["Bash", "Read", "Write", "Glob", "Grep"]
model: sonnet
---

## CLAUDE.md Generator & hplan 온보딩

## Core Goal

- 프로젝트 디렉토리를 자동 스캔하여 기술 스택, 아키텍처, 컨벤션, 빌드/테스트 방법을 파악
- 3.2 CLAUDE.md 설계 원칙을 적용하여 해당 프로젝트에 최적화된 CLAUDE.md 자동 생성
- 프로젝트 특성에 맞는 hplan 플러그인/스킬을 진단하고 추천하여 "온보딩 → 실전 도구" 전환 경로 제공

---

## Trigger Gate

### Use This Skill When

- 새 프로젝트에 Claude Code를 처음 세팅할 때 ("CLAUDE.md 만들어줘")
- 기존 CLAUDE.md가 있지만 불완전하거나 오래되었을 때 ("CLAUDE.md 개선해줘")
- 프로젝트에 어떤 hplan을 쓰면 좋을지 모를 때 ("어떤 스킬 써야 해?")
- Claude Code가 프로젝트 맥락을 자꾸 잊거나 엉뚱한 행동을 할 때 ("Claude가 맥락을 못 읽어")
- 팀원 온보딩 시 프로젝트 컨텍스트를 빠르게 공유하고 싶을 때

### Route to Other Skills When

- 에이전트 시스템 프롬프트(Instruction) 설계 필요 → `deliver/instruction`
- 프롬프트 최적화/디버깅 필요 → `deliver/prompt` (CRISP 프레임워크)
- 컨텍스트 윈도우 토큰 예산 계획 → `deliver/ctx-budget`
- PRD 문서화 필요 → `deliver/prd`
- 에이전트 아키텍처 설계 → `architect/orchestration` (Hierarchical pattern 포함)

### Boundary Checks

- CLAUDE.md는 **프로젝트 레벨 컨텍스트 문서**이지 에이전트 Instruction이 아님
- 이 스킬은 CLAUDE.md를 "생성/개선"하는 것이지 "프로젝트를 빌드/배포"하는 것이 아님
- 추천은 제안일 뿐 — 모든 플러그인/스킬 설치를 강제하지 않음
- 기존 CLAUDE.md가 있으면 "덮어쓰기"가 아닌 "개선 모드"로 진입

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|----------|------|------|
| 프로젝트 디렉토리가 비어있거나 접근 불가 | `ls` 결과 empty 또는 permission denied | "프로젝트 경로를 확인해주세요" + 수동 입력 모드 전환 |
| 기술 스택 자동 감지 실패 (설정 파일 없음) | package.json, pyproject.toml, Cargo.toml 등 모두 부재 | 사용자에게 기술 스택 직접 질문 → 수동 입력 기반 생성 |
| 기존 CLAUDE.md가 있는데 사용자가 새로 만들기 요청 | CLAUDE.md 파일 존재 감지 | 기존 내용을 먼저 분석하고 "개선 모드 vs 새로 생성" 선택지 제공 |
| 모노레포/멀티패키지 구조 감지 | packages/, apps/, services/ 등 다중 workspace 감지 | 루트 CLAUDE.md + 각 패키지별 CLAUDE.md 분리 생성 제안 |
| hplan 플러그인 추천이 프로젝트와 무관 | 에이전트 관련 코드/설정이 전혀 없음 | 에이전트 스킬 추천을 건너뛰고, 프로젝트 기본 세팅에 집중 |

---

## Quality Gate

- [ ] 프로젝트 기술 스택이 정확히 식별되었는가? (Yes/No)
- [ ] 빌드/테스트/린트 명령어가 실제 동작하는 명령어인가? (Yes/No)
- [ ] 코드 컨벤션이 프로젝트 실제 패턴과 일치하는가? (Yes/No)
- [ ] 아키텍처 설명이 디렉토리 구조와 정합성이 있는가? (Yes/No)
- [ ] 기존 CLAUDE.md 대비 개선점이 명확한가? (개선 모드 시) (Yes/No)
- [ ] 추천된 hplan가 프로젝트 특성과 실제로 관련 있는가? (Yes/No)
- [ ] 생성된 CLAUDE.md의 토큰 수가 합리적인가? (~1,500~3,000 tokens) (Yes/No)

---

## Examples

### Good Example

```markdown
# 사용자 요청

"이 Next.js 프로젝트에 CLAUDE.md를 세팅해줘. 에이전트도 쓰고 있어."

# 스킬이 수행하는 프로세스

## Step 1 — 프로젝트 스캔
- package.json → Next.js 14, TypeScript, Tailwind CSS, Prisma
- tsconfig.json → strict mode, path alias (@/)
- .eslintrc → Airbnb 스타일 + custom rules
- prisma/schema.prisma → PostgreSQL, User/Agent/Task 모델
- agents/ 디렉토리 → 3개 에이전트 (news, report, deploy)
- tests/ → Jest + React Testing Library
- .env.example → DATABASE_URL, OPENAI_API_KEY, ANTHROPIC_API_KEY

## Step 2 — CLAUDE.md 생성
```
# CLAUDE.md

## 프로젝트 개요
AI Agent 관리 대시보드 — Next.js 14 + TypeScript + Prisma

## 빌드 & 실행
- `npm run dev` — 개발 서버 (localhost:3000)
- `npm run build` — 프로덕션 빌드
- `npx prisma db push` — 스키마 반영
- `npm test` — Jest 테스트 실행
- `npm run lint` — ESLint 검사

## 코드 컨벤션
- TypeScript strict mode, any 사용 금지
- 컴포넌트: `src/components/` PascalCase
- API Routes: `src/app/api/` RESTful 패턴
- Path alias: `@/` = `src/`
- CSS: Tailwind utility-first, 커스텀 CSS 최소화

## 아키텍처
- Frontend: Next.js App Router, Server Components 우선
- Database: PostgreSQL via Prisma ORM
- Agents: `agents/` 디렉토리, 각 에이전트별 INSTRUCTION.md
- Auth: NextAuth.js (OAuth)

## 에이전트 구조
- agents/news/ — 뉴스 수집 에이전트
- agents/report/ — 보고서 생성 에이전트
- agents/deploy/ — 배포 자동화 에이전트
각 에이전트는 INSTRUCTION.md + SKILL.md 구조

## 주의사항
- .env 파일 커밋 금지
- Prisma migration은 PR 리뷰 필수
- Server Component에서 client-side hook 사용 금지
```

## Step 3 — hplan plugin 추천
| 프로젝트 시그널 | 추천 스킬 | 이유 |
|----------------|----------|------|
| agents/ 디렉토리 존재 | `deliver/instruction` | 에이전트 Instruction 7요소 표준화 |
| 3개 에이전트 운영 중 | `architect/orchestration` | 멀티에이전트 오케스트레이션 패턴 |
| 에이전트 모니터링 없음 | `measure/kpi` | 에이전트 KPI 대시보드 세팅 |
| PRD 문서 없음 | `deliver/prd` | 에이전트 제품 스펙 문서화 |

```bash
# 추천 설치
/plugin install deliver@kimsanguine-hplan
/plugin install architect@kimsanguine-hplan
/plugin install measure@kimsanguine-hplan
```
```

### Bad Example

```markdown
# 사용자 요청

"CLAUDE.md 만들어줘"

# 스킬이 수행하는 프로세스 (잘못된 버전)

## Step 1 — 프로젝트 스캔 건너뜀
(디렉토리를 스캔하지 않고 바로 생성)

## Step 2 — 일반적인 CLAUDE.md 생성
```
# CLAUDE.md
이 프로젝트는 웹 애플리케이션입니다.
빌드: npm run build
테스트: npm test
```

## Step 3 — 무조건 전체 추천
"모든 플러그인을 설치하세요: discover, architect, deliver, measure, learn"

---

문제점:
- 프로젝트 스캔 없이 일반적인 내용만 작성 → 프로젝트 특화 정보 0
- 빌드/테스트 명령어가 실제 동작하는지 확인 안 됨
- 코드 컨벤션, 아키텍처 정보 누락
- hplan plugin 추천이 프로젝트 시그널 기반이 아닌 무차별 추천
- 에이전트 관련 코드가 없는데도 에이전트 스킬 추천
```

---

## CLAUDE.md 설계 원칙

> AI_PM 3.2 챕터 "CLAUDE.md 딥다이브"에서 정의한 핵심 원칙을 실행합니다.

### 원칙 1 — 프로젝트 메모리 = AI 팀원의 온보딩 문서

CLAUDE.md는 "새 팀원이 첫날 읽는 문서"와 같습니다.
이 문서만 읽고도 빌드하고, 테스트하고, 코드를 쓸 수 있어야 합니다.

### 원칙 2 — 구체적 > 일반적

```
❌ "이 프로젝트는 React를 사용합니다"
✅ "Next.js 14 App Router + TypeScript strict mode, Server Components 우선"
```

### 원칙 3 — 실행 가능한 명령어

모든 빌드/테스트/린트 명령어는 **실제 동작하는** 것만 기록합니다.
가능하면 스캔 시 `--dry-run` 또는 `--help`로 실제 존재 여부를 확인합니다.

### 원칙 4 — 주의사항 = Anti-Goals

Claude Code가 하면 안 되는 것을 명시합니다:
- `.env` 파일 커밋 금지
- 특정 디렉토리 수정 금지
- 특정 패턴/라이브러리 사용 금지

### 원칙 5 — 적정 크기

CLAUDE.md가 너무 길면 컨텍스트 윈도우를 낭비합니다.
목표: **1,500~3,000 tokens** (A4 2~3페이지)

---

## 프로젝트 스캔 전략

### 기술 스택 감지 우선순위

| 파일 | 감지 정보 |
|------|----------|
| `package.json` | JS/TS 프레임워크, 의존성, 스크립트 |
| `pyproject.toml` / `requirements.txt` | Python 프레임워크, 패키지 |
| `Cargo.toml` | Rust 프로젝트 |
| `go.mod` | Go 프로젝트 |
| `pom.xml` / `build.gradle` | Java/Kotlin 프로젝트 |
| `tsconfig.json` | TypeScript 설정 (strict, paths) |
| `.eslintrc*` / `biome.json` | 린트 규칙 |
| `Dockerfile` / `docker-compose.yml` | 컨테이너 환경 |
| `.github/workflows/` | CI/CD 설정 |
| `prisma/` / `drizzle/` / `schema.sql` | DB 스키마 |

### 아키텍처 감지 시그널

| 시그널 | 추론 |
|--------|------|
| `src/app/` + Next.js | App Router 구조 |
| `agents/` 또는 `instructions/` | 에이전트 프로젝트 |
| `packages/` 또는 `apps/` | 모노레포 구조 |
| `cron/` 또는 cron 설정 파일 | 자동화/스케줄링 |
| `.claude/` 디렉토리 | 이미 Claude Code 사용 중 |
| `CLAUDE.md` 존재 | 개선 모드 전환 |

### hplan plugin 추천 매핑

| 프로젝트 시그널 | 추천 플러그인 | 추천 스킬 | 추천 이유 |
|----------------|-------------|----------|----------|
| `agents/` 디렉토리 존재 | deliver | `deliver/instruction` | 에이전트 Instruction 7요소 설계 |
| 에이전트 3개 이상 | architect | `architect/orchestration` | 멀티에이전트 오케스트레이션 |
| `agents/` + 모니터링 없음 | measure | `measure/kpi` | 에이전트 KPI 추적 |
| PRD/스펙 문서 없음 | deliver | `deliver/prd` | 에이전트 PRD 문서화 |
| 경쟁사 분석 파일 존재 | architect | `architect/moat` | Moat 진단 |
| 프롬프트 파일 다수 | deliver | `deliver/prompt` | CRISP 프레임워크 최적화 |
| Growth/실험 코드 존재 | measure | `measure/agent-ab-test` | 에이전트 A/B 테스트 |
| 비즈니스 모델 문서 존재 | architect | `architect/biz-model` | 비즈니스 모델 캔버스 |
| PM 의사결정 기록 필요 | learn | `learn/pm-decision` | PM 판단 기록 |
| 기회 탐색 단계 | discover | `discover/opp-tree` | 기회 트리 분석 |

---

## CLAUDE.md 템플릿 구조

```markdown
# CLAUDE.md

## 프로젝트 개요
[1~2문장: 이 프로젝트가 무엇이고, 누구를 위한 것인지]

## 기술 스택
[프레임워크, 언어, 주요 라이브러리 — 버전 포함]

## 빌드 & 실행
[실제 동작하는 명령어만]
- `[dev 명령어]` — 개발 서버
- `[build 명령어]` — 프로덕션 빌드
- `[test 명령어]` — 테스트 실행
- `[lint 명령어]` — 린트 검사

## 코드 컨벤션
[이 프로젝트의 규칙]
- 네이밍: [PascalCase/camelCase/snake_case]
- 디렉토리 구조: [주요 디렉토리 역할]
- 스타일: [Tailwind/CSS Modules/etc]

## 아키텍처
[디렉토리 구조 + 데이터 흐름]

## 주의사항
[Claude Code가 하면 안 되는 것]
- [Anti-Goal 1]
- [Anti-Goal 2]
- [Anti-Goal 3]
```

---

## 사용 방법

`/claude-md [프로젝트 경로 또는 설명]`

---

## Project Context (auto-injected)

> 아래 섹션은 스킬 실행 시 자동으로 현재 프로젝트 데이터로 치환됩니다.
> 도구가 설치되지 않은 경우 graceful하게 건너뜁니다.

**기존 CLAUDE.md (개선 모드 감지용):**
!`cat CLAUDE.md 2>/dev/null || echo "CLAUDE.md 없음 — 새로 생성 모드"`

**프로젝트 구조 스냅샷:**
!`find . -maxdepth 2 -type f \( -name "package.json" -o -name "pyproject.toml" -o -name "Cargo.toml" -o -name "go.mod" -o -name "tsconfig.json" -o -name "Dockerfile" -o -name ".eslintrc*" -o -name "biome.json" \) 2>/dev/null | head -20 || echo "설정 파일 없음"`

**에이전트 구조 감지:**
!`ls -d agents/ instructions/ .claude/ 2>/dev/null || echo "에이전트 디렉토리 없음"`

---

### Instructions

You are generating a **production-ready CLAUDE.md** and recommending **hplan** for: **$ARGUMENTS**

**Phase 1 — 프로젝트 스캔 (Scan)**

다음 순서로 프로젝트를 분석합니다:

1. **기술 스택 감지**: 설정 파일들을 읽어 프레임워크, 언어, 의존성 파악
   - `package.json` → dependencies, devDependencies, scripts
   - `pyproject.toml` / `requirements.txt` → Python 패키지
   - `tsconfig.json` → TypeScript 설정
   - 기타 언어별 설정 파일

2. **아키텍처 분석**: 디렉토리 구조를 탐색하여 패턴 파악
   - `find . -maxdepth 3 -type d` 로 구조 확인
   - `src/`, `app/`, `components/`, `api/`, `agents/` 등 주요 디렉토리 역할 파악

3. **컨벤션 추론**: 실제 코드에서 패턴 추출
   - 네이밍 컨벤션 (파일명, 컴포넌트명, 변수명)
   - 린트 설정 확인
   - 기존 코드에서 반복되는 패턴

4. **빌드/테스트 명령어 확인**: package.json scripts 또는 Makefile 에서 추출
   - 가능하면 `--help` 또는 `--dry-run`으로 실제 동작 검증

5. **기존 CLAUDE.md 확인**: 있으면 읽고 "개선 모드"로 전환
   - 기존 내용 중 유지할 것 / 개선할 것 / 추가할 것 분류

**Phase 2 — CLAUDE.md 생성 (Build)**

스캔 결과를 바탕으로 CLAUDE.md를 생성합니다:

1. 템플릿 구조에 맞춰 각 섹션 채우기
2. 설계 원칙 5가지 모두 적용 확인:
   - 온보딩 문서 수준의 완성도?
   - 구체적 > 일반적?
   - 실행 가능한 명령어?
   - Anti-Goals 포함?
   - 1,500~3,000 tokens 범위?
3. 개선 모드일 경우: diff 형태로 변경점 설명

**Phase 3 — 생태계 연결 (Connect)**

프로젝트 시그널을 기반으로 hplan plugin 추천:

1. 프로젝트 시그널 → 추천 매핑 테이블 참조
2. **관련 있는 것만** 추천 (전체 추천 금지)
3. 각 추천마다 "왜 이 프로젝트에 필요한지" 1줄 설명
4. 설치 명령어 제공
5. 에이전트 관련 시그널이 없으면 이 단계를 건너뜀

**Phase 4 — 검증 (Verify)**

1. Quality Gate 항목 전체 체크
2. 생성된 CLAUDE.md를 프로젝트 루트에 저장
3. "다음 추천 액션" 제시:
   - 에이전트 프로젝트 → "deliver/instruction으로 에이전트 Instruction을 설계하세요"
   - 일반 프로젝트 → "CLAUDE.md를 팀에 공유하고 피드백을 받으세요"

---

### 참고
- CLAUDE.md 설계 원칙: AI_PM 3.2 챕터 "CLAUDE.md 딥다이브"
- 프로젝트 스캔 패턴: Claude Code 프로젝트 초기화 모범사례
- hplan plugin 추천 매핑: Agent PM Lifecycle (Discover → Architect → Ship → Operate → Learn)

---

## Further Reading
- AI_PM 3.2 — CLAUDE.md 딥다이브: https://github.com/kimsanguine/AI_PM/blob/main/3.2-claude-md-deep-dive.md
- Anthropic, "Claude Code Best Practices" — Project memory setup
- hplan 전체 가이드: https://github.com/kimsanguine/hplan

## Contextual Knowledge (auto-loaded)

> 보조 파일이 존재할 때만 자동 로드됩니다. 파일이 없으면 건너뜁니다.

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`

### Test Cases
!`cat references/test-cases.md 2>/dev/null || echo ""`

### Troubleshooting
!`cat references/troubleshooting.md 2>/dev/null || echo ""`
