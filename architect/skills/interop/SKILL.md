---
name: interop
description: "Choose an agent connection/interoperability standard (MCP, A2A, and emerging vendor standards) and design for portability across harnesses (Claude Code, Codex, Cursor, Kiro). Covers vendor lock-in risk scoring and the file-as-durable-state pattern that keeps agent state harness-agnostic. Use when deciding which connection standard to bet on, when one agent must talk to another across systems, or when the same skillset must run on more than one harness."
argument-hint: "[agent/skillset to connect] [--mode select|portability|durable-state]"
allowed-tools: ["Read", "Grep"]
model: inherit
---

# Interop & Portability

> 연결 표준 선택과 하네스 간 이식성 설계

## Core Goal

- **연결 표준을 lock-in 리스크와 함께 선택** — MCP·A2A·신생 벤더 표준(예: 구글·MS 공동 발표 연결 표준)을 전송·도구 노출·탐색·성숙도·생태계·이탈비용 축으로 비교.
- **하네스 간 이식성을 아키텍처로 확보** — 같은 스킬셋이 Claude Code·Codex·Cursor·Kiro에서 돌도록 "이식 가능(SKILL.md) vs 비이식(commands·hooks)"을 분리하고 추상화 계층을 설계.
- **파일=durable state 패턴으로 표준 변화에 면역** — 에이전트 상태를 파일(markdown+frontmatter)에 두어 하네스·표준이 바뀌어도 상태가 살아남게 한다.

---

## Trigger Gate

### Use This Skill When

- 에이전트 연결 **표준에 베팅**해야 할 때 — MCP로 갈지, A2A로 갈지, 신생 표준을 기다릴지
- 한 에이전트가 **다른 시스템/에이전트와 통신**해야 하는데 전송·프로토콜 선택이 필요할 때
- 같은 스킬셋을 **2개 이상 하네스**(Claude Code + Codex 등)에서 유지하는 이식성 고통이 있을 때
- 단일 벤더 전송에 묶였을 때의 **lock-in 리스크**를 평가할 때

### Route to Other Skills When

- **orchestration** → 시스템 *내부* 에이전트 협력 패턴(순차·병렬·계층)이 핵심일 때 (연결 표준이 아니라 조율)
- **orchestration `--pattern router`** → 모델 라우팅(복잡도별 LLM 선택)이 핵심일 때
- **memory-arch** → 메모리 *계층*(Working/Episodic/Semantic/Procedural) 설계가 핵심일 때 (durable-state는 "어디에 두나", memory-arch는 "어떻게 계층화하나")
- **deliver:instruction** → 선택한 전송/도구를 시스템 프롬프트의 도구 정의로 옮길 때

### Boundary Checks

- **표준 미성숙** — 신생 표준은 스펙·생태계가 흔들린다 → 베팅 전 "철회 가능성(reversibility)"을 먼저 점검.
- **이식성 과설계** — 모든 하네스 지원을 처음부터 추상화하면 속도가 죽는다 → 실제 타깃 하네스 2개로 한정 후 확장.
- **표준 ≠ 보안** — 연결 표준 선택은 권한·DLP를 보장하지 않는다 → 권한·정지는 operate:govern 으로 위임.

---

## 개념

연결 표준 경쟁에서 "어떤 모델이 더 똑똑한가"보다 "내 에이전트가 어느 규약 위에 사는가"가 lock-in을 결정한다. 표준은 바뀌고 벤더는 합쳐지므로, 한 전송에 상태까지 묶으면 표준이 흔들릴 때 전부 잃는다. 그래서 **상태는 파일에, 전송은 교체 가능한 어댑터로** 두는 설계가 이식성의 핵심이다.

## Instructions

You are designing interop/portability for: **$ARGUMENTS**

### --mode select — 연결 표준 선택

후보 표준을 축으로 비교한다.

| 축 | MCP | A2A | 신생 벤더 표준 | 자체 전송 |
|----|-----|-----|----------------|-----------|
| 무엇을 연결 | 도구·컨텍스트 | 에이전트↔에이전트 | (벤더별) | 임의 |
| 성숙도/생태계 | | | | |
| 도구 노출·탐색 | | | | |
| 이탈비용(lock-in) | | | | |
| 철회 가능성 | | | | |

- 지금 필요한 게 **도구 연결**인가(→MCP 계열) **에이전트 간 위임**인가(→A2A 계열)
- 신생 표준은 "기다림의 옵션 가치 vs 조기 채택 리스크"로 판단

### --mode portability — 하네스 간 이식성

타깃 하네스(예: Claude Code · Codex · Cursor · Kiro)별로 이식 가능 여부를 매트릭스화한다.

| 자산 | Claude Code | Codex | Cursor | 이식성 |
|------|-------------|-------|--------|--------|
| SKILL.md (스킬 본문) | ✅ | ✅(복사) | ✅(복사) | 높음 |
| commands (슬래시) | ✅ | ❌ | ❌ | 낮음 |
| hooks | ⚠️ | ❌ | ❌ | 낮음 |
| 전송/도구 바인딩 | 어댑터 | 어댑터 | 어댑터 | 어댑터로 분리 |

- 이식 가능 자산(스킬 본문)과 비이식 자산(commands·hooks)을 **물리적으로 분리**
- 비이식 부분은 하네스별 얇은 어댑터로 격리 → 본체는 한 벌 유지

### --mode durable-state — 파일=durable state

- 에이전트 상태(메모리·로그·결정·인덱스)를 **파일(markdown+frontmatter)** 로 둔다
- 하네스/표준이 바뀌어도 파일은 그대로 → 상태가 전송에 묶이지 않는다
- frontmatter를 상호운용 표준(예: 공개 지식 포맷)에 맞추면 다른 도구도 읽는다
- 워크드 케이스: 한 스킬셋을 Claude Code(`hplan`)와 Codex(`hplan_codex`) 두 하네스로 유지할 때, 공통 SKILL.md + 하네스별 어댑터 + 파일 상태로 분리하면 본체 한 벌로 양쪽을 커버

### Output

Interop 결정 카드:
```
대상: [agent/skillset]
지금 필요: [도구 연결 / 에이전트 위임 / 멀티 하네스]
선택 표준: [MCP / A2A / 신생 / 자체] + 이유
lock-in 점수: [Low/Med/High] (철회 가능성: ...)
이식 전략: 본체(스킬) 1벌 + 어댑터 N개 + 파일 상태
durable state: [상태를 두는 파일/포맷]
재검토 트리거: [표준 성숙·벤더 변화 시점]
```

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| **신생 표준에 조기 올인** | 발표 직후 표준에 상태·전송을 전부 묶음 | 철회 가능성 점검 → 어댑터 계층 뒤로 격리, 상태는 파일로 분리 |
| **이식성 과설계** | 사용하지도 않는 하네스까지 추상화하다 출시 지연 | 실제 타깃 2개로 한정, 3번째부터 어댑터 추가 |
| **commands를 본체에 섞음** | 슬래시 명령·hook에 핵심 로직이 들어가 Codex/Cursor로 못 옮김 | 로직을 SKILL.md(이식 가능)로 내리고 command는 얇은 진입점으로 |
| **상태가 전송에 묶임** | 표준 교체 시 메모리·로그까지 마이그레이션 필요 | 파일=durable state로 분리 (전송은 교체, 상태는 보존) |
| **표준이 보안을 대신한다고 오해** | "MCP 쓰니 권한은 알아서 안전" | 연결 표준은 권한·DLP를 보장 안 함 → operate:govern 로 분리 점검 |

---

## Quality Gate

- [ ] 지금 필요한 게 도구 연결인지/에이전트 위임인지/멀티 하네스인지 먼저 규정했는가? (Yes/No)
- [ ] 후보 표준을 이탈비용·철회 가능성 축까지 포함해 비교했는가? (Yes/No)
- [ ] 이식 가능 자산(스킬)과 비이식 자산(commands·hooks)을 분리했는가? (Yes/No)
- [ ] durable state를 파일/포맷으로 명시해 전송과 분리했는가? (Yes/No)
- [ ] lock-in 점수와 재검토 트리거(표준 성숙·벤더 변화)가 명시되었는가? (Yes/No)
- [ ] 권한·보안은 operate:govern 으로 위임했는가(이 스킬에서 보안을 보장하지 않음)? (Yes/No)

---

## Examples

### Good Example

```
대상: PM 에이전트 스킬셋 (Claude Code + Codex 동시 유지)
지금 필요: 멀티 하네스 이식성
선택: 표준 베팅 보류 + 파일 상태 우선
  - 본체 = SKILL.md 한 벌 (양 하네스 복사 가능)
  - 비이식 = commands/hooks → 하네스별 얇은 어댑터로 격리
  - durable state = markdown+frontmatter 파일 (메모리·결정 로그)
lock-in 점수: Low (전송 교체해도 상태·본체 보존)
재검토 트리거: 구글·MS 연결 표준 생태계가 임계 도달 시 어댑터 1개 추가
```

왜 좋은가: 표준이 흔들려도 본체·상태는 한 벌로 보존, 하네스 추가는 어댑터 1개로 끝.

### Bad Example

```
"신생 연결 표준 발표됐으니 전 에이전트를 거기에 맞춰 다시 짜자.
 메모리도 그 표준 저장소에 넣고."

❌ 문제점:
- 미성숙 표준에 상태까지 올인 → 표준 바뀌면 전부 마이그레이션
- 철회 가능성 미점검 (베팅의 옵션 가치 무시)
- 이식 가능/비이식 자산 미분리 → 다른 하네스로 못 옮김
- 상태를 전송에 묶음 (파일 분리 안 함)

→ 재작업: 필요(도구/위임/멀티하네스) 규정 → 어댑터 뒤로 표준 격리 → 상태는 파일로
```

---

## Further Reading
- Model Context Protocol (MCP) — 도구·컨텍스트 연결 스펙
- Agent2Agent (A2A) — 에이전트 간 상호운용 프로토콜
- "File over app" (Steph Ango) — 상태를 앱이 아니라 파일에 두는 원칙
- Anthropic, "Building Effective Agents" (2024) — 도구·전송 경계 설계

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
