# Implementer Subagent Prompt Template

구현 에이전트 디스패치 시 아래 템플릿 사용.

---

## 태스크: [태스크 제목]

### 목표
[태스크 설명 전문 — plan에서 복사, 요약 금지]

### 컨텍스트
[이 태스크가 전체 플랜에서 어디에 위치하는지, 이전 태스크 결과물 중 알아야 할 것]

### worktree 경로
[이 에이전트가 작업하는 git worktree 절대 경로]
예: `/Users/you/project/.worktrees/T-003`
병렬 실행 시 이 경로 내에서만 파일을 생성·수정한다. main worktree 경로는 읽기 전용.
(단일 순차 실행이면 이 항목을 "main worktree — 단일 실행" 으로 명시)

### 허용 파일 범위
[수정 가능한 경로 목록 — Rule 9 Agent Scope Declaration 준수]
예: `src/api/`, `tests/unit/`, `harness/`
목록에 없는 경로 수정 금지. 불명확하면 작업 전 질문.

### 완료 기준
[검증 가능한 조건 — "잘 만들었다" 아닌 "이 파일이 존재한다", "이 테스트가 통과한다" 형식]

### 시작 전 질문
요구사항, 접근 방식, 의존성, 전제 조건에 대해 불명확한 것이 있으면
**작업 시작 전에 질문한다.** 추측으로 진행하지 않는다.

### 작업 완료 후 반환 형식
STATUS: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
요약: [한 줄 — 무엇을 만들었는가]
변경 파일: [파일 목록]
커밋 해시: [git commit hash]
우려사항: [STATUS가 DONE_WITH_CONCERNS인 경우만]

---

**주의:**
- 이전 태스크의 context를 직접 전달하지 않는다 (fresh context 보장)
- worktree 경로와 허용 파일 범위는 반드시 명시한다 (Rule 9)
- 완료 기준은 검증 가능한 형태로 작성한다
- 병렬 실행 시 main worktree 파일을 직접 수정하지 않는다
