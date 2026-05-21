# Breakpoint 검증 기준

mobile-check 스킬에서 Playwright 실행 시 사용하는 뷰포트 및 체크 항목.

## 뷰포트 정의

| 뷰포트 | 크기 | 대표 기기 | 높이 |
|--------|------|----------|------|
| mobile | 375px | iPhone 14 | 812px |
| tablet | 768px | iPad Mini | 1024px |
| desktop | 1440px | MacBook / 외부모니터 | 900px |

## 뷰포트별 체크 항목

### mobile (375px)
- [ ] 가로 스크롤 없음 (document.body.scrollWidth <= clientWidth)
- [ ] 터치타겟 최소 44×44px (버튼, 링크, [role=button])
- [ ] 폰트 최소 14px (가독성 기준)
- [ ] CTA 버튼 화면 하단 접근 가능

### tablet (768px)
- [ ] 가로 스크롤 없음
- [ ] 레이아웃 전환 (1컬럼→2컬럼) 정상 동작
- [ ] 이미지 비율 유지 (aspect-ratio 깨짐 없음)
- [ ] 사이드바/네비게이션 표시 상태 확인

### desktop (1440px)
- [ ] 최대 콘텐츠 너비 준수 (DESIGN.md 기준 초과 없음)
- [ ] 좌우 여백 균형
- [ ] 가로 스크롤 없음

## 실패 기준
하나의 뷰포트에서 체크 항목 1개 이상 실패 → 해당 뷰포트 ❌
3개 뷰포트 모두 ✅일 때만 mobile-check 통과.
