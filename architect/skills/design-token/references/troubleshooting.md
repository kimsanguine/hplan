# design-token — 자주 발생하는 문제

## 문제 1: DESIGN_BRIEF.md가 없는 상태로 실행
해결:
> "/design-reference를 먼저 실행하거나, 직접 토큰 값을 입력하시겠습니까?
> 직접 입력 시: 카테고리/대상/톤과 원하는 컬러 방향을 말씀해주세요."

## 문제 2: WCAG 대비비 계산이 필요할 때
도구: https://webaim.org/resources/contrastchecker/
공식: 밝은값/어두운값 = 대비비 (AA: 4.5:1, AAA: 7:1)
계산 없이 "통과할 것 같다"고 주석 작성 금지.

## 문제 3: 토큰이 너무 많아진다
기준: Color 7개, Typography 12개, Spacing 8개로 시작.
필요할 때만 추가. YAGNI 원칙 적용.
  ❌ --color-brand-primary-hover, --color-brand-primary-active 미리 생성
  ✅ 실제로 쓸 때 추가
