# Good Example — Reliability

## 사용자 요청

"우리 고객 지원 에이전트의 신뢰성이 떨어진 것 같아. 지난 30일 데이터를 기반으로 현재 신뢰성 기준선을 측정하고, 실패 패턴을 분류해서 각 패턴별 safeguard를 설계해줄 수 있어? 목표는 99% 신뢰성이야."

## 승인 이유

- 신뢰성 기준선 측정 명시 (Success Rate, Error Rate)
- 실패 패턴 분류 요청 (분석 기반 접근)
- Safeguard 설계 요구 (구체적 개선 방안)
- 신뢰성 목표 명시 (99% — High 수준)

## 예상 처리

1. 30일 운영 데이터로 기준선 수집 (총 실행, 성공, 실패, 부분 성공)
2. 실패를 5가지 카테고리(Input/Model/Tool/Logic/Output)로 분류
3. 각 카테고리별 패턴 분석 (Frequency, Root Cause, Impact, Detection, Recovery)
4. 높은 영향도 실패 각각에 대해 Safeguard 유형 선택 (Validation/Gate/Retry/Fallback/Circuit Breaker)
5. 신뢰성 목표 수준 설정 (현재 95% → 99% 달성)
6. 로드맵 수립 (Quick Wins, Medium Term, Long Term)
7. 각 Safeguard의 구현 복잡도 및 비용 영향 평가
