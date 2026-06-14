---
name: interview-synthesis
description: "Import AI synthesis output (BuildBetter MCP, Perspective AI, and similar AI synthesis tools) into hplan, then force a human to tag each quote with strength (strong/medium/weak) and Push/Pull/Habit/Anxiety/workaround/trigger axes. AI extracts quotes; humans assign evidence strength. Audits the SKILL.md rule: 5 interviews with 3 distinct strong-Push signals → proceed to Product Gate."
argument-hint: "[import|tag|audit|list] <path or id>"
allowed-tools: ["Read", "Write", "Bash"]
model: inherit
---

# Interview Synthesis — AI Extracts, Human Tags

Running for: **$ARGUMENTS**

## Core Goal

- 2026 현실 반영 — 78% PM 팀이 AI 합성 사용. **차단하지 말고 받아들이되, evidence strength 태깅은 인간에게 강제**.
- AI는 quote 추출 + 테마 클러스터링; 인간은 strong/medium/weak + Push/Pull/Habit/Anxiety 축 부여.
- "5 interviews 중 3명이 같은 강한 Push를 말하면 Product Gate로" 규칙을 코드로 강제 (`PROCEED_TO_PRODUCT_GATE` verdict).

## Trigger Gate

### Use This Skill When

- BuildBetter / Perspective / similar synthesis tools export JSON이 손에 있을 때
- 인터뷰 5건 이상 — 수동 정리는 비용 비효율적
- `evidence-rubric` 점수에서 `interview_notes` 보강이 필요할 때
- 신규 PM이 인터뷰 evidence를 어떻게 태깅해야 하는지 학습할 때

### Route to Other Skills When

- 5/3 패턴 통과 → Product Gate (`ost` skill)
- 5명 미만 → 추가 인터뷰 (skill 외 실세계 행동)
- 태그된 quote 강도가 너무 낮음 → `pivot` 또는 `hold` 결정 → `decision-log`

### Boundary Checks

- ❌ AI 합성이 evidence를 *대체할 수 없다*. 태그 안 된 quote는 evidence가 아니다.
- ❌ AI sentiment ≠ evidence strength. 인간이 직접 판단.

## Inputs

Expected AI export JSON shape:

```json
{
  "source": "buildbetter",
  "interviews": [
    {
      "person": "ICP candidate 1",
      "role": "HR 담당자 (선택 입력)",
      "company_size": "50-200명 (선택 입력)",
      "date": "2026-05-09",
      "quotes": [
        {"text": "지난주에 30분 또 날렸어요", "theme": "manual workaround"},
        {"text": "이거 안 되면 영업 못 따요", "theme": "economic pain"}
      ]
    }
  ]
}
```

> **`role` 필드 처리 정책**: `role`이 AI export JSON에 있으면 PERSONA_SPECS.json에 그대로 기입 (결정론). 없으면 `null`로 저장 — 이 경우 LLM이 ICP 컨텍스트 기반으로 추론하지 않으며, 수동으로 채워야 합니다. `role`은 PERSONA_SPECS 생성 규칙의 "LLM 추론 금지" 원칙의 예외가 아닌, 입력 데이터 부재 시 명시적 `null` 처리로 대응합니다.

## Steps

실행은 `python3 hplan/scripts/interview_synthesis.py <subcommand>` 형태로 호출합니다.

1. `python3 hplan/scripts/interview_synthesis.py import <ai_export.json>` — quotes를 `harness/evidence/snapshots.jsonl` 에 ingest (status: awaiting_human_tag).
2. `python3 hplan/scripts/interview_synthesis.py list --untagged` — 미태깅 quote 확인.
3. quote마다 `python3 hplan/scripts/interview_synthesis.py tag <quote_id> --strength strong --axes push,anxiety` — 인간 입력.
4. `python3 hplan/scripts/interview_synthesis.py audit` — 5/3 규칙 통과 여부 + 다음 액션 가이드.
5. `audit` 결과가 `PROCEED_TO_PRODUCT_GATE`이면 **PERSONA_SPECS.json 저장** — 태깅된 인터뷰이를 QA 라운드용 페르소나로 구조화해 `harness/PERSONA_SPECS.json`에 기록.

### PERSONA_SPECS.json 생성 규칙

- **대상**: `strength: strong` 또는 `medium` quote가 2개 이상인 인터뷰이만 포함 (noise 제거)
- **결정론**: id·name·anxiety_tags·trigger·experience_level은 태깅 데이터에서 직접 추출 (LLM 추론 금지)
- **null 처리**: `role`과 `company_size`는 AI export JSON에 해당 필드가 있으면 기입, 없으면 `null` 저장 — LLM 추론으로 채우지 않음.
- **experience_level**: `axes`에 `habit` strong이 있으면 "숙련", `push` strong만 있으면 "입문", 혼재 시 "중급", strong 신호 없으면 "입문" (default) — 결정론 매핑, 4 케이스 모두 코드에서 처리

```json
// harness/PERSONA_SPECS.json
[
  {
    "id": "P01",
    "name": "인터뷰이 이름 또는 익명 ID",
    "role": "AI export JSON passthrough — 없으면 null (수동 입력)",
    "anxiety_tags": ["anxiety"],
    "trigger": "가장 강한 strong push quote 앞 80자 (없으면 빈 문자열)",
    "experience_level": "입문 | 중급 | 숙련",
    "company_size": "AI export JSON passthrough — 없으면 null (수동 입력)"
  }
]
```

- `PROCEED_TO_PRODUCT_GATE`가 아닌 경우 PERSONA_SPECS.json **생성하지 않음** — 미충족 evidence로 QA 진입 방지.

## Outputs

- `harness/evidence/snapshots.jsonl` — append-only quote 저장소
- audit returns: `interviews, tagged_quotes, untagged_quotes, by_strength, persons_with_strong_push, verdict, persona_specs, guidance`
- `harness/PERSONA_SPECS.json` — PROCEED_TO_PRODUCT_GATE 시에만 생성. QA 라운드(`qa-checklist --mode adversarial`)의 페르소나 에이전트 설정 소스.

## Verification

- [ ] 모든 imported quote는 처음에 `status: awaiting_human_tag`
- [ ] tag 후 `status: tagged`, `strength`, `axes`, `tagged_at` 채워짐
- [ ] verdict는 `PROCEED_TO_PRODUCT_GATE` (5인터뷰 + 3 distinct strong-push) 또는 `INTERVIEW_OR_HOLD`
  - **distinct 정의**: 개인 단위 dedup — 같은 회사·팀 소속이어도 서로 다른 개인이면 distinct로 계산. 단, 동일 인물의 복수 세션은 1명으로 카운트.
- [ ] `PROCEED_TO_PRODUCT_GATE` 시 `harness/PERSONA_SPECS.json` 존재, strong/medium 인터뷰이만 포함됨
- [ ] `INTERVIEW_OR_HOLD` 시 `harness/PERSONA_SPECS.json` 생성되지 않음

## Why this design

다른 인터뷰 도구들은 "AI summary"를 evidence처럼 다룬다 — 위험. 한 LLM이 5개 인터뷰를 요약하면 자기 bias가 들어감. hplan은 **AI = quote 추출기**, **human = strength 판단**으로 명확히 분리.
