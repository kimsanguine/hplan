# Bad Example — KPI

## 사용자 요청

"KPI는 대충 정해도 되겠지. 에이전트가 잘 돌아가는 것 같으니까."

## 거절 이유

- KPI가 정의되지 않음 (어떤 메트릭을 추적할 것인가?)
- 운영 메트릭과 비즈니스 메트릭 구분 없음
- Formula 미명시 (팀마다 Accuracy를 다르게 계산할 수 있음)
- Alert threshold 없음 (문제 상황을 어떻게 감지할 것인가?)
- 리뷰 일정 없음 (주기적 관리 불가)
- "잘 돌아가는 것 같다"는 주관적 판단 (정량화 필요)

## 올바른 라우팅

**measure/skills/kpi** (명확한 메트릭 정의 및 대시보드 설계)

## 수정 방향

"에이전트의 핵심 KPI를 정의해줄 수 있어? Accuracy, Latency, Cost per Execution 같은 운영 메트릭과 Time Saved, User Satisfaction 같은 비즈니스 메트릭을 포함해서. Alert threshold도 설정해주고 주간 리뷰 일정을 잡아줘."
