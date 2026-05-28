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
| `--mode adversarial` | **QA 라운드** — `harness/PERSONA_SPECS.json` + `harness/QA_POOL.json`을 읽어 페르소나·개발 에이전트를 동적 구성. CRITICAL/HIGH 발견 시 ralph loop 자동 수정. 라운드별 `harness/qa-rounds/round-N.md` + `harness/qa_log.jsonl` 기록. |

> **심각도 체계 구분**: 일반 모드(`--append`/`--regenerate`)는 `critical/major/minor` 3등급. `--mode adversarial`은 `CRITICAL/HIGH/MEDIUM/MINOR` 4등급. 두 체계는 **독립**이며 결과물도 별도 — 일반: `harness/QA_CHECKLIST.md` / adversarial: `harness/qa-rounds/round-N.md`.

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
- **배포 전 최종 QA 라운드** — `--mode adversarial`: `harness/QA_POOL.json`이 존재하고 실 사용자 페르소나 + 개발 리뷰어 관점 검수가 필요할 때

### Route to Other Skills When
- UI 런타임 검증 → `deliver/ui-validate`
- ship 직전 전체 게이트 → `deliver/respect --mode checkpoint`
- PRD 작성 (§15 QA Pool 포함) → `deliver/prd`
- 페르소나 구성 → `hplan/interview-synthesis` (PERSONA_SPECS.json 생성)

### Boundary Checks
- `docs/PRD.md` 부재 → fail loud + "docs/PRD.md 없음. `/harness-build --step prd` 또는 `/prd` (deliver 스킬, §15 QA Pool 포함) 먼저 실행하세요."
- Section 1(ICP) 부재 → fail loud + "PRD §1 ICP 섹션이 필요합니다."
- `harness/` 디렉터리 부재 → `mkdir -p harness/` 후 진행
- `--mode adversarial` + `harness/QA_POOL.json` 부재 → fail loud + "harness/QA_POOL.json 없음. /prd 실행 후 §15 QA Pool이 생성되어야 합니다."
- `--mode adversarial` + `harness/PERSONA_SPECS.json` 부재 → WARN (FAIL 아님) + "페르소나 없이 개발 리뷰어만으로 진행합니다. interview-synthesis 완료 후 재실행을 권장합니다."
- `--mode adversarial` + `harness/QA_POOL.json`의 `dev_roles: []` 빈 배열 → fail loud + "`dev_roles`가 비어 있습니다. /prd 재실행하고 §15 QA Pool을 완성하세요."

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| `--regenerate` / `--append` / `--mode adversarial` | `$ARGUMENTS` | 모드 분기 |
| ICP 조건 목록 | `docs/PRD.md` Section 1 | critical TC 후보 |
| 성공 지표 | `docs/PRD.md` Section 12 (있으면) | 성공 지표 기반 TC 후보 |
| 실패 시나리오 | `docs/PRD.md` Section 14 | major/critical TC 후보 |
| CONDITIONAL_GO 조건 | `harness/build-gate/checkpoint.json` (있으면) | 추가 TC 후보 |
| QA Pool | `harness/QA_POOL.json` (`--mode adversarial` 전용) | 동적 에이전트 역할 구성 |
| 페르소나 스펙 | `harness/PERSONA_SPECS.json` (`--mode adversarial` 전용, 선택) | 페르소나 에이전트 구성 |

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
`/harness-build --step prd` 또는 `/prd` (deliver 스킬) 먼저 실행하세요.
`--mode adversarial` 예정이면 `/prd`를 사용해야 §15 QA Pool(harness/QA_POOL.json)이 생성됩니다.
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

## Instructions (`--mode adversarial`)

You are running qa-checklist in **adversarial QA 라운드** mode.

### Step 1 — 사전 파일 확인

```bash
ls harness/QA_POOL.json 2>/dev/null || echo "QA_POOL_MISSING"
ls harness/PERSONA_SPECS.json 2>/dev/null || echo "PERSONA_MISSING"
ls docs/PRD.md 2>/dev/null || echo "PRD_MISSING"
```

- `QA_POOL_MISSING` → 즉시 종료: "harness/QA_POOL.json 없음. /prd 실행 후 §15 QA Pool 생성 필요."
- `PRD_MISSING` → 즉시 종료
- `PERSONA_MISSING` → WARN 출력 후 계속: "페르소나 없이 개발 리뷰어만으로 진행. interview-synthesis 완료 후 재실행 권장."

### Step 2 — 에이전트 풀 구성

`harness/QA_POOL.json` 로드 → `dev_roles` 배열에서 역할 목록 추출.
- `dev_roles`가 빈 배열(`[]`)이면 즉시 종료: "`dev_roles`가 비어 있습니다. /prd 재실행하고 §15 QA Pool을 완성하세요."
- `interview_evidence_verified` 필드가 `false`이면 WARN: "⚠️ interview_evidence_verified: false — 인터뷰 evidence 없이 생성된 QA Pool입니다. 결과 신뢰도가 낮을 수 있습니다. `python3 hplan/scripts/interview_synthesis.py import → tag → audit` 완료 후 `/prd` 재실행해 `interview_evidence_verified: true`로 갱신하세요."

`harness/PERSONA_SPECS.json` 존재 시 → P01~P0N 로드.
- PERSONA_SPECS.json 내용이 빈 배열(`[]`)이면 → PERSONA_MISSING과 동일하게 처리:
  WARN: "PERSONA_SPECS.json이 빈 배열입니다 — 페르소나 없이 개발 리뷰어만으로 진행합니다."

에이전트 풀 출력:
```
QA 라운드 에이전트 풀 (Round 1)
─────────────────────────────
페르소나: P01 박이사(노무담당), P02 최대리(스타트업 HR) ...
개발 리뷰어: frontend, backend, qa_engineer, legal_domain
총 N명 병렬 검토
```

### Step 3 — 라운드 실행

**각 에이전트 역할별 검토 포인트**:

| 역할 | 검토 관점 |
|------|-----------|
| 페르소나 (P0N) | ICP 페인 해소 여부, UX 흐름 이해도. **PERSONA_SPECS 활용**: `anxiety_tags` → 불안 TC, `trigger` → CRITICAL TC 시드, `experience_level=입문` → 온보딩 TC 우선, `experience_level=숙련` → 엣지케이스 TC 우선 |
| `frontend` | UI 반응성, 접근성(WCAG AA), 모바일 동작, 빈 상태 처리 |
| `backend` | API 에러 핸들링, 인증 흐름, 비동기 처리, 레이트 리밋 |
| `qa_engineer` | TC 커버리지, 경계값, 회귀 위험, 테스트 누락 |
| `ai_engineer` | 프롬프트 엣지케이스, 환각 시나리오, 토큰 예산 초과 |
| `legal_domain` | 법령 인용 정확성, 책임 범위 명시, 무면허 법률행위 경계 |
| `security` | 인증 우회, 입력 검증, PII 노출, OWASP Top 10 |

각 에이전트는 발견한 이슈를 `CRITICAL / HIGH / MEDIUM / MINOR` 4등급으로 분류.

**등급 기준**:
- `CRITICAL`: ICP 핵심 경로 차단 또는 법적 책임 위험
- `HIGH`: 대다수 사용자에 영향, 대안 없음
- `MEDIUM`: 일부 사용자 영향, 대안 존재
- `MINOR`: UX 개선 사항, 즉각 수정 불필요

### Step 4 — 결과 집계 및 보고서 생성

```bash
mkdir -p harness/qa-rounds
```

라운드 번호 결정:
```bash
ls harness/qa-rounds/round-*.md 2>/dev/null | wc -l
# N개 존재 → 이번 라운드 = round-(N+1)
```

`harness/qa-rounds/round-N.md` 생성:

```markdown
# QA 라운드 N — [제품명]
일시: YYYY-MM-DD HH:MM | 이전 라운드: N-1 (또는 최초)

## 에이전트 풀
- 페르소나: P01 [이름·역할], P02 [이름·역할] ...
- 개발 리뷰어: [역할 목록]

## 결과 요약
| 등급 | 건수 | 전 라운드 대비 |
|------|------|---------------|
| CRITICAL | N | ▼N |
| HIGH | N | ▼N |
| MEDIUM | N | - |
| MINOR | N | - |

## CRITICAL 이슈
| ID | 리뷰어 | 설명 | 수정 방법 |
|----|--------|------|----------|
| CR-01 | legal_domain | 산재 전치주의 설명 오기 | § 103 임의적 전치 표현으로 교체 |

## HIGH 이슈
...

## MEDIUM 이슈 (유예 가능)
...

## Auto-Fix 로그 (ralph loop)
| 이슈 ID | 수정 내용 | 커밋 | 검증 결과 |
|---------|----------|------|----------|
| CR-01 | legal_router.py L655 수정 | abc1234 | ✅ PASS |

## 최종 판정
CRITICAL: N | HIGH: N → [SHIP 가능 / REWORK 필요]
```

### Step 5 — Ralph Loop (CRITICAL·HIGH 자동 수정)

CRITICAL 또는 HIGH 이슈가 1건 이상이면:

```
1. 이슈별 자동 수정 시도
2. 수정 후 해당 테스트 재실행 (pytest / npm run build 등)
3. 통과 시 round-N.md Auto-Fix 로그에 기록 → auto_fixed 카운터 +1
4. 실패 또는 수정 불가 시 → deferred 카운터 +1, "수동 개입 필요" 표시
5. 종료 조건 (우선순위 순):
   a. deferred > 0 AND (CRITICAL > 0 OR HIGH > 0) → 즉시 Step 7 REWORK 경로 (무한 루프 방지)
   b. CRITICAL = 0 AND HIGH = 0 → Step 7 SHIP 경로
   c. auto_fixed > 0 AND (CRITICAL > 0 OR HIGH > 0) → 다음 라운드 진입
```

> **deferred 정의**: auto-fix를 시도했지만 실패하여 수동 개입이 필요한 CRITICAL/HIGH 이슈 건수. deferred > 0이면 라운드를 반복해도 이슈가 줄지 않으므로 즉시 REWORK으로 분기한다.

### Step 6 — qa_log.jsonl append

```bash
# harness/qa_log.jsonl에 이번 라운드 결과 append
```

```jsonl
{"round": 1, "ts_start": "...", "ts_end": "...", "agents": ["P01","P02","frontend","backend"], "critical": 2, "high": 3, "medium": 5, "minor": 8, "auto_fixed": 4, "deferred": 1, "fix_commits": ["abc1234"], "test_delta": "+3 passed", "verdict": "REWORK"}
{"round": 2, "ts_start": "...", "ts_end": "...", "agents": [...], "critical": 0, "high": 0, "medium": 4, "minor": 7, "auto_fixed": 3, "deferred": 0, "fix_commits": ["def4567"], "test_delta": "+2 passed", "verdict": "SHIP"}
```

### Step 7 — 최종 보고

CRITICAL = 0 AND HIGH = 0 시:
```
✅ QA 라운드 완료 — SHIP 가능
   총 N 라운드 | Auto-fixed: N건 | 유예(MEDIUM): N건
   보고서: harness/qa-rounds/round-N.md
   로그:   harness/qa_log.jsonl
   → 다음 단계: `/deliver/respect --mode checkpoint` (최종 배포 게이트) 또는 배포 진행
```

CRITICAL 또는 HIGH 잔존 시:
- `deferred > 0` (자동 수정 실패 이슈 존재):
```
⚠️  QA 라운드 중단 — 수동 개입 필요
   CRITICAL: N건 | HIGH: N건 (자동 수정 실패: N건)
   상세: harness/qa-rounds/round-N.md
   → 수정 후 /qa-checklist --mode adversarial 재실행
```
- `deferred = 0` (아직 auto-fix 미시도): 다음 라운드 자동 진입 (Step 3→5 반복)

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
| `--mode adversarial` + `QA_POOL.json` 부재 | `ls` 실패 | fail loud + "/prd 실행 후 §15 QA Pool 생성 필요" 후 종료 |
| `--mode adversarial` + `PERSONA_SPECS.json` 부재 | `ls` 실패 | WARN + 개발 리뷰어만으로 진행 |
| `--mode adversarial` ralph loop 수정 실패 | 테스트 재실행 실패 | "수동 개입 필요" 표시 후 라운드 종료, 사용자 보고 |

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
- [ ] (`--mode adversarial`) QA_POOL.json 부재 시 즉시 종료
- [ ] (`--mode adversarial`) PERSONA_SPECS.json 부재 시 WARN만 출력, 계속 진행
- [ ] (`--mode adversarial`) CRITICAL·HIGH 이슈는 ralph loop 자동 수정 시도 후 결과 로그에 기록
- [ ] (`--mode adversarial`) round-N.md에 에이전트 풀·등급별 건수·auto-fix 로그 포함
- [ ] (`--mode adversarial`) qa_log.jsonl에 라운드 결과 append됨
- [ ] (`--mode adversarial`) CRITICAL=0·HIGH=0 달성 시에만 "SHIP 가능" 판정

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
`/harness-build --step prd` 또는 `/prd` (deliver 스킬) 먼저 실행하세요.
`--mode adversarial` 예정이면 `/prd`를 사용해야 §15 QA Pool(harness/QA_POOL.json)이 생성됩니다.
```
실행 중단. TC 생성 금지.

### Bad Example
**입력:** `--append` (PRD에 §1 없음)

**기대 동작:** "PRD §1 ICP 섹션이 필요합니다." fail loud 후 종료. 부분 생성 금지.
