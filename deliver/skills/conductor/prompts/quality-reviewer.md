# Code Quality Reviewer Prompt Template

코드 품질 검토 에이전트 디스패치 시 아래 템플릿 사용.
**Spec Compliance 통과 후에만 실행한다.**

---

## Code Quality Review — 태스크 [N]

### 구현된 코드 (커밋 해시 또는 파일 목록)
[변경 파일 목록]

### 검증 항목 A — 기본 코드 품질
- 테스트가 있는가? 테스트가 WHY를 인코딩하는가? (WHAT이 아니라)
- 로직이 바뀌어도 안 깨지는 테스트 = 잘못 쓴 테스트
- TODO/FIXME/임시방편 주석 수 (5개 이하 PASS, 6-15 WARNING, 16+ FAIL)
- 함수/파일 단위 책임이 명확한가?

### 검증 항목 B — hplan 9 Rules 준수
- **Rule 2 (Simplicity First)**: 요청하지 않은 기능이 추가됐는가? 호출 안 될 분기가 있는가?
- **Rule 3 (Surgical Changes)**: 요청 외 파일·섹션을 수정했는가?
- **Rule 4 (Goal-Driven)**: 완료 보고에 검증 행위(테스트 결과 등)가 인용됐는가?
- **Rule 8 (Fail Loud)**: 미검증 단계를 "완료"로 보고했는가?

### 판정 기준
- ✅ APPROVED: A·B 모두 충족
- ⚠️ APPROVED_WITH_NOTES: 통과하나 개선 권고
- ❌ NEEDS_WORK: 수정 필요 항목 명시

### 반환 형식
판정: APPROVED / APPROVED_WITH_NOTES / NEEDS_WORK
강점: [잘 된 것]
수정 필요 항목: [있을 경우]
Rule 위반: [있을 경우 Rule 번호 + 설명]
