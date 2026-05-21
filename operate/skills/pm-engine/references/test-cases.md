# Test Cases — pm-engine

## 1) Trigger Tests (5 Positive + 5 Negative)

### Positive Trigger Cases (should_trigger = true)

**Test 1.1** — TK 동적 검색 (상황 기반)
```
Query: "우리가 새 에이전트를 만들지 기존 도구를 쓸지 결정해야 하는데,
        PM-ENGINE-MEMORY에서 관련 TK를 찾아줘"
Expected: TK-007, TK-003 자동 검색 및 조회
Trigger: ✅ YES (TK 검색 요청)
```

**Test 1.2** — TK를 Instruction으로 변환
```
Query: "TK-009(질문의 품질이 에이전트 품질을 결정)를
        에이전트 System Prompt에 어떻게 반영할지 보여줘"
Expected: TK-009 내용 → Instruction 변환 과정 및 결과
Trigger: ✅ YES (TK→Instruction 변환 요청)
```

**Test 1.3** — 새로운 TK 추출 (경험 기반)
```
Query: "오늘 회의에서 '유저는 기능이 아니라 결과를 원한다'는 걸 다시 깨달았어.
        이걸 TK로 구조화해서 PM-ENGINE에 저장해줘"
Expected: TK-NNN 형식으로 추출, 활성화/비활성화 조건 포함
Trigger: ✅ YES (TK 추출 요청)
```

**Test 1.4** — TK 간 연관성 확인
```
Query: "TK-001과 관련된 다른 TK들이 뭐가 있나?
        지식 그래프로 보여줘"
Expected: TK-001의 연관 TK 조회, 관계도 시각화
Trigger: ✅ YES (TK 연관성 쿼리)
```

**Test 1.5** — 상황별 TK 추천 (Contextual Retrieval)
```
Query: "우리가 긴급 요청을 너무 많이 받는데,
        우선순위를 어떻게 관리해야 할까?
        관련 TK 추천해줘"
Expected: TK-001(긴급 요청 우선순위 판단) 자동 추천
         + 활성화 조건 확인 (O)
Trigger: ✅ YES (Contextual Retrieval 패턴)
```

### Negative Trigger Cases (should_trigger = false)

**Test 1.6** — 일반 LLM 지식 요청
```
Query: "프롬프트 엔지니어링 팁 좀 알려줘"
Expected: pm-engine 거절, deliver 스킬로 라우팅
Trigger: ❌ NO (TK와 무관한 기술 조언)
```

**Test 1.7** — 에이전트 아키텍처 설계
```
Query: "에이전트 오케스트레이션 패턴을 고르는 데
        Sequential vs Hierarchical 뭐가 나을까?"
Expected: pm-engine 거절, learn의 다른 스킬이나 deliver로 라우팅
Trigger: ❌ NO (PM 판단 기준이 아니라 기술 아키텍처)
```

**Test 1.8** — 비용 계산
```
Query: "에이전트 비용을 시뮬레이션해줘"
Expected: pm-engine 거절, discover의 cost-sim으로 라우팅
Trigger: ❌ NO (비용 분석은 discover 영역)
```

**Test 1.9** — 데이터 분석
```
Query: "지난 달 에이전트 사용 데이터를 분석해줘"
Expected: pm-engine 거절, measure 스킬로 라우팅
Trigger: ❌ NO (데이터 분석은 measure 영역)
```

**Test 1.10** — 일반적인 PM 조언
```
Query: "신입 PM으로 일 년 차인데, 좋은 PM이 되는 팁 좀 줄래?"
Expected: pm-engine 거절 (TK 검색/참조가 아닌 일반 조언)
Trigger: ❌ NO (TK 체계화되지 않은 일반 질문)
```

---

## 2) Functional Tests (Given-When-Then)

### Test 2.1: TK 동적 검색 후 활성화 조건 검증

```
Given:
  - PM-ENGINE-MEMORY.md에 TK-007(Build vs Buy 2주 법칙) 저장됨
  - 현재 상황: "3주 예상 개발 시간, 기존 도구 있음"

When:
  - 사용자가 "build vs buy 판단"을 요청
  - pm-engine이 TK-007 검색

Then:
  - TK-007 로드 ✓
  - 활성화 조건 확인: "신규 기능 개발 결정" → ✓ 만족
  - 비활성화 조건 확인: "기술 스택 교체" → ✓ 해당 없음
  - 판단 적용: "2주 > 3주 → Buy 우선 검토" → ✓ 결론 도출
```

### Test 2.2: TK 부재 시 검색 실패 처리

```
Given:
  - 사용자가 "AI 의료 진단 에이전트 규제 대응"에 대한 TK 요청
  - PM-ENGINE-MEMORY에는 TK가 없음 (의료 규제 미경험 영역)

When:
  - pm-engine이 TK 검색 시도
  - 결과: "No TK found for this context"

Then:
  - 에러 핸들링 적용: ✓
  - 피드백: "이것은 새로운 패턴입니다.
              `/pm-tacit-extract`로 경험을 기록해주세요" ✓
  - 이후 TK 추출 후 검색 재시도 가능 ✓
```

### Test 2.3: TK 간 연관성을 통한 확장 검색

```
Given:
  - 사용자가 "긴급 요청 관리" 요청
  - TK-001(긴급 요청 우선순위 판단)이 로드됨
  - TK-001의 연관 TK: TK-004, TK-009 명시

When:
  - pm-engine이 TK-001을 로드
  - 연관 TK(TK-004, TK-009) 검색 트리거

Then:
  - TK-001 + TK-004(데이터 없으면 가설) 함께 로드 ✓
  - TK-001 + TK-009(질문의 품질) 함께 로드 ✓
  - 사용자에게: "긴급 요청 판단 시 데이터 검증과 맥락 파악이 함께 필요합니다" ✓
```

---

## 3) Error Cases (2)

### Error Case 3.1: TK 적용 시 활성화 조건 무시

```
상황:
  사용자가 TK-001(긴급 요청)을 실제 SLA 걸린 장애 대응에 적용

오류:
  - TK-001의 비활성화 조건: "실제 SLA가 걸린 장애 대응 상황"
  - 위 조건 정확히 위반

감지:
  pm-engine이 Context 확인 시 비활성화 조건 감지

대응:
  ❌ "이 TK는 이 상황에 맞지 않습니다.
      지금은 실제 SLA 걸린 긴급 상황이므로
      TK-001의 '가짜 긴급 필터링'은 생략하고
      즉시 대응하세요" ✓
```

### Error Case 3.2: TK 간 충돌

```
상황:
  - TK-007(Build vs Buy 2주 법칙): "2주 이상이면 Buy"
  - TK-008(경쟁사 카피는 해자가 아님): "핵심 차별화는 무조건 Build"
  - 현재 상황: "3주 예상 개발, 차별화 기능"

오류:
  두 TK의 판단이 충돌 (Buy vs Build)

감지:
  pm-engine이 TK 간 충돌 감지

대응:
  ✓ "TK-007과 TK-008이 이 상황에서 충돌합니다.
      우선순위: TK-008(차별화 > 비용 절감)에 따라
      Build 진행하되, TK-007의 '비용 시뮬레이션'은
      병행 검토하세요" ✓
```

---

## 3) Edge Cases

| # | 쿼리 | 판정 | 이유 |
|---|------|------|------|
| E1 | "우리 팀이 TK를 아직 뽑아내지 못했어. 그런데 지금 긴급 의사결정이 필요해. pm-engine을 쓸 수 있을까?" | ⚠️ 경계 | pm-engine은 "TK 기반" 스킬이므로 TK 없으면 "부분적 활용". 하지만 "TK 부재 감지" 후 `/pm-tacit-extract`로 연결하면 이후 활용 가능 |
| E2 | "우리 조직 경험과 안 맞는 TK가 나왔어(외부에서 받은 TK). 이걸 무시하고 다른 판단을 해야 할까?" | ✅ Trigger | pm-engine은 TK의 "활성화 조건/비활성화 조건"을 확인. 현재 상황에 비활성화 조건이 맞으면 그 TK 적용 안 함 권고 |
| E3 | "Build vs Buy 판단에서 TK-007과 TK-008이 충돌해. 어떤 TK를 우선할까?" | ✅ Trigger | TK 간 충돌은 pm-engine의 "우선순위 정의" 단계에서 다뤄짐. "차별화 > 비용 절감" 같은 조직 가치관 기반 우선순위 명시 |
| E4 | "이번에 새로 배운 판단 패턴이 있어. 이걸 지금 TK로 만들어서 쓸 수 있을까?" | ✅ Trigger | `/pm-tacit-extract`로 새로운 TK를 추출 후, 이후 pm-engine에서 활용 가능. TK는 "경험 축적"이므로 동적 성장 가능 |
| E5 | "pm-engine에서 TK를 추천받았는데, 그게 정말 이 상황에 맞는지 확신이 없어. 어떻게 검증할까?" | ✅ Trigger | TK 추천 후 "활성화 조건 확인" + "반대 입장 생각해보기" 프로세스 권고. 확신 불가면 팀 토론으로 검증 |

---

## 4) With/Without Skill 비교 (1)

### Test 4.1: pm-engine 적용 전후 의사결정 품질 비교

#### 시나리오: 신규 에이전트 개발 여부 판단

**Without pm-engine (일반 LLM 지식만 사용)**
```
상황: "새로운 에이전트를 만들지, 기존 도구를 쓸지 결정"

판단 프로세스:
1. "우리가 만들면 커스터마이징 가능하니까 좋을 것 같다"
2. "팀이 개발하고 싶어 해"
3. 개발 시작 → 3주 소모 → $15K 비용
4. 나중에 "오픈소스 도구면 $2K/년이면 충분했네" 깨달음
5. 같은 상황 반복

결과:
- 의사결정 근거: 감정 + 일반 조언
- 재현성: 낮음 (매번 다른 판단)
- 학습: 사후 후회 (비용이 이미 들어감)
- 팀 일관성: 낮음 (개인차 큼)

점수: 2/10 (비용 낭비, 반복 실수)
```

**With pm-engine (TK 활용)**
```
상황: 동일

판단 프로세스:
1. pm-engine 호출 → TK-007 검색
2. "직접 만들면 2주 넘게 걸리는가?" → 3주 확인
3. TK-007 적용: "Buy 우선 검토"
4. 연관 TK-003 로드: "비용 10배 법칙" → $500 POC가 100명이면 $50K
5. 현재 추정 비용 $15K vs Buy $2K 비교
6. 결정: Buy 우선, 필요 시 커스터마이징 아이템 리스트업
7. 실행 → 1주일 내 결정 완료, $2K 소모

결과:
- 의사결정 근거: TK 기반 (검증됨)
- 재현성: 높음 (같은 상황 = 같은 패턴)
- 학습: 사전 검증 (비용 절감)
- 팀 일관성: 높음 (TK-007, TK-003 공유)

점수: 9/10 (비용 절감, 속도 향상, 일관성)
```

**개선도: +7점 (350% 품질 향상)**
- 시간: -2주 (50% 단축)
- 비용: -$13K (86.7% 절감)
- 의사결정 속도: +500% (감정 기반 → TK 기반)

---

## Evaluation Metrics

| 항목 | 성공 기준 | 측정 방법 |
|------|---------|---------|
| Trigger Accuracy | Positive 5/5, Negative 5/5 | 각 케이스별 스킬 호출 여부 |
| Functional Correctness | Test 2.1~2.3 모두 패스 | 각 단계별 결과 검증 |
| Error Handling | Error Case 3.1~3.2 적절 대응 | 예상 에러 메시지 생성 여부 |
| Quality Improvement | With/Without 비교에서 7점 이상 개선 | 의사결정 품질 척도 |
| TK 검색 정확도 | Recall >= 95%, Precision >= 90% | 실제 관련 TK 찾음 여부 |
| Instruction 변환 적용률 | 생성된 Instruction을 에이전트가 따르는가 | A/B 테스트 |

