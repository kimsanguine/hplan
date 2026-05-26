# Spec Compliance Reviewer Prompt Template

Spec 검토 에이전트 디스패치 시 아래 템플릿 사용.

**목적:** 구현체가 요청한 것과 PRD가 약속한 것을 동시에 만족하는지 검증.
superpowers와의 차이: task description 대조 외에 **PRD 섹션 대조**를 추가로 수행한다.

---

## Spec Compliance Review — 태스크 [N]

### 원래 요청 (태스크 전문)
[태스크 설명 전문]

### 구현자 보고
[implementer의 STATUS + 요약 + 변경 파일 목록]

### ⚠️ 보고를 신뢰하지 말 것
구현자의 보고는 낙관적이거나 불완전할 수 있다. 반드시 실제 코드를 직접 읽어 검증한다.

### 검증 항목 A — 태스크 스펙 대조
- 요청한 것이 실제로 구현됐는가?
- 요청하지 않은 것이 추가됐는가? (있으면 FAIL)
- 완료 기준이 모두 충족됐는가?

### 검증 항목 B — PRD 섹션 대조 (필수)
harness/PRD.md를 Read하여 아래를 확인한다.
harness/PRD.md가 없으면 **FAIL** — conductor Step 0에서 이미 존재를 확인했어야 함.

- **§3 ICP**: 이 구현이 PRD가 정의한 핵심 고객의 핵심 문제를 해결하는가?
- **§11 Output Spec**: 실제 출력 구조가 §11 출력 예시·포맷과 일치하는가?
- **§14 Failure Scenarios**: 이 태스크가 담당해야 할 실패 시나리오가 처리됐는가?
- **§7 Success Metrics (Anti-Goals)**: 하면 안 된다고 명시된 것이 구현되지 않았는가?

4항목 모두 확인. SKIP 없음.

### 판정 기준
- ✅ PASS: A 모두 충족 + B 4항목 모두 충족
- ❌ FAIL with gaps: 충족 안 된 항목 목록 명시 → 구현자에게 수정 요청
- ⚠️ PASS with notes: 통과하나 관찰 사항 있음

### 반환 형식
판정: PASS / FAIL / PASS_WITH_NOTES
미충족 항목: [있을 경우 목록]
PRD 섹션 대조 결과: [§ 번호별 PASS/FAIL]
