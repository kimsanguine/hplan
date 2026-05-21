# Bad Example — Premortem

## 사용자 요청

"배포 전에 리스크 회의를 한 번만 열자. 대충 어떤 문제가 있을 수 있을지 얘기하면 되겠지."

## 거절 이유

- Pre-mortem exercise 미실시 (구조화된 "3개월 후 실패" 질문 없음)
- FMEA 방법론 미적용 (Severity, Probability, Detection, RPN 계산 없음)
- 정성적 논의로 끝남 (정량화된 위험도 평가 부재)
- Prevention 전략 설계 미실행 (대응 방법 불명확)
- 모니터링 알림 미설정 (조용한 실패 감지 불가)
- 액션 아이템 Owner/Deadline 없음 (실행 추적 불가)

## 올바른 라우팅

**measure/skills/premortem** (구조화된 FMEA와 정량화된 위험도 평가 필요)

또는 초기 단계라면:
- 리스크 논의 후 **premortem**으로 전환하여 FMEA 테이블 작성

## 수정 방향

"배포 전에 FMEA로 실패 모드를 분석해주고, RPN 상위 10개를 우선순위화해서 각각에 대한 Prevention 전략을 설계해줄 수 있을까?"
