# Good Example — Agent A/B Test

## 사용자 요청

"새로운 시스템 프롬프트를 만들었는데, 지금 것보다 정말 나은지 확인하고 싶어. A/B 테스트를 설계해줄 수 있어? 통계적으로 유의한 수준으로 검증하면 좋겠어. 정확도(Primary metric)랑 응답 시간도 모니터링해줄 수 있어?"

## 승인 이유

- A/B 테스트 설계 명시 (Control vs Variant)
- Primary/Secondary 메트릭 정의
- 통계적 유의성 요구 (p-value 기반)
- 샘플 크기 및 기간 계산 필요

## 예상 처리

1. 가설 정의 ("새 프롬프트가 정확도를 5% 이상 개선")
2. Primary/Secondary/Guardrail 메트릭 설정
3. 필요 표본 크기 계산 (MDE 기반)
4. A/B 병렬 실행 계획 (동시 실행으로 시간대 편향 통제)
5. Rollback trigger 정의 (Guardrail 악화 시 즉시 중단)
6. 결과 분석 (p-value + 신뢰 구간 + 실무 유의성)
7. 의사결정 (Ship/Keep/Iterate/Investigate)
