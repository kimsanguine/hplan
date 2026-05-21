# Bad Example — pm-engine 오용

## 사용자 요청
"나한테 프롬프트 잘 짜는 팁 좀 알려줘."

## 거절 이유
- pm-engine의 역할: PM-ENGINE-MEMORY에서 TK를 참조하여 "판단"의 품질을 높이는 것
- 프롬프트 엔지니어링은 deliver 스킬 영역 (instruction, prd 스킬)
- TK 검색, 조회, 적용과 무관한 일반 기술 조언 요청

## 올바른 라우팅
- deliver 영역: `/instruction-design` (prompt engineering)
- discover 영역: `/prompt-chain` (프롬프트 체이닝 최적화)

## 수정 방향
사용자가 구체적 PM 판단 상황 제시: "에이전트가 특정 상황에서 환각을 자주 하는데, 이걸 줄이려면 어떻게 TK를 적용해야 할까?" → 그러면 pm-engine의 TK-006 (에이전트 환각은 UX로 해결), TK-009 (질문의 품질이 에이전트 품질을 결정) 참조 가능
