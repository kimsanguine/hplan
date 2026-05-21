# Agent PRD: Automated Code Review Agent

---

## Section 1 — Overview

```
에이전트 이름:  CodeSentinel
버전:           1.0
작성일:         2026-03-06
작성자:         Claude (claude-sonnet-4-6)
상태:           Draft

한 줄 정의:
GitHub PR을 자동으로 분석하여 보안 취약점·코드 스타일·성능 문제를
감지하고, PR에 인라인 코멘트로 직접 피드백하는 개발팀용 리뷰 에이전트

배경 / 만드는 이유:
- 코드 리뷰는 품질의 최후 방어선이지만, 반복적인 스타일·보안 체크에
  시니어 개발자의 인지 부하가 집중됨
- 보안 취약점(OWASP Top 10)은 리뷰어가 놓치기 쉬운 영역
- PR 대기 시간 단축 + 리뷰어는 아키텍처·로직에 집중할 수 있는 환경 조성
```

---

## Section 2 — Instruction Design

```
Role:
당신은 GitHub PR 코드 리뷰 전문 에이전트입니다. 변경된 diff를 분석하여
보안 취약점, 코드 스타일 위반, 성능 문제를 찾아내고, 근거와 개선안을
포함한 인라인 코멘트를 PR에 직접 작성합니다.

Primary Goal:
PR diff에서 실행 가능한(actionable) 리뷰 코멘트를 생성하고
GitHub PR에 자동 게시한다.

Secondary Goals:
1. OWASP Top 10 및 일반적인 보안 패턴 위반을 우선 탐지
2. 팀의 .editorconfig / 린트 설정과 일관된 스타일 피드백 제공
3. 명백한 O(n²) 루프, N+1 쿼리 등 성능 안티패턴 식별

Anti-Goals (하면 안 되는 것):
1. 아키텍처 방향 또는 비즈니스 로직에 대한 판단 — 이는 인간 리뷰어 영역
2. PR을 자동으로 승인(approve)하거나 병합(merge)하는 행동
3. diff에 없는 기존 코드(컨텍스트 라인)에 코멘트 작성
4. 확신이 낮은 이슈를 severity: critical로 분류하는 과대 보고
```

---

## Section 3 — Tools & Integrations

| 도구/API | 용도 | 사용 조건 | 호출 제한 |
|---|---|---|---|
| `github.get_pull_request` | PR 메타데이터·diff 수집 | 트리거 시 항상 | 1회/실행 |
| `github.list_pr_files` | 변경 파일 목록 + patch 수집 | 항상 | 1회/실행 |
| `github.get_file_content` | 리뷰 맥락용 원본 파일 조회 | 판단 불확실 시만 | 최대 5회/실행 |
| `github.create_review` | PR에 리뷰 코멘트 일괄 게시 | 분석 완료 후 1회 | 1회/실행 |
| `github.create_issue_comment` | 요약 코멘트 게시 | 항상 (리뷰 완료 후) | 1회/실행 |
| `read_file` | 로컬 규칙 파일 로드 | 초기화 시 | 제한 없음 |
| `web_search` | CVE·보안 패턴 참조 | 알 수 없는 라이브러리 취약점 | 최대 3회/실행 |

**최소 권한 원칙:**
- GitHub token scope: `pull_requests: write`, `contents: read` only
- Repository-level 설정 변경, secret 접근, CI 트리거 권한 없음

---

## Section 4 — Memory Strategy

```
Working Memory (컨텍스트):
- 항상 로드:
    · review_rules.yaml       — 팀별 커스텀 룰 (severity 임계값 포함)
    · security_patterns.md    — OWASP Top 10 체크리스트 + 언어별 패턴
    · style_guide.md          — 팀 코드 스타일 기준
- 조건부 로드:
    · lang/{language}_rules.md — 감지된 언어(Python/JS/Go 등)에 따라
    · past_reviews/{repo}.json — 동일 저장소 반복 이슈 패턴 (있을 경우)
- 컨텍스트 예산: ~30,000 tokens
    · diff:          최대 15,000 tokens
    · 룰 파일:       최대 5,000 tokens
    · 원본 컨텍스트: 최대 8,000 tokens
    · 예비:          2,000 tokens

Long-term Memory (파일):
- 읽기:
    · review_rules.yaml — 각 실행 시 최신 룰 로드
    · past_reviews/{repo}.json — 반복 패턴 파악
- 쓰기:
    · past_reviews/{repo}.json — 이번 리뷰 이슈 유형·빈도 누적
    · review_log.jsonl — 실행 이력 (PR URL, 이슈 수, 비용, 소요시간)
- 저장 트리거: 리뷰 게시 성공 후

Procedural Memory (Skills):
- agent-instruction-design (역할·경계 설계)
- failure-mode-analysis (실패 시나리오 도출)
- agent-kpi (성공 지표 정의)
```

---

## Section 5 — Trigger & Execution

```
트리거 유형:
☑ Event-Driven  — GitHub Webhook: pull_request (opened, synchronize)
☐ Cron
☐ Manual
☐ Pipeline

실행 흐름:
Step 1: [입력 수집]
  - Webhook payload에서 PR URL, repo, PR number 추출
  - github.get_pull_request → 제목, 작성자, base/head branch, 변경 파일 수
  - github.list_pr_files → 각 파일의 filename, status, patch(diff) 수집
  - diff 크기 확인 → 초과 시 분할 처리 또는 early exit (Section 7 참조)

Step 2: [분석]
  2a. 언어 감지 → 언어별 룰 파일 로드
  2b. 보안 스캔 (우선순위 1):
      - SQL Injection, XSS, SSRF, hardcoded secrets, insecure deserialization
      - 의존성 추가 시 알려진 CVE 패턴 탐지
  2c. 성능 스캔 (우선순위 2):
      - N+1 쿼리 패턴, O(n²) 루프, 불필요한 동기 블로킹
  2d. 스타일 스캔 (우선순위 3):
      - 네이밍 컨벤션, 함수 길이, 복잡도, 빠진 타입 힌트
  2e. 각 이슈에 severity 레이블: critical / high / medium / low

Step 3: [출력 생성]
  - 이슈 목록 → GitHub review comment 형식으로 변환
    (file path, line number, 문제 설명, 근거, 개선 코드 예시)
  - summary comment 생성:
    전체 이슈 수, critical/high 요약, 주요 패턴 하이라이트

Step 4: [전달/저장]
  - github.create_review (COMMENT 타입, 인라인 코멘트 일괄 게시)
  - github.create_issue_comment (PR 상단 요약)
  - review_log.jsonl 및 past_reviews/{repo}.json 업데이트

예상 실행 시간: 30~90초 (diff 크기에 따라)
타임아웃 설정: 180초
```

---

## Section 6 — Output Specification

```
출력 채널:  GitHub PR — 인라인 리뷰 코멘트 + PR 요약 코멘트
출력 형식:  Markdown
출력 길이:  인라인 코멘트 1개당 최대 500자 / 요약 코멘트 최대 1,500자
언어:       영어 (코드베이스 국제화 고려)
톤:         간결하고 건설적 — 문제 지적 + 개선 코드 제시
```

**인라인 코멘트 예시:**

```markdown
<!-- file: src/auth/login.py, line: 42 -->

🔴 **[CRITICAL] SQL Injection — 직접 문자열 포맷 사용**

사용자 입력값이 SQL 쿼리에 직접 삽입되고 있습니다.

**현재 코드:**
```python
query = f"SELECT * FROM users WHERE email = '{email}'"
```

**권장 수정:**
```python
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (email,))
```

> 참조: OWASP A03:2021 — Injection
```

**PR 요약 코멘트 예시:**

```markdown
## CodeSentinel Review Summary

| Severity | Count |
|---|---|
| 🔴 Critical | 1 |
| 🟠 High     | 2 |
| 🟡 Medium   | 4 |
| 🔵 Low      | 7 |

**주요 발견:**
- SQL Injection 취약점 1건 (즉시 수정 필요)
- N+1 쿼리 패턴 2건 (`user_service.py`)
- 타입 힌트 누락 4건

Critical/High 이슈 해결 후 인간 리뷰어 검토를 권장합니다.
_Reviewed by CodeSentinel v1.0 · 41 files · 1,203 lines changed_
```

---

## Section 7 — Failure Handling & Success Metrics

### 실패 시나리오

| 시나리오 | 감지 방법 | 대응 행동 |
|---|---|---|
| GitHub API 인증 실패 | 401/403 응답 | 즉시 종료 + 운영자 알림 (Slack/email), PR에 코멘트 없음 |
| PR diff 크기 초과 (>500 파일 또는 >50K lines) | 파일 수/토큰 측정 | 변경 규모 큰 파일 상위 20개만 분석 + 요약에 제한 사유 명시 |
| API Rate Limit 도달 | 429 응답 + Retry-After 헤더 | Retry-After 시간 대기 후 재시도 (최대 2회) |
| 언어 감지 실패 | 알 수 없는 확장자 | 언어별 룰 스킵, 공통 보안 패턴만 적용 |
| 토큰 예산 초과 (컨텍스트 85%+) | 토큰 카운터 | 스타일 이슈 제거 → 보안+성능만 유지 → 재시도 |
| LLM 응답 파싱 실패 | JSON parse error | 원시 텍스트 그대로 요약 코멘트에 첨부 후 종료 |
| 신뢰도 낮은 이슈 | 분석 신뢰 스코어 < 0.6 | severity를 한 단계 낮춤 (critical→high) + "requires human verification" 태그 |
| 완전 실행 실패 | 예외 미처리, 타임아웃 초과 | PR에 실패 알림 코멘트 1개만 게시: "CodeSentinel review failed — manual review required" |

### Human-in-the-loop 트리거

- **Critical 이슈 3건 이상** — 요약 코멘트에 `@security-team` 멘션 삽입
- **신뢰도 < 0.6 이슈가 전체의 40% 초과** — 전체 리뷰에 "(Low confidence — human review strongly recommended)" 배너 추가
- **알 수 없는 라이브러리의 보안 이슈** — web_search로 CVE 확인 후에도 판단 불가 시 이슈를 flagged 상태로 표시

### 성공 지표 (KPI)

```
정확도 목표:
  - False Positive율 < 15% (보고된 이슈 중 실제 아닌 것)
  - False Negative율 < 10% (Critical 이슈 기준)

비용 목표:
  - PR당 평균 < $0.05 (Sonnet 기준)
  - 월간 총 비용 < $50 (1,000 PR/월 가정)

레이턴시 목표:
  - PR 열림 후 첫 코멘트 게시까지 < 90초

신뢰성 목표:
  - 실행 성공률 > 99% (타임아웃 제외)
  - GitHub API 실패 후 복구율 > 95%

품질 지표:
  - 개발자 "유용한 리뷰" 평가율 > 75% (thumbs up reaction 기준)
  - 인라인 코멘트 dismiss율 < 20%
```

---

**설계 노트:**
- Security > Performance > Style 우선순위 엄수 — 토큰 예산 압박 시 역순으로 제거
- `create_review`는 반드시 COMMENT 타입 사용 (APPROVE/REQUEST_CHANGES 자동화 금지 — Anti-Goal)
- 동일 PR에 대한 재실행(synchronize 이벤트) 시 기존 CodeSentinel 코멘트는 업데이트하지 않고 새 리뷰로 추가 (추적 가능성 확보)