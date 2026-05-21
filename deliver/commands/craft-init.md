---
description: "Initialize craft plugin for a new screen or feature — chain respect-brief (RESPECT.md 인터뷰 생성) → hierarchy-rules baseline measurement (RESPECT 의 hierarchy_rules 적용 확인) → motion-language scan (현재 코드 base motion 추출). Single entry point. Use when starting any new UI-bearing feature, or when adopting craft on an existing codebase for the first time."
argument-hint: "[screen-name or feature]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /craft-init — craft Plugin Bootstrap

Single entry point for setting up craft on a new screen. Chains 3 setup steps. Stops early if any fails.

## Instructions

You are initializing craft for: **$ARGUMENTS**

### Step 1 — respect-brief 인터뷰

`respect-brief` 호출 (자율 모드면 PRD 인용 + 사용자 인터뷰):
- three_second_rule (한 문장 ≤ 20 단어)
- next_action (primary CTA 1개)
- social_proof (구체 데이터)
- hierarchy_rules (60/30/10 / cta=1 / 7 elements)
- motion_language (hover 200ms / easing / scroll_reveal)

출력: `.design/RESPECT.md`

### Step 2 — DESIGN.md 확인

- 부재 → `npx @google/design.md init` 권유 (Google 표준)
- 존재 → cross-reference 검증 (validate-craft-lint.py)

### Step 3 — hierarchy-rules baseline 측정 (선택)

기존 화면 있으면 hierarchy-rules 호출:
- 5 룰 + WCAG AA 측정
- 현재 상태 → `.design/hierarchy-baseline.json` 저장
- RESPECT 명세와 차이 보고

### Step 4 — motion-language 스캔 (선택)

기존 코드 있으면 motion-language 호출:
- 현재 transition / easing 추출
- RESPECT 명세와 일치 여부

### Step 5 — 최종 보고

출력:
- RESPECT.md 작성 완료
- DESIGN.md 상태
- hierarchy baseline (있으면)
- motion drift (있으면)
- 다음 단계: 첫 UI 코드 작성 → /craft-lint 권유

## Output Format

```
VERDICT: READY / NEEDS_DESIGN_MD / DRIFT_FOUND

RESPECT.md:      <작성 완료 + 5 섹션 통과 / fix 필요>
DESIGN.md:       <있음 + cross-ref OK / 부재 + npx 권유>
hierarchy:       <baseline 측정 / 기존 화면 없음 skip>
motion:          <drift 0 / N drift>
Next:            <첫 UI 코드 작성 후 /craft-lint>
```

## Failure Handling

| 실패 | 대응 |
|---|---|
| RESPECT.md 인터뷰 중 추상명사 거부 | 재인터뷰 강제 |
| DESIGN.md 부재 | npx @google/design.md init 권유 |
| Playwright 미설치 (hierarchy/drift skip) | warning + 정적 검증만 |
