---
name: respect-checkpoint
description: "Final pre-ship gate that enforces user-respect (영상 5번 통찰 — '이 존중은 사람이 넣는 겁니다'). AI classifies the screen as (screen_type × traffic_level) — Rule 5 분류 허용 영역. Then a deterministic lookup matrix selects gate combination: α (human 7-second checklist, 응답시간 측정), β (72h post-ship data gate via analytics endpoint), γ (synthetic CV simulation via Playwright + saliency map, reuses craft/hierarchy-rules). The matrix is a YAML file the user owns — policy is human-controlled, not LLM."
argument-hint: "[screen-id or path/to/page]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

- 화면 ship 직전 **사용자 존중** 게이트 mechanical enforcement
- AI 책임: 화면 분류 (screen_type / traffic_level) — Rule 5 허용 영역
- 결정론 책임: 분류 결과 → α/β/γ 게이트 조합 lookup (정책은 사용자 yaml)
- 게이트별 실행은 각각 다른 메커니즘 (인간 / 데이터 / 합성)

---

## 3 게이트 정의

| 게이트 | 메커니즘 | 실행 시점 | 신뢰도 | 비용 |
|---|---|---|---|---|
| **α — 인간 7초 체크리스트** | 사용자 직접 답 + 응답시간 측정 | ship 직전 (동기) | 본인 의식적 검수 | 화면당 ~30초 |
| **β — 72h 데이터 게이트** | PostHog/Plausible/GA4 metrics (scroll≥40%, CTR≥2%, bounce≤60%) | ship 후 72h (비동기) | 객관 데이터 100% | 인프라 셋업 1회 |
| **γ — 합성 시뮬레이션** | Playwright + saliency map + WCAG AA + craft/hierarchy-rules 재사용 | ship 직전 (자동) | 60-70% (실제 인지 ≠ saliency) | 자동, 무료 |

> γ 가 가장 자동 & 0 비용이지만 신뢰도 중간 — α + γ 조합이 default 권고.

---

## Rule 5 회피 메커니즘

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

LLM 책임은 화면 라벨링 2건만. 게이트 선택은 yaml lookup. 게이트 실행은 각자 결정론.

---

## 기본 매트릭스 (사용자 override 가능)

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

---

## Trigger Gate

### Use This Skill When
- 화면 ship 직전 (deploy / release 이전 마지막 게이트)
- craft-lint 통과 후 (디자인 정합성 확인 후 사용자 존중 게이트)
- 사용자가 명시 호출 (`/respect-check <screen>`)

### Route to Other Skills When
- 디자인 토큰·hierarchy 위반 → `craft/craft-lint` 또는 `craft/hierarchy-rules`
- 게이트 통과의 자연어 보고 → `track/progress-report`
- gate 매트릭스가 자주 override 됨 → 패턴을 `learn/pm-engine` TK 후보로 promote

### Boundary Checks
- 매트릭스 yaml 누락 → default 매트릭스 + warning
- β 게이트 + analytics_endpoint 부재 → β 자동 skip + warning
- γ 게이트 + Playwright 미설치 → γ 자동 skip + warning + α 강조
- α 응답시간 < 7초 → "thoughtless click" warning (재검수 권유)

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| 화면 ID 또는 경로 | $ARGUMENTS | 화면 메타데이터 로드 |
| RESPECT.md | `.design/RESPECT.md` | analytics_endpoint / max_elements 등 참조 |
| gate-matrix.yaml | `references/gate-matrix.yaml` 또는 default | yaml lookup |
| α 응답 | 사용자 직접 입력 + ts 측정 | 결정론 |
| β 데이터 | analytics API | metrics 임계치 비교 |
| γ 시각 분석 | Playwright saliency | 픽셀 분석 |

---

## Instructions

You are running respect-checkpoint for: **$ARGUMENTS**

**Step 1 — 화면 메타데이터 로드 + RESPECT.md 검증**
- RESPECT.md 없으면 fail loud → `craft/respect-brief` 먼저 권유

**Step 2 — AI 분류 (Rule 5 분류 영역)**
- screen_type: landing/feature_detail/dashboard/onboarding/settings 중 분류
- traffic_level: high/low (RESPECT.md analytics_endpoint 기반 estimated DAU 사용)
- 분류 confidence 낮으면 사용자에게 확인 1회 (자율 모드면 conservative = high_traffic 가정)

**Step 3 — 결정론 매트릭스 lookup**
- gate_matrix[(screen_type, traffic_level)] → 게이트 조합 [α/β/γ 부분집합]

**Step 4 — α 게이트 실행 (선택됐을 때)**
- 3 질문 출력 (RESPECT.md three_second_rule / next_action / social_proof 인용):
  - "이 화면이 무엇인지 3초에 알 수 있는가? (Y/N)"
  - "primary CTA 가 fold 안에 1개 명확한가? (Y/N)"
  - "social proof 가 fold 안에 있는가? (Y/N)"
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
| RESPECT.md 없음 | file not found | fail loud → craft/respect-brief 권유 |
| AI 분류 confidence 낮음 | LLM 응답 "unsure" | conservative = (landing, high_traffic) 가정 + 사용자 확인 |
| α 응답시간 < 7s × 3 회 | timing logs | "thoughtless click pattern" — 인간 검수 신뢰도 ↓ 경고 |
| β analytics_endpoint 없음 | RESPECT.md 누락 | β 자동 skip + warning ("ship 후 검증 불가") |
| γ Playwright 미설치 | which playwright | γ 자동 skip + warning + α 가중치 ↑ |
| AI 분류 결과가 정책 변경 시도 | code review | 즉시 fail (LLM 은 분류만, gate 선택은 yaml lookup) |

---

## Quality Gate

- [ ] AI 분류는 2 라벨만 (screen_type, traffic_level) — 그 외 결정 LLM 사용 0
- [ ] 게이트 조합은 yaml lookup (정책은 인간이 yaml 편집)
- [ ] α 응답시간 측정 + 7초 미만 warning
- [ ] β analytics_endpoint 확인 + 비동기 cron 등록
- [ ] γ Playwright + craft/hierarchy-rules 재사용
- [ ] 모든 게이트 통과만 ship 허용 + progress-report trigger 발화

---

## Examples

### Good Example
**입력:** "habix-landing"

**기대 동작:**
1. AI 분류: (landing, high_traffic)
2. lookup: [alpha, beta, gamma]
3. α 실행 — 사용자 3 질문 답, 평균 12초 (>7초, 의식적 검수)
4. γ 실행 — Playwright, fold elements 6 (RESPECT max 7 ✅), color ratio 62/30/8 (60/30/10 허용 오차)
5. β 등록 — PostHog endpoint 등록, cron 2026-05-20 점검 예약
6. 결과: ship 허용 + progress-report trigger 발화

### Bad Example
**입력:** "settings-page"

**기대 동작:**
1. AI 분류: (settings, low_traffic)
2. lookup: [gamma] (자동만)
3. γ 실행 — WCAG AA contrast 1개 미달 (3.8:1, 필요 4.5:1)
4. ship 차단 + "contrast 조정 후 재시도" fix 권유

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Gate Matrix Default
!`cat references/gate-matrix.yaml 2>/dev/null || echo ""`

### α Checklist Template
!`cat references/alpha-checklist.md 2>/dev/null || echo ""`
