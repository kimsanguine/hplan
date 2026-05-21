# Design Wisdom — 유명 디자인 시스템에서 추출한 원칙

Google Material · Apple HIG · IBM Carbon · Shopify Polaris ·
Atlassian · Microsoft Fluent · Vercel 디자인 시스템과
Robin Williams CRAP · Visual Hierarchy · WiderFunnel LIFT를
"그대로 쓰지 않고" 구조와 원칙만 추출.

각 원칙은 SKILL.md 지시문에서 직접 참조한다.

---

## 원칙 1: 토큰은 의미로 이름 짓는다
출처: IBM Carbon + Shopify Polaris 공통 관찰
원칙: 색·간격 토큰명에 값이 아니라 역할을 담는다
  ❌ --color-blue-500, --spacing-16
  ✅ --color-brand-primary, --space-4
이유: 나중에 값이 바뀌어도 코드를 수정하지 않아도 됨. "16px"은 변하지만 "기본 간격"은 변하지 않는다.
how-to-apply: design-token 스킬에서 토큰 생성 시 이 원칙으로 명명 강제.

---

## 원칙 2: 결정에는 반드시 이유를 함께 적는다
출처: Google Material Design 가이드라인 구조 관찰
원칙: 색·폰트·간격 선택값 옆에 선택 이유를 주석으로 기록
  ❌ --color-brand-primary: #3B82F6;
  ✅ --color-brand-primary: #3B82F6; /* 토스 레퍼런스 — 신뢰감+WCAG AA 통과 */
이유: 6개월 뒤 다른 사람이 바꿀 때 맥락을 이해하고 수정 가능.
how-to-apply: design-token 스킬에서 생성하는 모든 토큰에 주석 강제.

---

## 원칙 3: Do/Don't 예시를 포함한다
출처: Shopify Polaris 컴포넌트 문서 구조
원칙: 각 결정마다 하지 말아야 할 예시를 반드시 병기
이유: 규칙을 어기는 가장 흔한 상황을 사전에 차단. "하라"보다 "하지 마라"가 더 기억에 남는다.
how-to-apply: DESIGN_BRIEF.md 생성 시 각 패턴에 do/don't 1쌍 포함.

---

## 원칙 4: 타이포그래피는 비율 스케일로 관리한다
출처: Apple HIG 타이포그래피 스케일
원칙: H1-H2-H3-body 크기를 고정 비율로 설계. 권장: 1.25 (Minor Third) 또는 1.333 (Perfect Fourth)
예: body 16px → H3 20px → H2 25px → H1 31px (×1.25)
이유: 스케일이 흔들리면 페이지 간 위계가 무너짐.
how-to-apply: design-token 스킬에서 font-size 생성 시 비율 계산 강제.

---

## 원칙 5: 접근성은 디자인 결정의 제약 조건이다
출처: Microsoft Fluent Design 접근성 가이드라인
원칙: 색 대비는 WCAG AA(4.5:1) 이상을 디자인 단계에서 확인. 도구: https://webaim.org/resources/contrastchecker/
이유: 나중에 접근성 수정은 전체 컬러 시스템을 바꾸는 일.
how-to-apply: design-token 스킬에서 컬러 토큰 생성 시 대비비 계산 포함.

---

## 원칙 6: 중성 컬러가 베이스, 브랜드 컬러는 포인트
출처: Vercel 디자인 시스템 구조 관찰
원칙: 화면의 80%는 무채색(흰/검/회), 15%는 중간 톤, 5%만 브랜드 컬러
  ❌ 여러 개의 강한 색을 균등 배분
  ✅ 한 가지 브랜드 컬러가 결정적 순간에만 등장
이유: 포인트 컬러의 시각적 힘은 희소성에서 나온다.
how-to-apply: DESIGN_BRIEF.md 컬러 방향성 섹션에 이 비율 기준 적용.

---

## 원칙 7: 컴포넌트는 모든 상태를 커버한다
출처: Atlassian Design System 컴포넌트 명세
원칙: 버튼/입력/카드 등 모든 컴포넌트는 default/hover/active/disabled/error 상태 정의
이유: 상태 누락은 개발 중 UI 깨짐의 가장 흔한 원인.
how-to-apply: hierarchy-rules 스킬 연동 — 상태 미정의 컴포넌트 플래그.

---

## 프레임워크 8: CRAP 원칙
출처: Robin Williams, "The Non-Designer's Design Book"
원칙: 모든 페이지를 4개 축으로 평가한다 — Contrast · Repetition · Alignment · Proximity

**적용 체크리스트:**

| 축 | 관찰 방법 | 판정 기준 |
|----|----------|---------|
| Contrast | 배경 대비 충분한가? 섹션 경계가 보이는가? | ✅ 대비 명확 / ❌ 경계 모호 |
| Repetition | 섹션마다 동일한 구조(레이블→헤딩→본문)가 반복되는가? | ✅ 일관성 있음 / ❌ 섹션마다 다름 |
| Alignment | 그리드 축이 잡혀 있는가? 모바일 스택도 정상인가? | ✅ 정렬 일관 / ❌ 축이 흔들림 |
| Proximity | 관련 요소들이 시각적으로 가까운가? 무관한 요소가 붙어 있지는 않은가? | ✅ 관계 명확 / ❌ 요소 간 관계 끊김 |

**흔한 실패 패턴:**
- Contrast: 카드를 흰 배경 위 흰 카드로 구성 → 경계 없음
- Proximity: 좌측 텍스트와 우측 이미지 사이 여백 과도 → 두 요소의 관계가 끊겨 보임

how-to-apply: hierarchy-rules 스킬에서 페이지 검증 시 CRAP 4개 축을 체크리스트로 사용.

---

## 프레임워크 9: Visual Hierarchy (시각적 계층구조)
출처: UI/UX 디자인 원칙
원칙: 시선은 크기·색·대비가 강한 요소를 먼저 읽는다. 의도한 읽기 순서 ≠ 실제 시선 순서이면 메시지가 뒤집힌다.

**체크 방법:**
1. Hero에서 의도한 첫 메시지가 실제로 가장 눈에 띄는가?
   ❌ 서비스명(흰색)보다 기능명(그라디언트)이 더 눈에 띔 → 동사가 먼저 읽힘
   ✅ 서비스명이 크기·대비로 1순위, 기능명이 2순위
2. 카드/리스트에서 읽기 순서 유도가 있는가?
   ❌ 동일한 visual weight 3개 카드 → 스캔 포인트 없음
   ✅ 번호 레이블(1/2/3) 또는 크기 차이로 순서 유도

**의도 순서 vs 실제 시선 테스트:**
의도: A → B → C
실제: B → A → C (대비가 강한 B가 먼저 읽힘)
→ B의 대비를 낮추거나 A의 크기를 키워 순서 복원

how-to-apply: DESIGN_BRIEF.md 작성 시 Hero 섹션에 "의도한 읽기 순서" 명시 필수.

---

## 프레임워크 10: LIFT 모델
출처: WiderFunnel — Landing Page 전환율 최적화
원칙: 랜딩 페이지의 전환율은 4개 요소로 결정된다 — Leverage · Incentive · Friction · Trust

| 요소 | 의미 | 흔한 실패 | 개선 방향 |
|------|------|----------|---------|
| L (Leverage) | 3초 안에 내가 얻는 것이 보이는가? | 기능명 중심 ("자동화") | 결과 중심 ("폐기 판례 인용 방지") |
| I (Incentive) | CTA에 구체적 인센티브가 있는가? | "무료로 시작하기"만 있음 | "무료 체험 14일" 추가 |
| F (Friction) | 진입 장벽이 낮은가? | 가입 폼이 길거나 복잡 | 버튼 하나로 진입 |
| T (Trust) | 전환 직전에 신뢰를 깎는 요소가 없는가? | 푸터 면책 배너 → 전환 직전 불안 유발 | 면책 조항은 앱 내부로 이동 |

how-to-apply: DESIGN_BRIEF.md의 "디자인 방향성 결론" 섹션에서 랜딩/전환 페이지는 LIFT 4개 요소를 명시적으로 체크.
