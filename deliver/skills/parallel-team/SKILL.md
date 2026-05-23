---
name: parallel-team
description: "Dispatch a role-based parallel agent team for product delivery tasks. Defines 8 default roles (디자이너·개발자·품질담당자·마케터·리서처·배포담당자·까칠이·보안담당자) with worktree isolation. Use when ≥2 independent work streams exist after harness-plan is approved, or when superpowers:dispatching-parallel-agents is invoked. 까칠이 runs adversarial review after all other agents complete."
argument-hint: "[task brief from harness-plan]"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
model: sonnet
---

# /deliver:parallel-team — 역할 기반 병렬 에이전트 팀

Running for: **$ARGUMENTS**

---

## Core Goal

- `harness-plan`이 승인한 ARCHITECTURE.md를 **역할 기반 병렬 팀**으로 실행한다.
- 각 역할은 담당 도메인이 명확히 분리된다 — 같은 파일을 두 역할이 동시에 수정하지 않는다.
- 까칠이(Adversarial Reviewer)가 모든 팀원 결과물을 검토해 약점을 발굴한다.
- 보안 담당자가 머지 전 마지막 게이트를 막는다.

---

## 8-Role Default Team

모든 태스크에 8명이 투입되지 않는다. **아래 로스터에서 태스크 유형에 맞는 역할만 선택한다.**

| 역할 | 담당 범위 | 대표 산출물 | 필수/선택 |
|---|---|---|---|
| **디자이너** | 화면 레이아웃, 컴포넌트 디자인, 디자인 시스템 설계 | UI 스펙 · 와이어프레임 · 디자인 토큰 | 선택 |
| **개발자** | 코드 구현, 버그 수정, 기능 추가, 리팩토링 | PR-ready 코드 · 단위 테스트 | 거의 항상 |
| **품질담당자** | 테스트 코드 작성, 엣지 케이스 발굴, 회귀 방지 | e2e/통합 테스트 · 테스트 매트릭스 | 거의 항상 |
| **마케터** | 랜딩 카피, SEO, 출시 메시지, 채널별 콘텐츠 | 랜딩 텍스트 · Open Graph · GA 이벤트 플랜 | 선택 |
| **리서처** | 경쟁사 분석, 시장 조사, 기술·라이브러리 비교 | 비교 리포트 · ADR 초안 | 선택 |
| **배포 담당자** | 인프라 셋업, 환경 변수 관리, 도메인 연결, CI/CD | Dockerfile · wrangler.toml · GitHub Actions | 선택 |
| **까칠이** | 다른 팀원 결과물의 약점 발굴과 반박 | 반박 목록 · 수정 요청서 | **항상 (마지막)** |
| **보안 담당자** | 시크릿 노출 검사, 권한·취약점 점검, 푸시 전 가드 | 보안 체크리스트 · BLOCK/PASS 판정 | **항상 (머지 전)** |

---

## Role Selection Guide

태스크 brief에서 다음 키워드를 감지해 역할을 자동 선택한다.

| 키워드/특징 | 활성화 역할 |
|---|---|
| UI, 화면, 레이아웃, 컴포넌트, 디자인 | 디자이너 |
| 코드, 구현, API, 기능, 버그, 리팩터 | 개발자 |
| 테스트, QA, e2e, 회귀 | 품질담당자 |
| 랜딩, SEO, 카피, 출시, 마케팅 | 마케터 |
| 경쟁사, 시장, 라이브러리 비교, 기술 선택 | 리서처 |
| 배포, 인프라, CI/CD, 환경 변수, 도메인 | 배포 담당자 |
| (항상) | 까칠이, 보안 담당자 |

**최소 팀 구성:** 개발자 + 품질담당자 + 까칠이 + 보안 담당자 (4인)

---

## Instructions

### Step 1 — 역할 선택 + 작업 분해

1. `harness/ARCHITECTURE.md` 또는 `$ARGUMENTS`에서 작업 목록 추출
2. Role Selection Guide로 필요 역할 결정
3. 각 역할의 담당 파일 목록 명시 (겹침 = 0이어야 함)

```
디자이너: src/components/hero.tsx, src/styles/design-tokens.css
개발자: src/api/checkout.ts, src/lib/stripe.ts
품질담당자: tests/checkout.test.ts, tests/e2e/purchase.spec.ts
배포 담당자: .github/workflows/deploy.yml, wrangler.toml
```

### Step 2 — 독립성 검증

파일 쌍 충돌 검사. 충돌이 있으면 **직렬화** 또는 **분해 재설계**.

```bash
# 검증 예시
echo "디자이너-개발자 충돌 파일: $(comm -12 <(echo "디자이너 파일 목록") <(echo "개발자 파일 목록"))"
```

### Step 3 — Worktree 배치

```bash
# 각 역할마다 독립 worktree (git 저장소일 경우만 해당)
git worktree add .worktrees/designer main
git worktree add .worktrees/developer main
git worktree add .worktrees/qa main
# .gitignore에 .worktrees/ 추가
```

git 저장소가 아닌 경우: 각 에이전트는 `isolation: "worktree"` 파라미터 사용.

### Step 4 — 팀 디스패치 (단일 메시지)

**모든 역할 에이전트를 한 메시지에서 동시 호출한다.**
까칠이와 보안 담당자는 이 단계에서 호출하지 않는다.

```
Agent(디자이너, prompt="...")
Agent(개발자, prompt="...")
Agent(품질담당자, prompt="...")
Agent(배포담당자, prompt="...")  ← 단일 메시지 동시 호출
```

각 에이전트 prompt 필수 포함 항목:
- 자신의 역할과 담당 파일 목록
- 다른 역할 결과물에 접근 금지 (컨텍스트 격리)
- 완료 기준 + 산출물 경로

### Step 5 — 까칠이 리뷰 라운드

모든 에이전트 완료 후, 까칠이를 단독 호출한다.

**까칠이 프롬프트 구조:**
```
역할: 팀원 결과물을 검토하고 약점·위험·반박을 찾아라.
검토 대상: [디자이너/개발자/품질담당자/배포담당자 산출물 경로]
검토 관점:
- 각 역할의 가정이 틀린 경우는?
- 다른 역할의 결과물과 충돌하는 지점은?
- 엣지 케이스나 실패 경로가 누락된 곳은?
- 사용자 시나리오에서 깨지는 플로우는?
출력: 반박 목록 + 수정 요청서 (역할별 분류)
```

까칠이 결과를 기반으로 해당 역할 에이전트에게 수정 요청 (필요시).

### Step 6 — 보안 담당자 게이트 (머지 전 블로커)

**보안 담당자 체크리스트:**

```
[ ] .env · secrets · API key 하드코딩 없음
[ ] 환경 변수 사용 코드 — .env.example 업데이트됨
[ ] 외부 입력 검증 (XSS, SQL Injection, 경로 탈출)
[ ] 권한 범위 최소화 (least-privilege 원칙)
[ ] 로그에 PII / 토큰 노출 없음
[ ] 오픈 소스 라이선스 호환성 확인
[ ] CORS, CSP 헤더 미설정 없음 (웹 프로젝트)
```

**PASS** → 머지 진행  
**BLOCK** → 보안 문제 수정 후 재검사 (다른 에이전트 대기)

### Step 7 — 병합

```bash
# 순차 머지 (의존도 순서대로)
git merge .worktrees/designer
git merge .worktrees/developer
git merge .worktrees/qa
git merge .worktrees/deployment
```

충돌 발생 시: Step 1 재검토 — 독립성 평가가 잘못됨.

---

## 까칠이 Protocol (상세)

까칠이는 **팀의 일원이 아니다** — 팀 결과물을 외부 시각으로 검토하는 adversarial reviewer다.

| 원칙 | 설명 |
|---|---|
| 항상 마지막에 호출 | 다른 에이전트 완료 전 호출 금지 |
| 컨텍스트 격리 | 이전 팀원들의 "왜 이렇게 했는지" 설명을 보지 않음 |
| 방어 논리 차단 | "어쩔 수 없었다"는 설명 없이 결과물만 평가 |
| 구체적 반박 | "나빠 보인다" ❌ → "line 42: stripe key 하드코딩, 환경 변수로 교체 필요" ✅ |
| 수정 요청 형식 | `[역할] [파일:라인] [문제] → [권장 수정]` |

까칠이 결과가 없는 배포는 허용하지 않는다. 결과가 "문제 없음"이어도 리뷰 증거(빈 목록)를 `harness/team-review.md`에 기록한다.

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| 같은 파일 수정 | Step 2 충돌 검출 | 직렬화 또는 역할 경계 재설계 |
| 에이전트 1개 실패 | 개별 worktree 실패 | 해당 역할만 재시도, 나머지 유지 |
| 까칠이 수정 요청 다수 | 리뷰 결과 > 3건 BLOCK | 해당 역할 에이전트에게 수정 + 재검토 |
| 보안 BLOCK | Step 6 체크리스트 실패 | 보안 문제 수정 → 보안 담당자 재실행 |
| 머지 충돌 | git conflict | Step 1 재검토 — 독립성 잘못 평가됨 |

---

## Quality Gate

- [ ] 역할 선택 근거가 명시됨 (Role Selection Guide 기준)
- [ ] 각 역할의 담당 파일 목록 — 충돌 0건 확인됨
- [ ] 모든 에이전트 `isolation: "worktree"` 파라미터 사용
- [ ] 까칠이 리뷰 완료 + `harness/team-review.md` 기록
- [ ] 보안 담당자 PASS 확인 후 머지 진행
- [ ] 머지 완료 후 `validate_plugins.py` 또는 해당 프로젝트 테스트 통과

---

## Examples

### Good Example — 제품 기능 출시 (풀스택 + 마케팅)

**입력:** "결제 플로우 추가 (Stripe), 랜딩 카피 업데이트, 배포 파이프라인 구성"

**팀 구성:**
- 개발자: `src/api/checkout.ts`, `src/lib/stripe.ts`
- 마케터: `content/landing.md`, `src/components/hero.tsx` (카피만)
- 배포 담당자: `.github/workflows/deploy.yml`, `wrangler.toml`
- 품질담당자: `tests/checkout.test.ts`

**역할 충돌 검사:** `src/components/hero.tsx` — 마케터(카피)만 수정, 디자이너 없음 → 충돌 0

**순서:**
1. 개발자 + 마케터 + 배포 담당자 + 품질담당자 동시 디스패치
2. 완료 → 까칠이 리뷰
3. 수정 사항 반영 → 보안 담당자 PASS → 머지

---

### Bad Example — 잘못된 분해

**입력:** "App.tsx 리팩터링, 디자인 개선, 버그 수정"

**왜 나쁜가:**
- 디자이너·개발자 모두 `App.tsx` 수정 → 파일 충돌
- 병렬 불가 → 직렬 처리 또는 파일 분리 먼저

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Worktree Patterns
!`cat references/worktree-patterns.md 2>/dev/null || echo ""`
