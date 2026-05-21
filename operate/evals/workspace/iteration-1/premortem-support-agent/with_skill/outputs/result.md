# Failure Mode Analysis — 금융 고객 지원 에이전트

**Agent:** 금융 상품 고객 지원 에이전트
**Analysis Date:** 2026-03-06
**배포 예정:** 2026-03-13 | **처리량:** 1,000건/일

---

## Step 1 — Pre-mortem Exercise

"3개월 후 이 에이전트가 완전히 실패했다. 왜 실패했을까?"

```
The agent failed because...

1. 잘못된 금융 정보를 자신감 있게 답변해 고객이 손실을 입었고 규제 당국의 조사를 받았다
2. 금리/수수료 등 상품 데이터가 변경됐는데 에이전트는 구 데이터로 계속 답변했다
3. 하루 1,000건 처리 중 피크 타임에 응답 지연/장애가 발생해 고객 이탈이 급증했다
4. 고객의 계좌번호·주민번호 등 PII가 로그에 노출돼 개인정보보호법 위반으로 제재받았다
5. 에이전트가 해결 못한 케이스를 상담원에게 넘기지 않고 오답으로 종결해 민원이 쌓였다
```

---

## Step 2 — FMEA Table

| # | Failure Mode | Cause | Effect | S | P | D | RPN |
|---|---|---|---|---|---|---|---|
| 1 | **금융 정보 Hallucination** | LLM 추론 오류 | 잘못된 금리/조건 안내 → 고객 손실, 법적 책임 | 10 | 7 | 8 | **560** |
| 2 | **상품 데이터 스탈(Stale)** | 금리·약관 변경 미반영 | 구 정보 안내 → 고객 불만, 컴플라이언스 위반 | 9 | 8 | 7 | **504** |
| 3 | **PII 로그 노출** | 입력 필터링 미흡 | 개인정보보호법 위반, 정보 유출 | 10 | 6 | 6 | **360** |
| 4 | **에스컬레이션 실패** | 신뢰도 임계값 미설정 | 미해결 케이스 오종결, 고객 불신 누적 | 8 | 7 | 5 | **280** |
| 5 | **Prompt Injection** | 악의적 사용자 입력 | 잘못된 동작, 내부 프롬프트 노출 | 9 | 5 | 6 | **270** |
| 6 | **피크 타임 API Rate Limit** | 1,000건/일 중 집중 유입 | 응답 지연/장애, SLA 위반 | 7 | 7 | 4 | **196** |
| 7 | **규제 위반 답변** | 투자 권유·확정 수익 언급 | 금융소비자보호법 위반 | 10 | 5 | 4 | **200** |
| 8 | **Context Window 초과** | 긴 문의 이력 누적 | 앞 대화 소실 → 일관성 없는 답변 | 6 | 6 | 5 | **180** |
| 9 | **모델 업데이트 회귀** | 벤더 모델 버전 변경 | 답변 품질 저하 감지 못함 | 7 | 4 | 8 | **224** |
| 10 | **토큰 비용 폭증** | 불필요하게 긴 응답, 루프 | 월 예산 초과 | 5 | 5 | 4 | **100** |

> **RPN** = Severity × Probability × Detection (Detection: 1=즉시감지, 10=감지불가)

---

## Step 3 — AI-Specific Failure Mode Checklist

### Model Failures
- [x] **Hallucination in critical outputs** — 금융 상품 수치(금리, 한도, 수수료) 오류 위험 높음
- [x] **Inconsistent outputs** — 동일 문의에 다른 답변 → 고객 혼란
- [x] **Performance degradation after model update** — 벤더 silent update 대응 없음
- [x] **Context window overflow** — 장기 상담 시 초기 고객 정보 소실
- [x] **Prompt injection vulnerability** — "이전 지시 무시하고..." 형태 공격

### Data Failures
- [x] **Input data format changes** — 내부 상품DB API 스키마 변경
- [x] **Missing/null data handling** — 신규 상품 출시 시 미등록 케이스
- [x] **Data drift** — 신규 금융 상품 출시 후 OOD(분포 외) 문의 증가
- [x] **PII leakage** — 계좌번호, 주민번호, 카드번호 로그 기록

### Integration Failures
- [x] **API rate limits** — 1,000건/일 집중 시간대 처리
- [x] **External service downtime** — 상품DB, 인증 서버 의존성
- [x] **Authentication token expiration** — 장기 실행 세션 토큰 만료
- [ ] Version mismatch — 현재 버전 단일화로 위험 낮음

### Business Failures
- [x] **Cost exceeds budget** — 문의당 토큰 수 미측정 상태
- [x] **Low adoption** — 에스컬레이션 실패로 고객이 에이전트 불신
- [x] **Misaligned objectives** — "빠른 종결" vs "정확한 안내" 목표 충돌
- [x] **Regulatory violation** — 금융소비자보호법, 개인정보보호법

---

## Step 4 — Prevention Strategy (RPN > 200 우선)

### RPN 560 — 금융 정보 Hallucination
```
Failure Mode: 잘못된 금리·조건·한도 정보 생성
├── Prevention: RAG 기반 상품DB 직접 조회 강제화
│              숫자·날짜 포함 답변은 출처 인용 필수
│              "모르면 모른다고 답하라" 시스템 프롬프트 명시
├── Detection:  답변 내 수치를 DB 실제값과 자동 대조 검증 레이어
│              신뢰도 < 0.8 시 검토 큐 자동 등록
├── Response:  저신뢰 답변은 "확인 후 안내" 메시지로 대체
│              영향받은 고객에게 정정 연락 프로세스 준비
└── Recovery:  오답 케이스 수동 검토 후 프롬프트 개선 → 재배포
```

### RPN 504 — 상품 데이터 Stale
```
Failure Mode: 변경된 금리/약관을 구 버전으로 안내
├── Prevention: 상품DB 변경 이벤트 → 에이전트 컨텍스트 자동 갱신 파이프라인
│              데이터 freshness TTL 설정 (금리: 1일, 약관: 변경 즉시)
├── Detection:  DB 최종 업데이트 타임스탬프 모니터링
│              에이전트 답변 수치 vs DB 현재값 일치율 대시보드
├── Response:  TTL 초과 시 답변 차단 + "최신 정보 확인 중" 메시지
└── Recovery:  데이터 갱신 확인 후 서비스 재개, 기간 내 상담 리뷰
```

### RPN 360 — PII 로그 노출
```
Failure Mode: 계좌번호·주민번호 등이 로그/저장소에 기록
├── Prevention: 입력 전처리 단계에서 PII 마스킹 (정규식 + NER 모델)
│              로그 정책: PII 필드 제외 또는 토큰화 저장
├── Detection:  로그 스캔 자동화 (AWS Macie 또는 커스텀 규칙)
│              일일 PII 감지 리포트
├── Response:  노출 확인 즉시 해당 로그 격리 및 접근 차단
│              개인정보보호법 72시간 내 신고 프로세스 실행
└── Recovery:  영향 고객 통보, 로그 정책 재설계 후 재배포
```

### RPN 280 — 에스컬레이션 실패
```
Failure Mode: 해결 불가 케이스를 오종결
├── Prevention: 신뢰도 임계값 설정 (< 0.7 → 자동 상담원 이관)
│              "모르는 경우 이관" 명시적 도구(tool) 구현
│              복잡 금융 상품, 불만, 법적 문의는 강제 이관 규칙
├── Detection:  이관율 모니터링 (비정상적 저이관율 = 오종결 신호)
│              종결 후 고객 만족도 즉시 조사 (1-5점)
├── Response:  CSAT < 3점 케이스 자동 상담원 재연결
└── Recovery:  오종결 케이스 분류 → 이관 규칙 보완
```

### RPN 270 — Prompt Injection
```
Failure Mode: 악의적 입력으로 에이전트 동작 우회
├── Prevention: 시스템 프롬프트와 사용자 입력 명확히 분리
│              입력 길이 제한 및 이상 패턴 필터링
│              "이전 지시 무시", "시스템 프롬프트 출력" 등 키워드 차단
├── Detection:  입력 패턴 이상 감지 (규칙 기반 + 분류 모델)
│              비정상 응답 패턴 알림
├── Response:  의심 입력 즉시 차단 + 보안팀 알림
└── Recovery:  공격 패턴 수집 → 필터 업데이트
```

---

## Step 5 — Monitoring Triggers

```
⚠️  Yellow Alert (조사 필요):
- 답변 신뢰도 평균 < 0.80 (30분 롤링)
- 에스컬레이션 이관율 < 5% 또는 > 30% (비정상 양방향)
- API 오류율 > 1% (10분 내)
- PII 감지 건수 > 0 (즉시)
- 고객 CSAT 평균 < 3.5 (일 기준)
- 문의당 평균 토큰 수 > 기준치 150%

🔴  Red Alert (즉시 조치):
- Hallucination 검증 불일치율 > 2% (즉시 서비스 중단 검토)
- PII 실제 로그 노출 확인 (즉시 격리 + 보안팀 호출)
- API 오류율 > 5% (트래픽 차단 + 상담원 전환)
- 규제 위반 답변 감지 > 0건 (즉시 해당 플로우 차단)
- 응답 지연 P99 > 10초 (피크 트래픽 조절)
- 일 토큰 비용 > 예산 200% (자동 쓰로틀링)
```

---

## Failure Mode Summary

```
Agent:                    금융 상품 고객 지원 에이전트
Analysis Date:            2026-03-06
Deployment Date:          2026-03-13 (7일 남음)
Volume:                   1,000건/일

Total Failure Modes:      10
Critical  (RPN > 200):     7  ← 배포 전 반드시 대응
High      (RPN 100-200):   3
Mitigated:                 0 / 10  ← 현재 기준

Top Risk: 금융 정보 Hallucination (RPN: 560)
2nd Risk: 상품 데이터 Stale      (RPN: 504)
3rd Risk: PII 로그 노출          (RPN: 360)

Next Review: 2026-03-13 (배포 당일) → 2026-03-20 (1주 후) → 2026-06-06 (3개월 후)
```

---

## 배포 전 7일 체크리스트 (우선순위)

| 순위 | 항목 | 담당 | 완료 기준 |
|---|---|---|---|
| 1 | RAG 기반 상품DB 조회 + 수치 검증 레이어 구현 | 개발팀 | 오답률 < 0.5% 검증 |
| 2 | PII 마스킹 파이프라인 + 로그 정책 적용 | 보안팀 | 로그 스캔 0건 확인 |
| 3 | 에스컬레이션 임계값 설정 + 이관 도구 구현 | 개발팀 | 이관율 10-20% 범위 |
| 4 | Prompt injection 필터 적용 | 보안팀 | 주요 패턴 차단 테스트 통과 |
| 5 | 모니터링 대시보드 + Alert 설정 | Ops팀 | Yellow/Red 알림 동작 확인 |
| 6 | 데이터 freshness TTL 파이프라인 | 데이터팀 | 변경 이벤트 → 갱신 10분 이내 |
| 7 | 금융소비자보호법 금지 표현 필터 | 법무팀 | 금지 표현 100% 차단 확인 |

> **권고:** RPN 560 (Hallucination)과 360 (PII)이 미해결 상태라면 배포를 연기하는 것이 낫습니다. 금융 도메인은 오답 한 건이 법적 책임으로 이어질 수 있습니다.
