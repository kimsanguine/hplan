---
name: respect-brief
description: "Generate RESPECT.md (hplan extension to Google DESIGN.md standard) BEFORE any UI code is written — the design brief that captures three_second_rule / next_action / social_proof / hierarchy_rules / motion_language as mechanically enforceable constraints. Acts as the input gate for craft-lint and feeds the gate-matrix lookup in track/respect-checkpoint. Use when starting a new screen, redesign, or any UI-bearing feature — RESPECT.md absent means craft-lint exit 2."
argument-hint: "[screen name or feature]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

- 화면 코딩 전에 RESPECT.md 생성 — "respect before design" 원칙
- 5개 핵심 의도 commit: three_second_rule / next_action / social_proof / hierarchy_rules / motion_language
- 결정론 검증 가능한 YAML 스키마 (craft-lint 가 픽셀 분석 없이 정합성 검증)
- DESIGN.md (Google 표준 토큰) 와 cross-reference 강제

---

## 영상 5번 통찰 (왜 이 스킬이 필요한가)

"AI 는 기능을 만들어 주지만, **이 존중은 사람이 넣는 겁니다**." (UX 심리학 5가지 트릭)

기존 DESIGN.md 표준의 한계:
- Token (색·폰트·간격) 만 명시 → "professionally generic" 양산
- 사용자 목적·3초 룰·다음 행동·social proof 의 영역 없음
- Adobe 2026 트렌드 "hybrid craft" (AI raw + human-touched) 의 human-touched 레이어 부재

respect-brief 가 채우는 것: **token 위의 의도 레이어**.

---

## RESPECT.md 스키마 (필수 5 섹션)

```yaml
screen: "<화면 이름>"
references_design_md: ./DESIGN.md     # 표준 파일 cross-ref 강제

three_second_rule:
  what_is_this: "한 문장. 3초 안에 답이 나와야 한다 (≤20 단어, 금지어 없음)"
  # 예: "교사가 강의 슬라이드를 5분에 만드는 AI 도구"
  # 실패 예: "차세대 AI 기반 교육 콘텐츠 플랫폼" ← 의미 0

scan_test:
  if_user_only_reads_headlines: "핵심 가치를 잡을 수 있는가?"
  required_headlines: 3

next_action:
  primary_cta: "<단 1개 CTA 문구>"      # craft-lint: != null + ≤ 6 단어
  secondary_cta: null                   # 처음엔 None. 2개 이상이면 fail
  placement: "0.05초 룰 — fold 안"

social_proof:
  type: "logo_strip | testimonial | usage_number"
  evidence: "<구체 데이터>"              # 예: "26M ALTools 사용자"
  position: "fold 직후"

emotional_tone:
  hero_image_face: "smiling | neutral | candid"
  rationale: "<왜 이 표정이 적합한가>"

hierarchy_rules:
  max_elements_above_fold: 7
  max_type_scale_per_screen: 4
  color_ratio: [60, 30, 10]              # 합 100 강제 (craft-lint 검증)
  whitespace_to_content_min: 0.4
  cta_count_above_fold: 1                # 영상 5번 — 1 강제

motion_language:
  hover_transition_ms: 200
  page_transition_easing: "cubic-bezier(0.4, 0, 0.2, 1)"
  scroll_reveal: "stagger 80ms"

forbidden:
  - "차세대, 혁신, 솔루션 같은 추상명사"
  - "기능 나열 (이 단계에선 결과만)"
  - "fold 안에 4개 이상의 element"
  - "Inter / Roboto / Arial / system-ui 폰트 (generic AI aesthetics)"

analytics_endpoint: "<PostHog/Plausible/GA4 URL>"   # track/respect-checkpoint β 게이트
```

---

## Trigger Gate

### Use This Skill When
- 새 화면 디자인 시작 (라우팅 추가 직전)
- 기존 화면 리디자인 — RESPECT.md 갱신
- 사용자 인터페이스가 있는 LLM 에이전트의 PRD Section 11 보강 (forge/prd 라우팅)

### Route to Other Skills When
- 표준 토큰 (색·폰트·간격) 정의 → Google DESIGN.md (`npx @google/design.md`)
- 픽셀 분석 (fold density / contrast) → `craft/hierarchy-rules` (Playwright)
- ship 직전 게이트 → `track/respect-checkpoint` (α/β/γ 매트릭스)

### Boundary Checks
- DESIGN.md 부재 시 → "먼저 `npx @google/design.md init` 권유"
- 백엔드 only 에이전트 → "RESPECT.md 불필요, PRD Section 11 N/A 표기"
- forbidden 패턴 (차세대·혁신·솔루션) 자동 정규식 검증

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| 화면 이름 / feature | $ARGUMENTS | 사용자 인터뷰 |
| PRD (있으면) | `docs/PRD.md` | Section 1-3 (페르소나·JTBD) 인용 |
| DESIGN.md | `.design/DESIGN.md` | cross-ref 강제 |
| 기존 RESPECT.md (있으면) | `.design/RESPECT.md` | 갱신 모드 |

---

## Instructions

You are writing RESPECT.md for: **$ARGUMENTS**

**Step 1 — Interview: 3초 룰 도출**
- "이 화면을 처음 본 사람이 3초 안에 알아야 할 한 문장은?"
- 답이 추상명사 포함 → "차세대 → 무엇을 5분만에? 같이 구체화" 재질문
- 단어 수 ≤ 20 + 금지어 없음 통과 시 commit

**Step 2 — Interview: 다음 행동**
- "이 화면에서 사용자가 해야 할 단 하나의 행동은?"
- primary CTA 6 단어 이내. secondary 는 처음엔 None.
- "2개 이상 두고 싶다" → 영상 5번 원칙 강조 + 거부

**Step 3 — Interview: 신뢰 신호**
- "social proof — 로고/숫자/후기 중 어떤 것을 fold 직후 보여줄지?"
- 구체 데이터 인용 (예: "사용자 수 26M") 없으면 fail loud

**Step 4 — Interview: 정서 톤**
- hero image 의 인물 표정 (있으면) / 톤 (warm/serious/playful)
- rationale 한 줄

**Step 5 — Hierarchy rules (default + 사용자 override)**
- max_elements_above_fold (default 7) / max_type_scale (4) / color_ratio (60/30/10) / whitespace_ratio (0.4) / cta_count (1)
- 사용자가 override 시 reason 한 줄 강제

**Step 6 — Motion language**
- hover transition / page transition easing / scroll reveal 명세

**Step 7 — Forbidden list (default + 추가)**
- default 4 항목 + 화면별 추가 (예: "어두운 그라데이션 금지")

**Step 8 — analytics_endpoint**
- PostHog/Plausible/GA4 URL — 없으면 `null` (β 게이트 skip 됨)

**Step 9 — RESPECT.md 저장 + craft-lint 검증**
- `.design/RESPECT.md` write
- 즉시 `python3 scripts/validate-craft-lint.py` 실행 → exit 0 확인
- 통과 시 "ship 전 craft-lint + respect-checkpoint 권유" 안내

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| three_second_rule 에 추상명사 | 정규식 매칭 (차세대/혁신/솔루션) | 재인터뷰 강제 |
| 단어 수 > 20 | split count | "3초에 못 읽음 — 한 문장 줄여주세요" |
| secondary_cta 명시 | yaml 검증 | "처음엔 1개만 — 영상 5번 원칙" 거부 |
| color_ratio 합 ≠ 100 | sum() | 자동 정규화 + 사용자 확인 |
| cta_count_above_fold > 1 | yaml 검증 | "영상 5번 원칙 위반" 경고 + force override 허용 |
| DESIGN.md 없음 | file not found | `npx @google/design.md init` 권유 |

---

## Quality Gate

- [ ] 5 필수 섹션 모두 작성 (three_second / next_action / social_proof / hierarchy / motion)
- [ ] three_second_rule.what_is_this ≤ 20 단어 + 금지어 0
- [ ] next_action.primary_cta 1개 + secondary null
- [ ] hierarchy_rules.color_ratio 합 = 100
- [ ] hierarchy_rules.cta_count_above_fold = 1 (force override 시 audit log)
- [ ] references_design_md 명시 (DESIGN.md cross-ref)
- [ ] `validate-craft-lint.py` exit 0 통과

---

## Examples

### Good Example
**입력:** "habix-landing"

**기대 RESPECT.md:**
```yaml
screen: "habix.ai 랜딩"
references_design_md: ./DESIGN.md

three_second_rule:
  what_is_this: "AI 가 매일 1개 새 습관을 3분 코칭하는 PM 도구"
  # 12 단어, 금지어 0 ✅

next_action:
  primary_cta: "무료로 시작"             # 3 단어 ✅
  secondary_cta: null                    # ✅
  placement: "fold 안"

social_proof:
  type: "usage_number"
  evidence: "26M ALTools 사용자가 만든 팀"
  position: "fold 직후"
...
```

### Bad Example
**입력:** "차세대 AI 솔루션 랜딩"

**왜 나쁜가:** 입력 자체에 추상명사 — 인터뷰 단계에서 reject

**기대 동작:** "차세대/솔루션은 의미 0 — 무엇을 풀어주는 도구인지 한 문장 재요청" 거부

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Schema Reference
!`cat references/respect-schema.yaml 2>/dev/null || echo ""`

### Forbidden Word Dictionary
!`cat references/forbidden-words.md 2>/dev/null || echo ""`
