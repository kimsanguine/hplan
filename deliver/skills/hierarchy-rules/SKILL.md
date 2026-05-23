---
name: hierarchy-rules
description: "Alias for ui-validate --check hierarchy — Playwright DOM saliency analysis for visual hierarchy compliance (WCAG AA). Deprecated: use ui-validate --check hierarchy directly."
argument-hint: "[--url URL]"
alias_for: "ui-validate --check hierarchy"
allowed-tools: ["Read", "Write", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `ui-validate --check hierarchy` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: Playwright + DOM saliency 분석으로 시각 계층 구조를 검증합니다.
WCAG AA 기준, 텍스트 대비·포커스 순서·헤딩 레벨 점검 포함.
기존 `hierarchy-rules` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `ui-validate --check hierarchy $ARGUMENTS` 와 동일하게 동작합니다.
`ui-validate --check hierarchy` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
