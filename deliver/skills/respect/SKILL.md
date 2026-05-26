---
name: respect
description: "2-mode UI respect skill — brief (generate RESPECT.md design brief before coding) and checkpoint (final pre-ship gate enforcing user-respect via α/β/γ gate matrix). Use --mode brief when starting any UI screen; use --mode checkpoint before shipping. RESPECT.md absence blocks craft-lint (exit 2)."
argument-hint: "[screen-name] [--mode brief|checkpoint]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

**--mode brief:**
- 화면 코딩 전에 RESPECT.md 생성 — "respect before design" 원칙
- 5개 핵심 의도 commit: three_second_rule / next_action / social_proof / hierarchy_rules / motion_language
- 결정론 검증 가능한 YAML 스키마 (craft-lint가 픽셀 분석 없이 정합성 검증)
- DESIGN.md (Google 표준 토큰)와 cross-reference 강제

**--mode checkpoint:**
- 화면 ship 직전 사용자 존중 게이트 mechanical enforcement
- AI 책임: 화면 분류 (screen_type / traffic_level) — Rule 5 허용 영역
- 결정론 책임: 분류 결과 → α/β/γ 게이트 조합 lookup (정책은 사용자 yaml)
- 게이트별 실행은 각각 다른 메커니즘 (인간 / 데이터 / 합성)

---

## Trigger Gate

### Use This Skill When
- 새 화면 디자인 시작 (라우팅 추가 직전) → `--mode brief`
- 기존 화면 리디자인 — RESPECT.md 갱신 → `--mode brief`
- 사용자 인터페이스가 있는 LLM 에이전트의 PRD Section 11 보강 → `--mode brief`
- 화면 ship 직전 (deploy / release 이전 마지막 게이트) → `--mode checkpoint`
- craft-lint 통과 후 (디자인 정합성 확인 후 사용자 존중 게이트) → `--mode checkpoint`

### Route to Other Skills When
- 표준 토큰 (색·폰트·간격) 정의 → Google DESIGN.md (`npx @google/design.md`)
- 픽셀 분석 (fold density / contrast) → `craft/hierarchy-rules` (Playwright)
- 디자인 토큰·hierarchy 위반 → `craft/craft-lint` 또는 `craft/hierarchy-rules`
- 게이트 통과의 자연어 보고 → `track/progress-report`

### Boundary Checks
- DESIGN.md 부재 시 → "먼저 `npx @google/design.md init` 권유"
- 백엔드 only 에이전트 → "RESPECT.md 불필요, PRD Section 11 N/A 표기"
- 매트릭스 yaml 누락 → default 매트릭스 + warning
- β 게이트 + analytics_endpoint 부재 → β 자동 skip + warning

---

## Mode: brief

### RESPECT.md 스키마 (필수 5 섹션)

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
  cta_count_above_fold: 1                # 1 강제

motion_language:
  hover_transition_ms: 200
  page_transition_easing: "cubic-bezier(0.4, 0, 0.2, 1)"
  scroll_reveal: "stagger 80ms"

forbidden:
  - "차세대, 혁신, 솔루션 같은 추상명사"
  - "기능 나열 (이 단계에선 결과만)"
  - "fold 안에 4개 이상의 element"
  - "Inter / Roboto / Arial / system-ui 폰트 (generic AI aesthetics)"

analytics_endpoint: "<PostHog/Plausible/GA4 URL>"   # checkpoint β 게이트
```

### Instructions (brief mode)

You are writing RESPECT.md for: **$ARGUMENTS**

**Step 1 — Interview: 3초 룰 도출**
- "이 화면을 처음 본 사람이 3초 안에 알아야 할 한 문장은?"
- 답이 추상명사 포함 → 재질문
- 단어 수 ≤ 20 + 금지어 없음 통과 시 commit

**Step 2 — Interview: 다음 행동**
- "이 화면에서 사용자가 해야 할 단 하나의 행동은?"
- primary CTA 6 단어 이내. secondary는 처음엔 None.
- "2개 이상 두고 싶다" → 영상 5번 원칙 강조 + 거부

**Step 3 — Interview: 신뢰 신호**
- "social proof — 로고/숫자/후기 중 어떤 것을 fold 직후 보여줄지?"
- 구체 데이터 인용 없으면 fail loud

**Step 4 — Interview: 정서 톤**
- hero image의 인물 표정 (있으면) / 톤 (warm/serious/playful)
- rationale 한 줄

**Step 5 — Hierarchy rules (default + 사용자 override)**
- max_elements_above_fold (default 7) / max_type_scale (4) / color_ratio (60/30/10) / whitespace_ratio (0.4) / cta_count (1)
- 사용자가 override 시 reason 한 줄 강제

**Step 6 — Motion language**
- hover transition / page transition easing / scroll reveal 명세

**Step 7 — Forbidden list (default + 추가)**
- default 4 항목 + 화면별 추가

**Step 8 — analytics_endpoint**
- PostHog/Plausible/GA4 URL — 없으면 `null` (β 게이트 skip 됨)

**Step 9 — RESPECT.md 저장 + craft-lint 검증**
- `.design/RESPECT.md` write
- 즉시 `python3 scripts/validate-craft-lint.py` 실행 → exit 0 확인
- 통과 시 "ship 전 craft-lint + `--mode checkpoint` 권유" 안내

---

## Mode: checkpoint

### 3 게이트 정의

| 게이트 | 메커니즘 | 실행 시점 | 신뢰도 | 비용 |
|---|---|---|---|---|
| **α — 인간 7초 체크리스트** | 사용자 직접 답 + 응답시간 측정 | ship 직전 (동기) | 본인 의식적 검수 | 화면당 ~30초 |
| **β — 72h 데이터 게이트** | PostHog/Plausible/GA4 metrics (scroll≥40%, CTR≥2%, bounce≤60%) | ship 후 72h (비동기) | 객관 데이터 100% | 인프라 셋업 1회 |
| **γ — 합성 시뮬레이션** | Playwright + saliency map + WCAG AA + craft/hierarchy-rules 재사용 | ship 직전 (자동) | 60-70% (실제 인지 ≠ saliency) | 자동, 무료 |

> γ가 가장 자동 & 0 비용이지만 신뢰도 중간 — α + γ 조합이 default 권고.

### Rule 5 회피 메커니즘

```
[입력: 화면 ID]
   ↓
[AI 분류 — Rule 5 허용]
   - screen_type: landing | feature_detail | dashboard | onboarding | settings
   - traffic_level: high_traffic | low_traffic
   ↓
[결정론 lookup — 매트릭스 yaml]
   gate_matrix[(screen_type, traffic_level)] → [α, β, γ 중 선택 조합]
   ↓
[게이트별 실행]
   - α: clickable checklist + 응답시간 측정 (인간 동기)
   - β: analytics endpoint 등록 + cron 72h 점검 (자동 비동기)
   - γ: Playwright 호출 + saliency map (자동 동기)
   ↓
[통과 → ship 허용 / 실패 → 차단 + fix 권유]
```

### 기본 매트릭스 (사용자 override 가능)

```yaml
# references/gate-matrix.yaml
gate_matrix:
  landing:
    high_traffic: [alpha, beta, gamma]    # 풀 게이트 (첫인상 + 트래픽 충분)
    low_traffic:  [alpha, gamma]          # 데이터 안 모임 → beta 무의미
  feature_detail:
    high_traffic: [alpha, beta]
    low_traffic:  [alpha]
  dashboard:
    any:          [gamma]                  # 반복 사용 = 첫인상 비중 낮음
  onboarding:
    any:          [alpha, gamma]
  settings:
    any:          [gamma]                  # 자동만, 의식적 검수 불필요
```

### Instructions (checkpoint mode)

You are running respect --mode checkpoint for: **$ARGUMENTS**

**Step 1 — 화면 메타데이터 로드 + RESPECT.md 검증**
- RESPECT.md 없으면 fail loud → `respect --mode brief` 먼저 권유

**Step 2 — AI 분류 (Rule 5 분류 영역)**
- screen_type: landing/feature_detail/dashboard/onboarding/settings 중 분류
- traffic_level: high/low (RESPECT.md analytics_endpoint 기반 estimated DAU 사용)
- 분류 confidence 낮으면 사용자에게 확인 1회

**Step 3 — 결정론 매트릭스 lookup**
- gate_matrix[(screen_type, traffic_level)] → 게이트 조합 [α/β/γ 부분집합]

**Step 4 — α 게이트 실행 (선택됐을 때)**
- 3 질문 출력 (RESPECT.md three_second_rule / next_action / social_proof 인용):
  - "이 화면이 무엇인지 3초에 알 수 있는가? (Y/N)"
  - "primary CTA가 fold 안에 1개 명확한가? (Y/N)"
  - "social proof가 fold 안에 있는가? (Y/N)"
- 응답 ts 측정 — 7초 미만 시 warning
- 1개라도 N → 실패 → fix 권유

**Step 5 — β 게이트 실행 (선택됐을 때)**
- RESPECT.md analytics_endpoint 등록 + cron 72h 후 점검 스케줄
- ship 자체는 통과 (비동기 게이트)
- 72h 후 metrics 미달 시 GitHub/Linear issue 자동 생성

**Step 6 — γ 게이트 실행 (선택됐을 때)**
- Playwright 호출 → 화면 캡처
- saliency map 계산 (CSS contrast/size/position 가중치)
- WCAG AA contrast 검증
- craft/hierarchy-rules (fold density / color_ratio / cta count) 재사용
- 미달 항목 → 실패

**Step 7 — 최종 판정 + ship 허용/차단**
- 선택된 모든 게이트 pass → ship 허용 + progress-report trigger (phase_transition)
- 1개라도 fail → ship 차단 + fix 권유 (β는 차단 안 함, 사후 issue만)

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| three_second_rule에 추상명사 | 정규식 매칭 (차세대/혁신/솔루션) | 재인터뷰 강제 |
| 단어 수 > 20 | split count | "3초에 못 읽음 — 한 문장 줄여주세요" |
| secondary_cta 명시 | yaml 검증 | "처음엔 1개만" 거부 |
| color_ratio 합 ≠ 100 | sum() | 자동 정규화 + 사용자 확인 |
| DESIGN.md 없음 (brief) | file not found | `npx @google/design.md init` 권유 |
| RESPECT.md 없음 (checkpoint) | file not found | fail loud → `--mode brief` 먼저 권유 |
| AI 분류 confidence 낮음 | LLM 응답 "unsure" | conservative = (landing, high_traffic) 가정 + 사용자 확인 |
| α 응답시간 < 7s × 3 회 | timing logs | "thoughtless click pattern" — 인간 검수 신뢰도 ↓ 경고 |
| β analytics_endpoint 없음 | RESPECT.md 누락 | β 자동 skip + warning ("ship 후 검증 불가") |
| γ Playwright 미설치 | which playwright | γ 자동 skip + warning + α 가중치 ↑ |

---

## Quality Gate

**brief mode:**
- [ ] 5 필수 섹션 모두 작성 (three_second / next_action / social_proof / hierarchy / motion)
- [ ] three_second_rule.what_is_this ≤ 20 단어 + 금지어 0
- [ ] next_action.primary_cta 1개 + secondary null
- [ ] hierarchy_rules.color_ratio 합 = 100
- [ ] hierarchy_rules.cta_count_above_fold = 1 (force override 시 audit log)
- [ ] references_design_md 명시 (DESIGN.md cross-ref)
- [ ] `validate-craft-lint.py` exit 0 통과

**checkpoint mode:**
- [ ] AI 분류는 2 라벨만 (screen_type, traffic_level) — 그 외 결정 LLM 사용 0
- [ ] 게이트 조합은 yaml lookup (정책은 인간이 yaml 편집)
- [ ] α 응답시간 측정 + 7초 미만 warning
- [ ] β analytics_endpoint 확인 + 비동기 cron 등록
- [ ] γ Playwright + craft/hierarchy-rules 재사용
- [ ] 모든 게이트 통과만 ship 허용 + progress-report trigger 발화

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Schema Reference
!`cat references/respect-schema.yaml 2>/dev/null || echo ""`

### Gate Matrix Default
!`cat references/gate-matrix.yaml 2>/dev/null || echo ""`
