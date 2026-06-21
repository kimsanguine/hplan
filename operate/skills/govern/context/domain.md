# Domain Context — Agent Deployment Governance

## 위험 등급 산정 (먼저 한다)

데이터 민감도 × 행위 권한으로 게이트 깊이를 결정한다.

| | 읽기 | 쓰기 | 삭제/전송 |
|--|------|------|-----------|
| 공개 | Low | Low | Med |
| 내부 | Low | Med | High |
| 기밀/PII | Med | High | Critical |

- Low: dlp·audit만 점검
- Med: + permissions
- High/Critical: 전 항목(killswitch·orphaned 포함) 강제

## DLP — 유출 표면

- 외부로 나가는 경로: 모델 API, 서드파티 도구, 로그/캐시/메모리 잔류, 출력물
- 통제 수단: 마스킹, 토큰화, 레다크션, 전송 차단, 보존 기간 제한
- "읽기 도구 vs 쓰고 지우고 전송하는 주체" — 후자는 유출 표면이 본질적으로 넓다

## 감사 로그 최소 스키마

```
timestamp · actor(user|agent) · tool · target · decision · outcome · cost
```
- append-only(불변), 접근 최소, 변조 탐지, 보존 기간 명시

## 킬스위치 / 롤백 RACI

- 즉시 정지(kill): 실행 가능한 버튼/플래그여야 함 (문서상 권한 ≠ 통제)
- 롤백: "직전 안전 상태"를 명시 (이전 모델 버전 / 승인 큐 / 비활성 상태)
- 권한 회수: off-boarding·프로젝트 종료 시 토큰·접근 폐기 절차

## 최소권한 (least privilege)

- allowed-tools 를 실제 필요분으로 축소
- 쓰기/삭제/전송 도구 → HITL 승인 또는 가역성 검증(reversibility × error-impact)
- 자격증명 scope 최소화 + 만료·회전

## Orphaned agent

- owner·목적·TTL·재검토일이 없는 에이전트 = 잠복 리스크(내부자 위협 표면)
- 프로젝트 종료 후 잔존 → 권한 회수 또는 아카이브
- 정기 인벤토리로만 발견 가능 (스스로 신고하지 않음)

## 참고 프레임워크 (체크리스트 수준, 법적 자문 아님)

- NIST AI RMF — Govern/Map/Measure/Manage
- OWASP LLM Top 10 — Excessive Agency, Sensitive Info Disclosure, Insecure Output Handling
- 가역성 × 오류영향 매트릭스 (automation level 1–5)
