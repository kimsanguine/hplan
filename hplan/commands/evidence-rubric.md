---
description: "Use when 제품 아이디어의 고객 증거를 8축 100점 루브릭으로 판정해야 합니다. hplan/evidence-rubric wrapper는 ICP·통증·우회법·반복도·경제적 손실·전환 트리거·MVP 좁힘·획득 경로를 점수화합니다."
argument-hint: "[idea or product name]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /evidence-rubric — 8축 100점 Evidence Gate

Running for: **$ARGUMENTS**

이 커맨드는 `hplan/evidence-rubric` 스킬을 즉시 호출합니다.

## Instructions

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

## Output Format

8축 점수와 총점, `BUILD` / `INTERVIEW` / `HOLD` / `PIVOT` 판정, 그리고 다음 검증 조치를 반환합니다.
