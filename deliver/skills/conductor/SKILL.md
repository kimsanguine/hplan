---
name: conductor
description: "태스크별 fresh subagent 디스패치 + 2단계 게이트(spec→quality) 반복 실행. harness-plan 승인 후 구현 루프를 돌릴 때 사용. parallel-team이 역할 병렬이라면, conductor는 태스크 순차+게이트다."
argument-hint: "[plan source: PRD path or delivery brief]"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
model: sonnet
---

# /deliver:conductor — 태스크 순차 실행 + 2단계 게이트

Running for: **$ARGUMENTS**

---

## Core Goal

- `harness-plan`이 승인한 PRD 또는 PROGRESS.md를 **태스크별 순차 루프**로 실행한다.
- 각 태스크마다 구현 → Spec Compliance → Quality Gate 순으로 검증한다.
- 태스크 간 컨텍스트 오염을 막기 위해 subagent를 매 태스크마다 fresh하게 디스패치한다.
- PRD 섹션 단위 충족 여부를 체크리스트로 추적한다.

---

## parallel-team과의 차이

| 구분 | parallel-team (기존) | conductor (신규) |
|---|---|---|
| 실행 방식 | 역할별 동시 병렬 | 태스크별 순차 + 2단계 게이트 |
| 검토 시점 | 까칠이가 마지막 한 번 | 태스크마다 spec-review → quality-gate |
| subagent 격리 | worktree 사용 | fresh context per task |
| 스펙 추적 | 없음 | PRD 섹션 단위 충족 여부 추적 |

**언제 conductor를 선택하는가:**
- 태스크 간 의존도가 높아 순서를 바꿀 수 없을 때
- 각 태스크 완료 즉시 spec 정합성을 확인해야 할 때
- PRD 섹션별 진행률을 가시적으로 추적해야 할 때

---

## 역할 선택 가이드 (구현 에이전트 편성 시)

역할 기반 병렬 실행이 필요할 때(독립 태스크 ≥2개가 동시에 진행 가능한 경우) 아래 8역할 로스터에서 선택한다.

| 역할 | 담당 범위 | 대표 산출물 | 필수/선택 |
|---|---|---|---|
| **디자이너** | 화면 레이아웃, 컴포넌트 디자인, 디자인 시스템 | UI 스펙 · 와이어프레임 · 디자인 토큰 | 선택 |
| **개발자** | 코드 구현, 버그 수정, 기능 추가, 리팩터링 | PR-ready 코드 · 단위 테스트 | 거의 항상 |
| **품질담당자** | 테스트 코드 작성, 엣지 케이스 발굴, 회귀 방지 | e2e/통합 테스트 · 테스트 매트릭스 | 거의 항상 |
| **마케터** | 랜딩 카피, SEO, 출시 메시지, 채널별 콘텐츠 | 랜딩 텍스트 · Open Graph · GA 이벤트 플랜 | 선택 |
| **리서처** | 경쟁사 분석, 시장 조사, 기술·라이브러리 비교 | 비교 리포트 · ADR 초안 | 선택 |
| **배포 담당자** | 인프라 셋업, 환경 변수 관리, CI/CD | Dockerfile · wrangler.toml · GitHub Actions | 선택 |
| **까칠이** | 다른 팀원 결과물의 약점 발굴과 반박 | 반박 목록 · 수정 요청서 | **항상 (마지막)** |
| **보안 담당자** | 시크릿 노출 검사, 권한·취약점 점검 | 보안 체크리스트 · BLOCK/PASS 판정 | **항상 (머지 전)** |

키워드 기반 역할 선택: UI/화면/레이아웃 → 디자이너 / 코드/구현/버그 → 개발자 / 테스트/QA → 품질담당자 / 랜딩/SEO → 마케터 / 배포/인프라 → 배포 담당자. 까칠이·보안 담당자는 항상 포함.

**최소 팀 구성:** 개발자 + 품질담당자 + 까칠이 + 보안 담당자 (4인)

---

## 실행 루프

```
[Phase 1] 플랜 파싱
  - docs/PRD.md 또는 harness/PROGRESS.md에서 태스크 목록 추출
  - 각 태스크를 체크리스트로 변환 ([ ] 형식)

[Phase 2] 태스크별 루프 (태스크 하나씩 순서대로)
  For each task:
    Step A: 구현 에이전트 디스패치
      - 새 subagent에 태스크 텍스트 + 범위 + 허용 파일 전달
      - subagent는 구현 완료 후 STATUS 반환
          DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED

    Step B: Spec Compliance Check
      - harness-build --step spec-review 실행
      - ICP 정합성, 비기능 요건, 실패 모드 커버 3체크포인트
      - 미충족 항목 → 구현 에이전트에게 수정 요청 → 재검토

    Step C: Quality Gate
      - harness-build --step quality-gate 실행
      - 기술 부채 마커, 테스트 커버리지, 보안 기본 점검
      - PASS → 다음 태스크로. FAIL → 수정 후 재실행

    Step D: 태스크 완료 표시
      - [ ] → [x] 갱신
      - 완료 증거 (커밋 해시 또는 파일명) 기록

[Phase 3] 최종 리뷰
  - 전체 태스크 완료 후 spec-review 전체 실행
  - 완료 리포트 출력
```

---

## Instructions

### Step 1 — 플랜 파싱

1. `$ARGUMENTS`에서 PRD 경로 또는 delivery brief 추출
2. 우선순위: `docs/PRD.md` → `harness/PROGRESS.md` → `$ARGUMENTS` 인라인
3. 태스크 목록을 아래 형식으로 변환:

```
[ ] T1: [태스크 제목] — [담당 파일 범위]
[ ] T2: [태스크 제목] — [담당 파일 범위]
[ ] T3: [태스크 제목] — [담당 파일 범위]
```

태스크 목록 파싱 후 **즉시 실행**한다. (기본값: Continuous Execution)

사용자에게 묻는 유일한 이유:
- BLOCKED 상태가 자력으로 해결 불가능할 때
- PRD 자체가 모순되어 진행 불가할 때

`--confirm-plan` 플래그가 있을 때만 파싱 후 목록 확인 후 진행.

### 모델 선택 가이드

태스크의 PRD 관련 섹션을 기준으로 모델을 선택한다:

| 태스크 성격 | 관련 PRD 섹션 | 권장 모델 | 이유 |
|---|---|---|---|
| 에이전트 설계, LLM 아키텍처 | §7-11 (에이전트 사양) | opus (capable) | 설계 판단 + LLM 아키텍처 이해 필요 |
| 기능 구현, PRD 요건 해석 | §1-6 (Product 요건) | sonnet (standard) | PRD 해석 + 코드 구현 복합 |
| 포맷 변환, 파일 수정, 스캐폴딩 | §11 출력 포맷 구현 등 | haiku (fast) | 기계적 작업, 판단 불필요 |
| 검토 에이전트 (spec/quality) | 전체 | sonnet (standard) | 판단 필요하나 가장 넓은 범용 |

### Step 2 — 구현 에이전트 디스패치

각 태스크마다 `deliver/skills/conductor/prompts/implementer.md` 템플릿을 사용해
fresh subagent를 호출한다. 템플릿의 각 플레이스홀더를 현재 태스크 정보로 채운다.

마찬가지로:
- Spec Compliance Review: `prompts/spec-reviewer.md` 템플릿 사용
- Quality Review: `prompts/quality-reviewer.md` 템플릿 사용

### Step 3 — STATUS 처리

| STATUS | 처리 |
|---|---|
| `DONE` | 즉시 Spec Compliance로 이동 |
| `DONE_WITH_CONCERNS` | 우려사항 목록 검토 후 Spec으로 이동 |
| `NEEDS_CONTEXT` | 누락 컨텍스트 식별 → 제공 후 재디스패치 |
| `BLOCKED` | 블로커 원인 분석 → 컨텍스트 보완 or 태스크 분해 or 상위 에스컬레이션 |

`NEEDS_CONTEXT` 재디스패치는 최대 2회. 2회 초과 시 `BLOCKED`로 처리.

### Step 4 — Spec Compliance Check

3체크포인트를 순서대로 검증한다.

```
[ ] ICP 정합성: 구현 결과가 target user의 핵심 문제를 해결하는가
[ ] 비기능 요건: 성능·접근성·국제화 등 PRD 명시 요건이 충족되었는가
[ ] 실패 모드 커버: 주요 에러 경로가 명시적으로 처리되었는가
```

미충족 항목은 구현 에이전트에게 수정 요청 → 재검토. 재검토 횟수는 태스크당 최대 1회.

> **구현 전 4축 설계 검증이 필요한 경우**: 에이전트 3개 이상 오케스트레이션, 도구 5개 이상, 컨텍스트 50%+ 점유, 외부 API 3개 이상 의존 시 — 구현 에이전트 디스패치 전에 아래 4축 체크를 추가로 수행한다.
> - 범위(MVA: Minimum Viable Agent 정의, 기존 자산 재사용 가능성)
> - 아키텍처(오케스트레이션 패턴, 데이터 흐름, 단일 장애 지점)
> - 인스트럭션(7요소 완성도: Role/Context/Instructions/Tools/Memory/Output/GuardRails)
> - 신뢰성(장애 모드 매트릭스 최소 5종, 치명적 gap 수 명시)

### Step 5 — Quality Gate

3항목을 순서대로 점검한다.

```
[ ] 기술 부채 마커: TODO / FIXME / HACK 주석 신규 추가 없음
[ ] 테스트 커버리지: 태스크에서 수정된 함수에 대한 단위 테스트 존재
[ ] 보안 기본: 하드코딩된 시크릿, 검증 없는 외부 입력 없음
```

**PASS** → Step 6으로 진행  
**FAIL** → 해당 항목 수정 요청 → quality-gate 재실행 (1회 한도)

### Step 6 — 태스크 완료 표시

```
[x] T1: [태스크 제목] — 완료 증거: [커밋 해시 or 파일명]
```

완료 증거가 없는 체크 표시는 허용하지 않는다 (Rule 4 — Goal-Driven Execution).

### Step 7 — 최종 리뷰

전체 태스크 완료 후:

```bash
# 전체 spec-review
harness-build --step spec-review --scope all

# 완료 리포트
cat harness/PROGRESS.md
```

완료 리포트 포함 항목:
- 총 태스크 수 / 완료 수
- 게이트 통과 지연이 있었던 태스크 목록
- 미완료 태스크 (있을 경우) + 사유

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| 플랜 파싱 실패 | PRD/PROGRESS.md 없음 | `$ARGUMENTS` 인라인 파싱 시도 → 없으면 중단 |
| STATUS: BLOCKED 반환 | 에이전트 응답 | 블로커 원인 분석 → 분해 or 에스컬레이션 |
| Spec Compliance 재검토 실패 | 1회 수정 후 재검토에서도 미충족 | 해당 태스크 `WARN` 표시 + 사용자 에스컬레이션 |
| Quality Gate 재실행 실패 | FAIL 2회 | 태스크 중단 + 사유 기록, 다음 태스크 진행 여부 사용자 결정 |
| 완료 증거 없음 | 커밋/파일 경로 부재 | 완료 처리 거부 → 증거 요청 |

---

## Quality Gate (스킬 자체)

- [ ] 플랜 파싱 후 즉시 실행됨 (--confirm-plan 없는 경우)
- [ ] 각 태스크 에이전트 프롬프트에 허용 파일 범위 명시됨
- [ ] STATUS 처리 규칙이 각 태스크마다 적용됨
- [ ] Spec Compliance + Quality Gate가 모든 완료 태스크에 실행됨
- [ ] 완료 증거(커밋 해시 or 파일명) 없는 체크박스 없음
- [ ] 최종 리뷰 완료 리포트 출력됨

---

## Examples

### Good Example — 태스크별 순차 게이트 통과
!`cat examples/good-01.md 2>/dev/null || echo ""`
