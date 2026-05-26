# Good Example — qa-checklist 스킬

## 사용자 요청

"AI 인터뷰 분석 SaaS PRD 기반으로 QA 체크리스트 만들어줘."

## 입력 컨텍스트 (PRD 요약)

- **제품명**: InterviewLens — AI 인터뷰 분석 SaaS
- **§3 ICP**: "PM/UX 리서처가 5명 이상의 인터뷰 노트(파일)를 한 번에 업로드해 주제·인사이트·인용구를 자동 추출"
- **§11 테스트 전략**: "파일 업로드 10개 이하, 분석 완료 응답 30초 이내, 결과 정확도 BLEU ≥ 0.7"
- **§14 실패 시나리오**: 파일 업로드 실패, 분석 타임아웃(>30초), 일부 인터뷰만 분석됨, 중복 결과 표시, 비지원 파일 형식 업로드

## 승인 이유

- PRD §3 ICP, §11 테스트 전략, §14 실패 시나리오가 모두 존재
- deliver 완료 후 quality-gate 전 TC 정의 필요
- 5명 동시 업로드가 핵심 가치이므로 배치 처리 시나리오가 critical

## 예상 처리

1. PRD §3 ICP 파싱 → "5명 이상 파일 한 번에 분석" → critical TC 후보
2. PRD §14 실패 시나리오 파싱 → major/critical 분류
3. PRD §11 테스트 전략 → 기존 조건(30초, BLEU 기준) TC에 반영
4. Web app 키워드 감지 → Chrome Desktop, Safari Mobile 환경 포함
5. 심각도 분류 후 TC-ID 부여
6. `harness/QA_CHECKLIST.md` 생성

## 예상 출력 (harness/QA_CHECKLIST.md)

```markdown
# QA Checklist — InterviewLens
생성: 2026-05-26 | 소스: docs/PRD.md

## 🔴 Critical (ICP 핵심 경로)
| TC-ID | 시나리오 | 환경/디바이스 | 전제조건 | 기대 결과 | PRD 출처 | 심각도 |
|---|---|---|---|---|---|---|
| TC-001 | 인터뷰 파일 5개 동시 업로드 → 전체 분석 완료 | Chrome Desktop | 로그인, .docx/.txt 파일 5개 준비 | 5개 모두 분석 완료, 주제/인사이트/인용구 추출 | §3 ICP | critical |
| TC-002 | 분석 30초 초과 시 타임아웃 에러 메시지 표시 | 모든 주요 브라우저 | 분석 의도적 지연 (목 서버) | "분석에 시간이 걸리고 있습니다" 에러 UI 표시 | §11, §14 | critical |
| TC-003 | 회원가입 → 이메일 인증 → 첫 업로드 완료 | Chrome Desktop, Safari Mobile | 신규 이메일 계정 | 회원가입 완료, 대시보드 진입 | §3 ICP | critical |
| TC-004 | 로그인 후 기존 분석 결과 조회 | Chrome Desktop | 이전 분석 완료 이력 존재 | 분석 이력 목록 및 상세 결과 정상 표시 | §3 ICP | critical |

## 🟡 Major (대체 경로 존재, 현저히 불편)
| TC-ID | 시나리오 | 환경/디바이스 | 전제조건 | 기대 결과 | PRD 출처 | 심각도 |
|---|---|---|---|---|---|---|
| TC-005 | 일부 인터뷰 파일만 분석됨 (5개 중 3개 성공) | Chrome Desktop | 파일 2개를 손상 파일로 설정 | 성공 3개 결과 표시 + "2개 분석 실패" 명시적 안내 | §14 | major |
| TC-006 | 비지원 파일 형식 업로드 (.pptx) | 모든 주요 브라우저 | .pptx 파일 준비 | "지원하지 않는 형식입니다. .docx/.txt/.pdf 업로드 가능" 안내 | §14 | major |
| TC-007 | 업로드 중 네트워크 끊김 → 재연결 후 상태 복구 | Chrome Desktop | 업로드 50% 시점 네트워크 차단 | 재연결 후 업로드 재시도 가능, 상태 보존 | §14 | major |
| TC-008 | 분석 결과 중복 항목 표시 검증 | Chrome Desktop | 동일 파일 2회 업로드 | 중복 경고 또는 자동 중복 제거 처리 | §14 | major |
| TC-009 | 모바일 Safari에서 파일 업로드 UI 동작 | Safari Mobile (iOS 17/18) | iOS 기기, .docx 파일 | 파일 선택 → 업로드 완료 정상 동작 | §3 ICP | major |

## 🟢 Minor (엣지 케이스)
| TC-ID | 시나리오 | 환경/디바이스 | 전제조건 | 기대 결과 | PRD 출처 | 심각도 |
|---|---|---|---|---|---|---|
| TC-010 | 파일명에 특수문자 포함된 경우 업로드 | Chrome Desktop | 파일명 "인터뷰 #1 (최종).docx" | 파일명 처리 정상, 분석 결과 출력 | §14 | minor |
| TC-011 | 빈 파일(0KB) 업로드 시도 | 모든 주요 브라우저 | 0KB .txt 파일 | "파일 내용이 없습니다" 안내 | §14 | minor |
| TC-012 | 1개 파일만 업로드 (최솟값 경계) | Chrome Desktop | 파일 1개 | 정상 분석 완료 | §3 ICP | minor |

## 통계
- Total: 12개 | Critical: 4 | Major: 5 | Minor: 3
- PRD 섹션 커버리지: §3 ✅, §11 ✅, §14 ✅
```

## 최종 결과물

`harness/QA_CHECKLIST.md` 12개 TC (critical 4, major 5, minor 3).
PRD §3·§11·§14 전 섹션 커버리지 달성.
심각도 분류 기준(ICP 직결 여부, 대체 경로 존재 여부)이 각 TC에 명시적으로 적용됨.
