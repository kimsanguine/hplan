---
name: infographic-gif-creator
description: "Alias for media-asset --type infographic — HTML/CSS to GIF/MP4 infographic generation pipeline. Deprecated: use media-asset --type infographic directly."
argument-hint: "[--data PATH] [--format gif|mp4]"
alias_for: "media-asset --type infographic"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `media-asset --type infographic` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: HTML/CSS 기반으로 애니메이션 인포그래픽을 GIF 또는 MP4로 생성합니다.
데이터 주입 → HTML 렌더 → 캡처 → 영상 합성 파이프라인.
기존 `infographic-gif-creator` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `media-asset --type infographic $ARGUMENTS` 와 동일하게 동작합니다.
`media-asset --type infographic` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
