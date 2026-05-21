---
name: gate-checkpoint
description: "Enforce event-driven phase transition gates — requirements → design → tasks → implementation → verification → ship. Each gate has a deterministic checklist (file existence, content regex, exit codes) that PreToolUse Hook can BLOCK on. Unlike operate/scorecard-5axis (weekly absolute scoring), this is per-transition mechanical enforcement. Use after estimate-tasks defines phases, paired with progress-probe Hook for automatic gate firing on every tool call."
argument-hint: "[check <phase> | install | unlock <phase> --force]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

- 6 phase 전환을 결정론 체크리스트로 mechanical enforcement
- PreToolUse Hook 으로 미통과 phase 의 다음 작업을 **차단**
- LLM 호출 0 — 모든 게이트 조건이 파일 존재·정규식·exit code
- gate 통과 시 progress-report 의 trigger 1 (phase_transition) 발화

---

## 6 Phase 정의 (default — 사용자 override 가능)

| # | Phase | 통과 조건 (결정론) | 차단 대상 |
|---|---|---|---|
| 1 | **requirements** | PRD 파일 존재 + Section 1-3 비어 있지 않음 (정규식) | 다음 phase 의 design 파일 작성 |
| 2 | **design** | PRD Section 7-11 작성 + workflow mermaid 다이어그램 1개 (정규식) | implementation tool_call |
| 3 | **tasks** | `.track/predicted.json` 존재 + tasks 배열 ≥ 1 + 의존성 cycle 없음 (DFS) | implementation 직전 검증 |
| 4 | **implementation** | 모든 task 의 actual_log complete event 수 == predicted total_tasks | verification tool_call |
| 5 | **verification** | `python3 validate_plugins.py` exit 0 + 테스트 스위트 exit 0 + craft-lint exit 0 (UI 있으면) | ship phase |
| 6 | **ship** | git tag <version> + push origin + GitHub release 메타데이터 | (마지막 — 차단 없음) |

> 각 phase 의 통과 조건 yaml 은 `references/gate-conditions.yaml` 에 정의. 사용자가 phase 추가/제거 가능.

---

## Trigger Gate

### Use This Skill When
- estimate-tasks 가 predicted.json lock 직후 → install (Hook 등록)
- 각 phase 도달 시 자동 (PreToolUse Hook 발화)
- 강제 unlock 필요 (디버깅) → `--force` 명시

### Route to Other Skills When
- gate 통과의 자연어 보고 → `track/progress-report` 의 trigger 1
- 게이트 실패의 fix 권유 → `craft/craft-lint` (디자인) / 테스트 fix
- 가중치 기반 절대 점수 → `operate/scorecard-5axis` (cadence 다름)

### Boundary Checks
- phase 정의 yaml 없으면 default 6 phase 사용 + warning
- unlock --force 는 audit log 남김 (`.track/gate-unlock.log`)
- Hook 차단이 dev 워크플로우 방해 시 `--soft` 모드 (warning only)

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| 현재 phase | `.track/current-phase.txt` (gate-checkpoint 자체 관리) | text read |
| phase 정의 | `references/gate-conditions.yaml` 또는 default | yaml parse |
| tool_call event | PreToolUse Hook callback | 결정론 분기 |
| validate exit code | `bash python3 validate_plugins.py` | exit code |

---

## Instructions

You are operating gate-checkpoint in mode: **$ARGUMENTS**

### Mode: check <phase>

**Step 1 — phase 정의 로드**
- `references/gate-conditions.yaml` 또는 default 6 phase

**Step 2 — 통과 조건 결정론 검증**
```python
def check(phase):
    cond = gate_conditions[phase]
    results = []
    for c in cond:
        if c.type == "file_exists":
            results.append(Path(c.path).exists())
        elif c.type == "regex_in_file":
            results.append(bool(re.search(c.pattern, Path(c.path).read_text())))
        elif c.type == "bash_exit":
            results.append(subprocess.run(c.cmd, shell=True).returncode == 0)
        elif c.type == "json_path":
            results.append(jq_eval(c.path, c.query))
    return all(results), results
```

**Step 3 — 결과 보고**
- 통과: "✅ <phase> gate 통과" + 다음 phase 안내 + progress-report trigger
- 실패: "❌ <phase> gate 실패: <조건 X 미충족>" + fix 권유

### Mode: install

**Step 1 — `.track/current-phase.txt` 초기화**
- `requirements` 로 시작

**Step 2 — PreToolUse Hook 등록**
- `.claude/settings.json` 의 hooks.PreToolUse 에 `scripts/gate-block.sh` 명령 추가
- gate-block.sh: 현재 phase 의 통과 조건 검증 → exit 1 시 tool_call 차단

**Step 3 — gate-block.sh 작성 + chmod +x**

**Step 4 — smoke test**
- 임의 tool_call 발생 시 Hook 가 호출되는지 확인

### Mode: unlock <phase> --force

**Step 1 — audit log 작성**
- `.track/gate-unlock.log` append (ts, phase, reason)

**Step 2 — current-phase.txt 다음 phase 로 갱신**

**Step 3 — 사용자 경고**
- "<phase> 의 통과 조건 X 가 충족 안 됐는데 force unlock 됐음. 회귀 위험 ↑"

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| Hook 가 silent fail (issue #17688) | `gate-block.sh` 호출 안 됨 | shell fallback: 사용자가 `gate-checkpoint check <phase>` 수동 호출 |
| gate-conditions.yaml 손상 | yaml parse error | default 6 phase fallback + warning |
| `--force` 남용 (3회 이상) | audit log 카운터 | "gate-conditions 자체 재검토 권유" |
| current-phase.txt 누락 | file not found | `requirements` 로 자동 초기화 + warning |
| 검증 cmd 가 무한 실행 | timeout 30s | subprocess kill + 실패 처리 |

---

## Quality Gate

- [ ] 6 phase 모두 통과 조건 정의됨 (default 또는 사용자 override)
- [ ] 각 조건이 결정론 (LLM 호출 0)
- [ ] PreToolUse Hook 등록 후 smoke test 통과
- [ ] unlock --force 시 audit log 작성
- [ ] gate 통과 시 progress-report trigger 1 발화

---

## Examples

### Good Example
**입력:** "check tasks"

**기대 출력:**
```
🔒 Phase: tasks
  ✅ .track/predicted.json 존재
  ✅ tasks 배열 ≥ 1 (현재 12)
  ❌ 의존성 cycle 검출: T-008 → T-011 → T-008
  
Gate 실패. Fix: predicted.json 의 T-008 dependencies 재검토 필요.
```

### Bad Example
**입력:** "unlock implementation"

**왜 나쁜가:** --force 없이 unlock 시도 = 게이트 무력화 위험

**기대 동작:** "--force 명시 필요. 실제로 design phase 통과 못 한 상태에서 unlock 하시려면 audit log 동의 + 명시" fail loud

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Default Gate Conditions
!`cat references/gate-conditions.yaml 2>/dev/null || echo ""`

### Phase Customization
!`cat references/phase-customization.md 2>/dev/null || echo ""`
