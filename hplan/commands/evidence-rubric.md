---
description: "hplan/evidence-rubric 스킬 wrapper — 8축 100점 evidence 루브릭 점수화 (ICP·통증·우회법·반복도·경제적 손실·전환 트리거·MVP 좁힘·획득 경로)"
argument-hint: "[idea or product name]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /evidence-rubric — 8축 100점 Evidence Gate

Running for: **$ARGUMENTS**

이 커맨드는 `hplan/evidence-rubric` 스킬을 즉시 호출합니다.

## 호출 흐름

1. `hplan/evidence-rubric` 스킬을 `$ARGUMENTS`로 invoke.
2. 스킬이 8축(ICP · 최근 통증 이벤트 · 현재 우회법 · 반복도 · 경제적 손실 · 전환 트리거 · MVP 좁힘 · 첫 5명 획득 경로) 100점 만점 채점.
3. 결과:
   - 75점 이상 → BUILD 권장
   - 55~74점 → INTERVIEW 권장
   - 35~54점 → HOLD 권장
   - 35점 미만 → PIVOT 권장

## 후속

- 점수가 INTERVIEW 이상이면 `/interview-synthesis import` 워크플로우 진입.
- BUILD면 `/harness-build`로 PRD 작성.
