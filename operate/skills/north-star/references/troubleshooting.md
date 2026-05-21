# Troubleshooting — north-star 스킬

## 1) North Star 달성 불가능

**증상:**
- "3개월 목표 100에서 현재 65, 계속 내려간다"
- "왜 목표를 못 달성하는지 모르겠다"
- 팀 사기 저하, "이대로면 목표 달성 불가능"

**확인:**
- 목표값이 현실적이었나?
  - 기준선(Baseline)에서 얼마나 증가했나? (92% → 95%? 아니면 10배?)
  - 3개월 기간이 충분했나?
- 분해 트리에서 막힌 드라이버가 있나?

**조치:**
1. 목표 현실성 재검토:
   ```
   기존: North Star 100 (Month 3)
   기준선: 50 (지금)
   필요: +50 (100% 증가) — 보통 어렵다

   재설정:
   Month 1: 55 (+10%)
   Month 2: 65 (+18%)
   Month 3: 75 (+50%) — 더 현실적
   ```
2. 분해 트리 분석:
   - 각 드라이버의 성과 확인
   - "Driver 1은 +5 달성, Driver 2는 +2만 달성, Driver 3은 0" 분석
   - 막힌 Driver 파악
3. 막힌 부분 해결:
   - Driver 3이 막혔다면, "왜 막혔나?" (리소스? 기술? 고객 피드백?)
   - 해결책 재설계
4. 목표 재합의:
   - 경영진과 현실적 목표 재설정
   - "Month 3: 75 (원래 100에서 수정)"

---

## 2) Anti-metric 악화

**증상:**
- "North Star 'Executions per week' 늘렸는데"
- "Accuracy가 95%에서 85%로 추락"
- "양쪽을 동시에 달성할 수 없는 건가?"

**확인:**
- Anti-metric threshold 설정 여부 (Accuracy > 90%?)
- Anti-metric 악화가 구조적인가, 일시적인가?
- North Star 증가와 Anti-metric 악화 간의 인과관계

**조치:**
1. Anti-metric 강화:
   ```
   기존: Executions per week > 500
         Anti-metric: Accuracy > 90% (약함)

   강화: Executions per week > 500
         Anti-metric: Accuracy > 93% (강화)
         Anti-metric: Hallucination < 3% (추가)
   ```
2. North Star 재정의:
   - 순수 Executions이 아니라 "정확한 실행"으로 변경
   - North Star = Executions × Accuracy
   - 양쪽을 모두 고려하는 합성 지표
3. 개선 전략 변경:
   - "실행 수 증가"만이 아니라 "높은 품질 유지하며 증가"로 재정의
   - 품질 저하를 초래하는 레버는 제거
4. 점진적 개선:
   - Accuracy 회복이 선행되면 Executions 증가 추진

---

## 3) 분해 트리 미작동

**증상:**
- "이 레버를 당기면 North Star가 올라가야 하는데 안 올라간다"
- "드라이버와 레버의 연결이 끊어진 것 같다"
- 팀이 "뭘 해야 하는지" 모르는 상태

**확인:**
- 분해 트리 설계:
  - North Star는 명확한가?
  - 드라이버는 North Star에 영향을 주나?
  - 레버는 팀이 직접 통제 가능한가?
- 인과 관계:
  - "레버 X를 당기면 드라이버 Y가 변하고, Y가 변하면 North Star Z가 변한다" 검증

**조치:**
1. 분해 트리 재검증:
   ```
   North Star: Revenue from agent = $10M/year
   Driver 1: Users × Willingness to Pay
   Driver 2: Usage per User

   레버가 정확한가?
   ✓ 마케팅 (Users 증가 → Driver 1)
   ✓ UX 개선 (Usage 증가 → Driver 2)
   ✗ "색상 변경" (어느 드라이버에도 영향 없음)
   ```
2. 누락된 레버 추가:
   - "가격책정 최적화" 추가 (Willingness to Pay 영향)
   - "고객 성공 팀" 추가 (Retention 영향)
3. 인과 관계 검증:
   - A/B 테스트: "레버 X 적용 후 드라이버 Y 변했나?"
   - 최소 3개월 데이터로 연결성 확인
4. 팀 커뮤니케이션:
   - "이 레버는 장기(3개월+) 효과가 있습니다" 명시
   - 즉각적 효과 기대 안 함

---

## 4) 팀 정렬 부족

**증상:**
- "일부 팀은 자신의 KPI만 최적화하고 North Star는 무시한다"
- "Marketing팀은 Users 늘리고, Engineering팀은 Cost 줄이고"
- North Star가 실제 의사결정에 반영 안 됨

**확인:**
- 팀별 OKR과 North Star의 연결 여부
- 성과 평가 기준 (North Star 포함?)
- 인센티브 체계 (North Star 달성 시 보상?)
- 월간 North Star 리뷰 미팅 여부

**조치:**
1. North Star를 OKR과 명시 연결:
   ```
   North Star: Accurate Executions per Week (500 → 700)

   Marketing OKR:
   - Key Result 1: Users 2,000 → 3,000 (North Star의 Driver 1)
   - Key Result 2: Retention 40% → 50% (North Star의 Driver 1)

   Engineering OKR:
   - Key Result 1: Accuracy 90% → 93% (North Star의 Quality 부분)
   - Key Result 2: Cost per Execution -20% (Anti-metric 보호)
   ```
2. 월간 North Star 리뷰 (강제):
   - 고정 일정 (매월 첫 주 수요일, 1시간)
   - 모든 팀 참석 (PM, Marketing, Engineering)
   - 각 팀의 OKR 진도 + North Star 기여도 검토
3. 인센티브 연동:
   - 분기 보너스 = (North Star 달성율 × 50%) + (팀 OKR 달성율 × 50%)
   - 개인 평가 시 "North Star 기여" 항목 추가
4. 커뮤니케이션 강화:
   - 주간 standup에서 North Star 언급
   - "이 작업이 North Star의 어떤 드라이버에 영향을 주나?" 질문

---

## 5) 목표 달성 후 정체

**증상:**
- "North Star 목표 달성했는데 팀 동기가 떨어졌다"
- "다음이 뭔지 모르겠다"
- 개선 속도 저하

**확인:**
- 목표 달성 시점과 팀 동기 저하 시점 연관성
- 새로운 목표 없음 (목표 공백 기간)
- 팀의 성취감 충분히 인정받지 못한 건 아닌가?

**조치:**
1. 성취 인정:
   - 팀 전체 축하 미팅 (30분)
   - 개인별 기여도 인정 (공식 칭찬)
   - 성과 공유 (회사 전체 공지)
2. 다음 단계 North Star 설정:
   ```
   이전: Executions per week 500 → 700 ✓ 달성
   다음: Executions per week 700 → 1,000 (다음 분기)
   또는 다른 지표로 전환: Revenue Growth 또는 Customer NPS
   ```
3. 향상 목표 설정:
   - 양적 증가: 700 → 1,000 (43% 증가)
   - 질적 개선: Accuracy 93% → 96% (프리미엄 티어 지원)
   - 신규 차원: Customer NPS 50 → 70 (고객 만족도)
4. 장기 비전 공유:
   - "1년 후 우리 에이전트는 이 정도 규모가 될 것"
   - "이 달성이 그 여정의 첫 마일스톤"

