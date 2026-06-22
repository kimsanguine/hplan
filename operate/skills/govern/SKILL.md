---
name: govern
description: "Run a deployment governance gate for an AI agent before and during production — data-loss/DLP exposure, audit logging, kill-switch and rollback authority, least-privilege tool permissions, and orphaned-agent inventory. Use when deciding whether an agent is safe and controllable to ship, when security/legal asks 'who can stop this agent and what can it touch,' or when auditing agents already running in production."
argument-hint: "[agent to assess] [--check dlp|audit|killswitch|permissions|orphaned|all]"
allowed-tools: ["Read", "Grep"]
context: fork
model: inherit
hooks:
  Stop:
    - type: command
      command: "bash scripts/validate-review.sh govern . 2>/dev/null || true"
---

# Deployment Governance Gate

> 배포·운영해도 통제 가능한가 — 출시 전/후 거버넌스 게이트

## Core Goal

- **"멈출 수 있는가"를 출시 전에 증명** — 에이전트를 정지·롤백할 권한과 절차가 명시돼 있어야 GO. 평균 정확도가 아니라 통제 가능성으로 판정.
- **에이전트가 만질 수 있는 것 = 최소권한으로 제한** — 도구·데이터·외부 전송 권한을 읽기/쓰기/전송 단계로 분해하고, 필요 없는 권한은 회수.
- **사람 판단이 필요한 5개 점검을 1개 게이트로 통합** — DLP·감사 로그·킬스위치/롤백·도구 권한·orphaned agent를 `--check` 모드로 순차 점검하고 GO/CONDITIONAL/NO-GO로 수렴.

---

## Trigger Gate

### Use This Skill When

- 에이전트를 프로덕션에 **배포할지 결정하기 직전** — 기능은 됐지만 "통제 가능한가"가 미검증일 때
- 보안·법무·컴플라이언스가 **"이 에이전트가 무엇을 만지고, 누가 멈출 수 있나"**를 물을 때
- 이미 운영 중인 에이전트 포트폴리오의 **권한·감사 추적·잔존 에이전트(orphaned)를 정기 감사**할 때
- 에이전트가 데이터를 **쓰거나 삭제하거나 외부로 전송**하는 권한을 가질 때 (읽기 전용이 아닐 때)

### Route to Other Skills When

- **reliability** → 정지/롤백이 아니라 **정확도·실패율·SLA 목표**가 핵심일 때 (P95/P99 신뢰성)
- **incident** → 이미 **장애가 발생**해 봉쇄·근본원인 분석이 필요할 때 (사후 대응)
- **ops-review** → **모델 비용·번레이트** 통제가 핵심일 때 (거버넌스가 아니라 예산)
- **deliver:instruction** → 점검 결과 **시스템 프롬프트의 최소권한 도구 정의**를 다시 써야 할 때
- **hplan (게이트)** → 이 스킬은 hplan 의 결정 게이트에서 *ship 직전* 자동 호출되는 보안 분기

### Boundary Checks

- **거버넌스 ≠ 규제 완전성** — 이 게이트는 *출시 전 체크리스트*이지 법적 자문이 아니다. EU AI Act·개인정보보호법 해석은 법무로 위임.
- **점검 대상이 모호** — 에이전트의 도구·데이터 접근 목록이 없으면 DLP·권한 점검 불가 → 먼저 instruction/PRD에서 도구 인벤토리 확보.
- **과도한 게이트** — 모든 내부 읽기전용 에이전트에 풀 게이트를 강제하면 운영 마비 → 위험 등급(데이터 민감도 × 쓰기/전송 권한)으로 점검 깊이 차등.

---

## 개념

에이전트 거버넌스는 "잘 작동하는가"가 아니라 "통제권을 우리가 쥐고 있는가"로 측정한다. 읽기 도구는 실수해도 되돌릴 수 있지만, 쓰고·지우고·전송하는 주체는 한 번의 오작동이 복구 불가능한 손실을 만든다. 따라서 권한이 클수록 **정지·롤백·감사**가 기능보다 먼저 존재해야 한다.

## Instructions

You are running a **deployment governance gate** for: **$ARGUMENTS**

먼저 위험 등급을 정한다 — **데이터 민감도(공개/내부/기밀/규제) × 행위 권한(읽기/쓰기/삭제/외부 전송)**. 등급이 높을수록 모든 `--check`를 강제하고, 낮으면 dlp·audit만 본다.

### --check dlp — 데이터 유출 표면

에이전트가 접근·생성·전송하는 데이터를 분류한다.

| 데이터 | 분류(공개/내부/기밀/PII) | 흐름(읽기/쓰기/외부 전송) | 노출 위험 | 통제 |
|--------|--------------------------|---------------------------|-----------|------|
| | | | | 마스킹/토큰화/차단 |

- 외부(모델 API·서드파티 도구)로 나가는 기밀·PII가 있는가 → 마스킹·레다크션·전송 차단 중 택1
- 증류·로그·캐시에 민감 데이터가 잔류하는가 (caching/메모리 잔류)

### --check audit — 감사 로그

- 누가(사용자/에이전트), 언제, 어떤 도구로, 무엇을 했는지가 **불변(append-only)** 로그로 남는가
- 로그 보존 기간·접근 권한·변조 방지가 정의됐는가
- 최소 기록 필드: `timestamp · actor · tool · target · decision · outcome`

### --check killswitch — 정지/롤백 권한 (핵심)

"누가 이 에이전트를 멈출 수 있나" 매트릭스를 채운다.

| 권한 | 담당(역할) | 절차 | 소요(목표) |
|------|-----------|------|-----------|
| 즉시 정지(kill) | | | < N분 |
| 롤백(직전 안전 상태로) | | | |
| 권한 회수 | | | |

- 킬스위치가 코드/설정에 실제로 존재하는가 (문서상 권한이 아니라 실행 가능한 버튼)
- 롤백 대상 = 직전 "안전 상태"가 무엇인지 정의됐는가

### --check permissions — 최소권한 도구 감사

- 에이전트에 부여된 도구를 나열하고 **각 도구가 실제로 필요한지** 검증 (allowed-tools 최소화)
- 쓰기/삭제/전송 도구는 사람 승인(HITL) 게이트 또는 가역성 검증을 통과했는가
- 자격증명·토큰의 범위(scope)가 최소인가, 만료·회전 정책이 있는가

### --check orphaned — 잔존 에이전트 인벤토리

- 소유자·목적이 불명확하거나 **프로젝트 종료 후에도 계속 도는** 에이전트가 있는가
- 각 에이전트에 owner·만료(TTL)·재검토일이 있는가 → 없으면 orphaned 후보로 표시
- 잔존 에이전트의 권한·접근을 즉시 회수 또는 아카이브

### --check all

dlp → audit → killswitch → permissions → orphaned 순서로 전부 점검 후 종합 판정.

### Output

거버넌스 게이트 결과 카드:
```
Agent: [name]
위험 등급: [데이터 민감도] × [행위 권한] = [Low/Med/High/Critical]
점검: dlp [✅/⚠️/❌] · audit [..] · killswitch [..] · permissions [..] · orphaned [..]
미충족 항목: [목록]
판정: GO / CONDITIONAL GO (조건: ...) / NO-GO (선결: ...)
다음 재검토: [date]
```

판정 기준: 하나라도 ❌(High/Critical 등급에서)이면 NO-GO. ⚠️만 있으면 CONDITIONAL GO(완화 조건 명시). 전부 ✅면 GO.

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| **도구 인벤토리 부재** | 에이전트가 어떤 도구·데이터에 접근하는지 목록이 없음 | DLP·권한 점검 불가 → deliver:instruction/PRD 에서 도구·데이터 인벤토리 먼저 확보 후 재실행 |
| **킬스위치가 문서뿐** | "정지 권한은 운영팀"이라 적혀 있으나 실제 정지 버튼/절차 없음 | NO-GO. 실행 가능한 kill/rollback 구현을 선결 조건으로 등록 |
| **감사 로그 가변** | 로그는 있으나 에이전트/운영자가 덮어쓸 수 있음 | append-only 저장소로 분리, 접근 권한 최소화, 변조 탐지 추가 |
| **권한 과다인데 '편의상 필요'** | 삭제·전송 도구를 "혹시 몰라서" 부여 | 최소권한 원칙 — 미사용 권한 회수, 필요 시 HITL 승인 게이트로 대체 |
| **게이트 과부하** | 모든 내부 읽기전용 에이전트까지 풀 게이트 요구로 배포 정체 | 위험 등급(민감도×권한)으로 점검 깊이 차등 — 저위험은 dlp·audit만 |
| **규제 완전성 오해** | "이 게이트 통과 = 법적 컴플라이언스 완료"로 받아들임 | 게이트는 체크리스트일 뿐 — 규제 해석은 법무 위임을 출력에 명시 |

---

## Quality Gate

- [ ] 위험 등급(데이터 민감도 × 행위 권한)이 먼저 산정되었는가? (Yes/No)
- [ ] DLP 점검에서 외부로 나가는 기밀·PII와 그 통제(마스킹/차단)가 식별되었는가? (Yes/No)
- [ ] 감사 로그가 불변(append-only)이며 최소 기록 필드를 충족하는가? (Yes/No)
- [ ] "누가 멈출 수 있나" 매트릭스(즉시 정지·롤백·권한 회수)가 **실행 가능한** 형태로 채워졌는가? (Yes/No)
- [ ] 모든 쓰기/삭제/전송 도구가 최소권한·HITL·가역성 중 하나로 방어되는가? (Yes/No)
- [ ] orphaned 후보(owner·TTL 없는 에이전트)가 식별되고 처리 방침이 정해졌는가? (Yes/No)
- [ ] 최종 판정(GO/CONDITIONAL/NO-GO)과 미충족 선결 조건이 명시되었는가? (Yes/No)

---

## Examples

### Good Example

```
거버넌스 게이트: 고객 환불 처리 에이전트
위험 등급: 기밀(결제) × 쓰기/전송 = Critical → 전 항목 강제

dlp:        ✅ 카드번호 토큰화, 모델 API로 PII 미전송(레다크션)
audit:      ✅ append-only 로그(actor·tool·amount·decision·outcome), 1년 보존
killswitch: ⚠️ 즉시 정지 O(<2분) / 롤백 = "직전 승인 큐로 되돌림" 정의됨 / 권한 회수 절차 미정
permissions:✅ 환불 한도 초과 건은 HITL 승인 게이트, 토큰 scope=refund-only, 90일 회전
orphaned:   ✅ owner=결제팀, TTL=분기 재검토

판정: CONDITIONAL GO
조건: 권한 회수 절차(off-boarding 시 토큰 폐기) 문서화 + 1주 내 재점검
```

### Bad Example

```
"환불 에이전트 정확도 98% 나오니 다음 주에 배포하시죠. 감사 로그랑 정지 버튼은 운영하면서 붙입시다."

❌ 문제점:
- 통제(정지·롤백)가 배포 후로 미뤄짐 — Critical 등급에서 NO-GO 사유
- DLP 미점검 (카드번호가 모델 API로 평문 전송되는지 확인 안 함)
- 감사 로그 부재 (사고 시 누가 무엇을 했는지 추적 불가)
- "정확도"만 게이트로 사용 (통제 가능성은 보지 않음)

→ 재작업: 위험 등급 산정 → dlp/audit/killswitch 선결 → GO 판정 후 배포
```

---

## Further Reading
- NIST AI Risk Management Framework (AI RMF 1.0) — Govern/Map/Measure/Manage 함수
- OWASP Top 10 for LLM Applications — Excessive Agency, Sensitive Information Disclosure
- Anthropic, "Building Effective Agents" (2024) — 도구 권한과 사람 개입
- Google SRE Workbook — Rollback, kill-switch, and safe deployment practices

## Contextual Knowledge (auto-loaded)

> 보조 파일이 존재할 때만 자동 로드됩니다. 파일이 없으면 건너뜁니다.

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`

### Test Cases
!`cat references/test-cases.md 2>/dev/null || echo ""`

### Troubleshooting
!`cat references/troubleshooting.md 2>/dev/null || echo ""`
