---
name: qa-checklist
description: "docs/PRD.md를 파싱해 harness/QA_CHECKLIST.md를 자동 생성. ICP/실패 시나리오 기반으로 TC를 critical/major/minor 3등급으로 분류하고 디바이스·환경 링크. deliver 완료 후 또는 harness-build --step quality-gate 전에 실행."
argument-hint: "[--regenerate | --append]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

`docs/PRD.md`의 ICP·성공 지표·실패 시나리오 섹션을 파싱해
`harness/QA_CHECKLIST.md`를 자동 생성한다.

| 모드 | 동작 |
|---|---|
| `--append` (기본값) | 기존 TC 유지, 새로 생성된 TC만 추가, 중복 제거 |
| `--regenerate` | 기존 파일 덮어쓰기 |

---

## Rule 5 준수 — 심각도 분류는 명시적 기준으로 결정

| 판단 | 도구 | LLM |
|---|---|---|
| PRD 섹션 존재 여부 | grep/Read | ❌ |
| ICP 조건 목록 추출 | 텍스트 파싱 | ✅ (비정형 추출) |
| 실패 시나리오 목록 추출 | 텍스트 파싱 | ✅ (비정형 추출) |
| 심각도 분류 | 아래 명시된 기준 + LLM | ✅ |
| 디바이스/환경 판단 | PRD 플랫폼 키워드 → 결정론 매핑 | ❌ |
| TC-ID 번호 부여 | 순번 증가 | ❌ |
| PRD 섹션 커버리지 집계 | 파일 존재 여부 | ❌ |

---

## 심각도 분류 기준

- **critical**: ICP가 이 시나리오 없이 핵심 목표를 달성 못 함 (결제, 회원가입, 핵심 기능 등)
- **major**: 대체 경로 존재하지만 현저히 불편하거나 ICP의 20% 이상에 영향
- **minor**: 엣지 케이스, 특수 환경, 브랜드 영향 낮음

---

## 디바이스/환경 판단 로직

PRD에 명시된 타겟 플랫폼 기준:

| PRD 키워드 | 포함 환경 |
|---|---|
| Web app / 웹앱 | Chrome Desktop, Safari Mobile |
| Mobile app / 모바일앱 | iOS 최신+1, Android 최신+1 |
| API / CLI | 해당 런타임 환경 |
| 미명시 | 모든 주요 브라우저 |

---

## Trigger Gate

### Use This Skill When
- deliver 완료 후, QA 체크리스트 작성 전
- `harness-build --step quality-gate` 실행 전
- PRD가 업데이트되어 TC 재생성이 필요할 때

### Route to Other Skills When
- UI 런타임 검증 → `deliver/ui-validate`
- ship 직전 전체 게이트 → `deliver/respect --mode checkpoint`
- PRD 작성 → `deliver/prd`

### Boundary Checks
- `docs/PRD.md` 부재 → fail loud + "docs/PRD.md 없음. /harness-build --step prd 먼저 실행하세요."
- Section 1(ICP) 부재 → fail loud + "PRD §1 ICP 섹션이 필요합니다."
- `harness/` 디렉터리 부재 → `mkdir -p harness/` 후 진행

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| `--regenerate` / `--append` | `$ARGUMENTS` | 모드 분기 |
| ICP 조건 목록 | `docs/PRD.md` Section 1 | critical TC 후보 |
| 성공 지표 | `docs/PRD.md` Section 12 (있으면) | 성공 지표 기반 TC 후보 |
| 실패 시나리오 | `docs/PRD.md` Section 14 | major/critical TC 후보 |
| CONDITIONAL_GO 조건 | `harness/build-gate/checkpoint.json` (있으면) | 추가 TC 후보 |

---

## Instructions

You are running qa-checklist with arguments: **$ARGUMENTS**

### Step 1 — 인자 파싱 및 PRD 로드

```
mode = "--regenerate" if "--regenerate" in $ARGUMENTS else "--append"
```

```bash
ls docs/PRD.md 2>/dev/null || echo "PRD_MISSING"
```

PRD_MISSING 시:
```
❌ 에러: docs/PRD.md 없음.
/harness-build --step prd 먼저 실행하세요.
```
즉시 종료.

### Step 2 — PRD 섹션 추출

다음 섹션을 순서대로 Read해 내용을 추출한다:

- **§1 ICP / 타겟 사용자**: ICP 정의, 주요 사용 시나리오, 핵심 목표 목록
  - 부재 시 fail loud: "PRD §1 ICP 섹션이 필요합니다."
- **§12 성공 지표** (있으면): 성공 지표 및 측정 기준
- **§14 실패 시나리오** (있으면): 예상 실패 케이스 목록

```bash
# checkpoint.json 존재 시 CONDITIONAL_GO 조건 추출
cat harness/build-gate/checkpoint.json 2>/dev/null | grep -A2 "CONDITIONAL_GO" || true
```

### Step 3 — TC 생성 및 심각도 분류

각 입력 소스에서 TC 후보를 생성하고 심각도를 분류한다:

**critical 생성 규칙 (§1 ICP 기반)**:
- ICP의 핵심 목표 달성에 직결되는 시나리오 → critical
- 회원가입, 로그인, 결제, 핵심 기능 단일 경로 → critical

**major/critical 생성 규칙 (§14 실패 시나리오 기반)**:
- 서비스 완전 불가 → critical
- 기능 저하, 대체 경로 존재 → major

**minor 생성 규칙**:
- 엣지 케이스, 특수 환경, UX 저하 없는 브랜드 이슈 → minor

**디바이스/환경**: 위 판단 로직 테이블 적용 (결정론)

**TC-ID**: `TC-001`부터 세 자리 순번으로 자동 부여

### Step 4 — harness/QA_CHECKLIST.md 작성

```bash
mkdir -p harness
```

**`--regenerate` 모드**: 파일 전체 덮어쓰기

**`--append` 모드**:
- 기존 파일 Read → 기존 TC-ID 목록 추출
- 신규 TC만 추가 (기존 ID와 시나리오 중복 제거)
- TC-ID는 기존 최대값+1부터 부여

출력 형식:

```markdown
# QA Checklist — [제품명]
생성: YYYY-MM-DD | 소스: docs/PRD.md

## 🔴 Critical (ICP 핵심 경로)
| TC-ID | 시나리오 | 환경/디바이스 | 전제조건 | 기대 결과 | PRD 출처 | 심각도 |
|---|---|---|---|---|---|---|
| TC-001 | ... | ... | ... | ... | §1 ICP | critical |

## 🟡 Major (대체 경로 존재, 현저히 불편)
| TC-ID | 시나리오 | 환경/디바이스 | 전제조건 | 기대 결과 | PRD 출처 | 심각도 |
|---|---|---|---|---|---|---|

## 🟢 Minor (엣지 케이스)
| TC-ID | 시나리오 | 환경/디바이스 | 전제조건 | 기대 결과 | PRD 출처 | 심각도 |
|---|---|---|---|---|---|---|

## 통계
- Total: N개 | Critical: X | Major: Y | Minor: Z
- PRD 섹션 커버리지: §1 ✅/❌, §12 ✅/❌, §14 ✅/❌
```

### Step 5 — 통계 출력

```
✅ harness/QA_CHECKLIST.md 생성 완료
   Total: N | Critical: X | Major: Y | Minor: Z
   커버리지: §1 ICP ✅ | §12 성공지표 [✅/❌(없음)] | §14 실패시나리오 [✅/❌(없음)]
```

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| `docs/PRD.md` 부재 | `ls` 실패 | fail loud + "harness-build --step prd 먼저" 안내 후 종료 |
| §1 ICP 섹션 부재 | 섹션 추출 결과 없음 | fail loud + "PRD §1 ICP 섹션이 필요합니다." 후 종료 |
| §12/§14 부재 | 섹션 추출 결과 없음 | SKIP (FAIL 아님) + 커버리지에 ❌ 표시 |
| `harness/` 부재 | `ls` 실패 | `mkdir -p harness/` 후 진행 |
| `checkpoint.json` 부재 | `cat` 실패 | SKIP + 경고 없이 계속 |
| `--append`에서 기존 파일 없음 | Read 실패 | `--regenerate`와 동일하게 신규 생성 |

---

## Quality Gate

- [ ] PRD_MISSING 시 즉시 종료, auto-generation 금지
- [ ] §1 ICP 부재 시 즉시 종료
- [ ] §12/§14 부재는 SKIP (FAIL 아님)
- [ ] 심각도 분류가 명시된 기준을 따름 (임의 분류 금지)
- [ ] 디바이스/환경이 PRD 플랫폼 키워드 기반 결정론 매핑으로 결정됨
- [ ] TC-ID가 TC-001부터 세 자리 순번으로 부여됨
- [ ] `--append` 모드에서 기존 TC가 삭제되지 않음
- [ ] 통계 줄이 실제 TC 수와 일치함

---

## Examples

### Good Example
**입력:** `--append` (기본값, docs/PRD.md 존재, §1·§14 있음)

**기대 동작:**
1. PRD §1에서 ICP 조건 추출 → critical TC 후보
2. PRD §14에서 실패 시나리오 추출 → major/critical TC 후보
3. 심각도 기준으로 분류
4. harness/QA_CHECKLIST.md 생성
5. 통계 출력

### Good Example
**입력:** `--regenerate`

**기대 동작:** 기존 `harness/QA_CHECKLIST.md`를 덮어쓰고 PRD 전체 재파싱

### Bad Example
**입력:** `--append` (docs/PRD.md 없음)

**기대 동작:**
```
❌ 에러: docs/PRD.md 없음.
/harness-build --step prd 먼저 실행하세요.
```
실행 중단. TC 생성 금지.

### Bad Example
**입력:** `--append` (PRD에 §1 없음)

**기대 동작:** "PRD §1 ICP 섹션이 필요합니다." fail loud 후 종료. 부분 생성 금지.
