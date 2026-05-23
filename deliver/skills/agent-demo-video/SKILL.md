---
name: agent-demo-video
description: "Alias for media-asset --type video — Remotion React-based agent demo video generation pipeline. Deprecated: use media-asset --type video directly."
argument-hint: "[--scenes PATH] [--duration N]"
alias_for: "media-asset --type video"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `media-asset --type video` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: Remotion(React) 기반으로 에이전트 데모 영상을 생성합니다.
씬 정의 → 컴포넌트 렌더 → mp4 출력 파이프라인.
기존 `agent-demo-video` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `media-asset --type video $ARGUMENTS` 와 동일하게 동작합니다.
`media-asset --type video` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
