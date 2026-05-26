---
description: "Verify task/feature completion against CONDITIONAL_GO conditions in STATE.md. Syncs condition status (❌→✅) before any 'done' declaration. Use when marking a task complete, closing a sprint, or claiming a condition is met. Use --spec to run full Spec Compliance Review instead of STATE.md condition check."
argument-hint: "[task description or condition name] [--spec for PRD compliance check]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /harness-verify

개발 중 완료 선언 전에 실행하는 증거 게이트.
`harness/STATE.md`의 `verified_by` 파일 존재를 확인하고 조건 상태를 갱신합니다.

## Instructions

You are running `/harness-verify` for: **$ARGUMENTS**

### Step 1 — STATE.md 로드

```bash
cat harness/STATE.md 2>/dev/null || echo "STATE_MISSING"
```

`STATE_MISSING` → Stop. "harness/STATE.md 없음 — `/harness-build` 실행 후 CONDITIONAL_GO 출력이 필요합니다." 출력.

### Step 2 — 조건 anchor 검사

`STATE.md`의 `Active 조건` 테이블에서 `verified_by` 경로를 추출.
각 경로에 대해:

```bash
# 각 verified_by 경로에 대해
ls <verified_by_path> 2>/dev/null && echo "EXISTS" || echo "MISSING"
```

규칙:
- `verified_by` = "추후 기입" → 상태 유지 ❌, 경고만 출력 ("이 조건의 verified_by 파일 경로가 아직 기입되지 않았습니다.")
- 파일 EXISTS → 상태 ✅로 갱신
- 파일 MISSING → 상태 ❌ 유지

**중요**: 파일 존재 여부만 확인합니다. 테스트 통과 여부는 CI/pytest 책임입니다.

### Step 3 — STATE.md 갱신

검사 결과를 `harness/STATE.md`에 반영:
- ✅ 로 바뀐 조건은 해당 행의 `상태` 컬럼을 업데이트
- 변경된 행이 있으면 파일 저장 후 "N개 조건 갱신됨" 출력

### Step 4 — 완료 선언 판정

| 상태 | 판정 | 출력 |
|------|------|------|
| 모든 조건 ✅ | **COMPLETE** | "모든 조건 검증 완료 — 완료 선언 가능합니다." |
| 일부 ✅, 일부 ❌ | **PARTIAL** | "미검증 조건 N개 남음. 완료 선언 보류." + 미검증 목록 |
| 전부 ❌ | **BLOCKED** | "검증된 조건 없음. verified_by 파일을 먼저 생성하세요." |

### Step 5 — 대상 조건 매칭 (선택)

`$ARGUMENTS`가 조건 이름과 매칭되면 해당 조건만 선택적으로 체크:
- "free quota", "gate f", "p95" 등 부분 문자열 매칭
- 매칭된 조건 없으면 전체 조건 대상으로 실행

## Output Format

```
hplan-verify — [날짜]

조건 상태:
  ✅ [조건 1] — verified_by: tests/unit/test_foo.py
  ❌ [조건 2] — verified_by: 추후 기입 (경로 미기입)
  ❌ [조건 3] — verified_by: tests/unit/test_bar.py (파일 없음)

판정: PARTIAL — 미검증 조건 2개
다음: verified_by 파일을 생성하거나 경로를 STATE.md에 기입하세요.
```

## 주의

- 이 커맨드는 파일 존재만 확인합니다. 테스트 실행은 `pytest tests/` 로 별도 실행하세요.
- STATE.md의 `verified_by`를 채우는 것은 개발자 책임입니다.
- COMPLETE 판정이 나와야 하나의 CONDITIONAL_GO 사이클이 닫힙니다.

## `--spec` 단축 플래그

`$ARGUMENTS`가 `--spec`으로 시작하면 `/harness-build --step spec-review`로 라우팅한다.

```bash
# STATE.md 검사 대신 spec compliance 체크 실행
# /harness-verify --spec [brief]
# → harness-build --step spec-review [brief] 와 동일
```

이 플래그는 개발 완료 후 즉시 spec 준수 여부를 확인하고 싶을 때 사용한다.
STATE.md 조건 검사(기본 동작)와 달리 PRD 대비 구현 완성도를 검토한다.
