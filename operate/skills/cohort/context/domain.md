# Domain Context — Cohort

## 1) Domain Scope

**에이전트 코호트(버전, 기간, 세그먼트)별 성능 추적 및 비교**

- 시간 기반 코호트: 에이전트 버전별 배포 시점으로 추적
- 세그먼트 기반 코호트: 사용자 그룹/유형별 성능 비교
- TK 기반 코호트: 축적된 TK 수준에 따른 성능 변화
- Week-over-Week 메트릭 비교 (초기 vs 4주 vs 12주)
- Retention curve 분석 (사용자의 재사용 패턴)
- Degradation detection (급락/점진적 하락/계절성)

## 2) Primary Users

- **PM/프로덕션 오너**: 버전 배포 후 장기 성능 추적
- **데이터 분석가**: 코호트 메트릭 계산 및 리포팅
- **에이전트 팀**: 성능 저하 원인 분석 (데이터 드리프트? 프롬프트 노후화?)
- **리더**: 배포 결정 및 롤백 판단

## 3) Required Inputs

- **에이전트 명 및 배포 이력**: 버전, 배포 시점, 주요 변경사항
- **운영 메트릭 데이터**: Accuracy, Latency, Cost, Retention, Escalation Rate (최소 4주 이상)
- **사용자 세그먼트 정보** (있다면): 내부/외부, 사용 빈도, 사용자 특성
- **외부 변수**: 입력 데이터 분포 변화, 사용 패턴 변화 등

## 4) Output Contract

- **코호트 정의 명시**: 시간/세그먼트/TK 기반 중 어느 것을 사용하는지
- **메트릭 추적 매트릭스**: 각 코호트별 Week 0/1/2/4/8/12 메트릭
- **Retention curve**: 각 코호트의 재사용률 시간별 추이
- **Degradation 패턴 분류**: Sudden Drop/Gradual Decline/Seasonal/Cohort-specific
- **의사결정 및 액션 아이템**: Improve/Maintain/Rollback 선택과 근거

## 5) Guardrails

- **일시적 변동 vs 진정한 저하 구분**: 1주 데이터는 노이즈 → 최소 4주 추세 필요
- **코호트 크기 충분성**: 샘플 < 100건이면 통계 신뢰도 낮음 → 기간 연장
- **외부 변수 통제**: 성능 변화의 원인이 에이전트인지 입력 데이터 변화인지 분리
- **과도한 최적화 방지**: Cohort A가 "나쁜" 성능이라고 해서 무조건 제거 X (원인 파악 필수)
- **계절성 인식**: 월초 사용량 증가를 "개선"으로 착각 X (정상 범위 설정)

## 6) Working Facts (TO BE UPDATED by reviewer)

- **코호트 크기 기준**: 최소 100건 이상 (샘플 통계학적 유의성)
- **추적 메트릭**: Task Accuracy, Response Time (P95), Token Cost/Task, User Retention, Escalation Rate 등
- **Week-over-Week 계산**: 코호트의 첫 1주, 4주, 12주 메트릭 수집
- **Retention 해석**: Week 1 < 40% (온보딩 문제), Week 4 < 20% (가치 미전달), Week 12 > 30% (건강)
- **Degradation 유형별 원인**: 급락(API 장애), 점진적(데이터 드리프트), 계절성(사용 패턴)

## 7) Fill-in Checklist

- [ ] 분석 대상 에이전트 및 코호트 정의(시간/세그먼트/TK) 확인
- [ ] 코호트별 배포 시점 또는 세그먼트 경계 명확화
- [ ] 추적할 메트릭 일관성 정의 (formula, data source, 수집 방법)
- [ ] 최소 4주(코호트당) 이상 데이터 수집
- [ ] 코호트별 샘플 크기 충분성 확인 (최소 100건)
- [ ] Week 0/1/2/4/8/12 메트릭 수집 및 비교
- [ ] Retention curve 그리기 및 해석
- [ ] Degradation 패턴 식별 (급락/점진적/계절성/코호트특정)
- [ ] 입력 데이터 분포 변화 분석 (외부 변수 통제)
- [ ] 의사결정(Improve/Maintain/Rollback) 및 액션 아이템 명문화
