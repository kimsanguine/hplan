# Good Example — Premortem

## 사용자 요청

"다음 주에 멀티에이전트 오케스트레이터를 프로덕션에 배포하는데, FMEA로 실패 모드를 사전 분석해줘. 심각도, 발생 가능성, RPN까지 계산하고 Prevention 전략도 함께."

## 승인 이유

- 배포 전 체계적 실패 분석 필요 (premortem의 핵심 트리거)
- FMEA 방법론 명시 (정확한 스킬 일치)
- 위험도 정량화 요청 (RPN 계산)

## 예상 처리

1. Pre-mortem exercise 실행 ("3개월 후 이 시스템이 완전히 실패했다면?")
2. 도출된 실패 모드를 FMEA 테이블로 구성 (Severity, Probability, Detection, RPN)
3. RPN 상위 10-15개 모드 우선순위화
4. 각 고위험 모드(RPN > 100)에 대해 Prevention/Detection/Response/Recovery 전략 설계
5. 모니터링 트리거 정의 (Yellow alert 조사 수준, Red alert 즉시 대응)
6. 액션 아이템 목록화 (Owner, Deadline, 상태 추적)
7. 분기별 재premortem 일정 수립
