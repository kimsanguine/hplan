# Test Cases — interop

## 트리거되어야 함 (Use)
- "MCP로 갈지 A2A로 갈지, 지금 어떤 연결 표준에 베팅해야 하나?"
- "이 에이전트가 다른 팀 에이전트랑 통신해야 하는데 프로토콜을 뭘 쓰지?"
- "같은 스킬셋을 Claude Code랑 Codex 양쪽에서 유지하는데 너무 번거롭다"
- "신생 연결 표준이 발표됐는데 지금 갈아타야 하나, 기다려야 하나?"
- "단일 벤더 전송에 묶이면 위험한가? lock-in 점수 내줘"

## 라우팅되어야 함 (Route, interop 아님)
- "에이전트 5개를 순차로 돌릴까 병렬로 돌릴까?" → orchestration (내부 협력)
- "간단한 건 Haiku, 복잡한 건 Opus로 자동 라우팅" → orchestration --pattern router
- "어제 세션 컨텍스트를 오늘 어떻게 기억하지?" → memory-arch (메모리 계층)
- "선택한 전송을 시스템 프롬프트 도구로 어떻게 정의?" → deliver:instruction
- "이 에이전트 권한이 과한가, 멈출 수 있나?" → operate:govern (보안)

## 경계 (Boundary)
- 신생 표준 → 철회 가능성 먼저, 상태는 묶지 않음
- 타깃 하네스 2개로 한정 (과설계 금지)
- 연결 표준이 권한/DLP를 보장한다고 가정 금지

## 품질 assertion
- 출력에 "지금 필요(도구/위임/멀티하네스)"가 먼저 규정된다
- 이식 가능(스킬) vs 비이식(commands/hooks) 분리가 제시된다
- durable state를 두는 파일/포맷이 명시된다
- lock-in 점수 + 재검토 트리거가 나온다
