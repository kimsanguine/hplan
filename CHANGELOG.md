# Changelog

All notable changes to hplan (renamed from AI_PM_Skills in v0.5) are documented here.

---

## [1.0.1] — 2026-06-04

> **설치 정정 + 일괄 설치 지원.** marketplace 식별자 오류를 수정하고, settings.json 한 파일로 5개 플러그인을 한 번에 활성화하는 경로를 추가.

### Fixed
- **설치 명령 식별자 정정** — `README.md` / `README-ko.md` / `GUIDE-ko.md`의 `/plugin install <plugin>@kimsanguine-hplan` → `@hplan`. Claude Code의 marketplace 식별자는 `marketplace.json`의 `name` 필드(`"hplan"`)이며 owner-repo 자동생성(`kimsanguine-hplan`)이 아님 (공식 문서 `plugin-marketplaces.md#marketplace-schema` 2-소스 교차확인). 기존 명령은 설치 실패했음.

### Added
- **`.claude/settings.json.example`** — `extraKnownMarketplaces` + `enabledPlugins`로 5개 플러그인을 한 파일에 선언. `clone` + trust dialog만으로 `/plugin marketplace add` + 5× `/plugin install` 없이 전체 활성화. README 설치 섹션(Option 1b / 방법 0)에 안내 추가.
- `.gitignore` — `.claude/*` + `!.claude/settings.json.example` 패턴으로 템플릿 파일만 추적 (git negation 함정 회피).

---

## [1.0.0] — 2026-06-04

> **첫 정식 안정 릴리스.** `AI_PM_Skills` 리네임(v0.5) 이후 v0.14.2까지의 검증을 거쳐 ADK 5-Layer가 안정화됨. 기능 변화 없이 v0.14.2를 1.0.0으로 승격.

### Stable
- **ADK 5-Layer 완성** — L1 Memory(CLAUDE.md 9 규칙) · L2 Skills(34개) · L3 Hooks(SessionStart · PreToolUse gate · PostToolUse secret scan) · L4 Subagents(8역할 병렬 팀) · L5 Plugins(5 marketplace).
- **검증 통과** — `validate_plugins` 34 active / 0 errors · `pytest` 147 passed · 페르소나 5 + codex/claude 적대적 리뷰 통과 · 죽은 라우팅 0.
- **설치** — `curl -fsSL https://habix.ai/hplan/install.sh | bash` (sha256 검증 · atomic 설치 · path-traversal 차단) 또는 `/plugin marketplace add kimsanguine/hplan`.

---

## [0.14.2] — 2026-06-04

> **사용자 영향**: 표면 변화 없음. v0.14.1 머지 후 리뷰에서 발견된 MED/LOW 항목 정리 — gate_guard 보안 강화, 죽은 라우팅 참조 제거, 문서 메트릭 실측 정정, 문서 동기화.

### Security

- **gate_guard fail-closed 강화** — `gate_guard.py`의 CONDITIONAL_GO 처리와 `allowed_paths` 검증을 fail-closed로 강화. 게이트 상태가 모호하거나 경로 검증 정보가 불완전할 때 통과 대신 차단되도록 보강.

### Fixed

- **죽은 라우팅 정리** — 통합으로 흡수된 스킬을 가리키던 잔존 라우팅/참조를 제거·정정해 실재하지 않는 라우팅 타깃을 더 이상 가리키지 않도록 정리.

### Docs

- **트리거 정확도 실측 정정** — README.md / README-ko.md / `operate/evals/README.md`의 트리거 정확도 헤드라인을 과거 baseline(97.9% / 93.5% 등)에서 v0.14.1 실측 **90.9% (80/88, Haiku 4.5, 1-run 스냅샷)**으로 교체. 현재 34개 스킬 중 22개 커버, 1-run 스냅샷이라 ±변동, 전체 34-skill 커버는 진행 중임을 명시. 과거 v0.6 baseline 수치는 명확히 과거 baseline으로 라벨링해 보존.
- **CHANGELOG 날짜 정정** — `[0.14.1]` 헤더의 `YYYY-MM-DD (unreleased)` placeholder를 실제 머지 날짜(2026-06-04)로 갱신하고 `(unreleased)` 표기 제거.

---

## [0.14.1] — 2026-06-04

> **사용자 영향**: 스킬 수 38 → 34. 중복·근접 스킬 4종을 기존 스킬의 모드로 흡수. customer-reach(discover)는 정식 유지. README/CHANGELOG/문서 카운트 정합. 이번 릴리스의 핵심은 통합 + CRITICAL/HIGH 안정화 수정으로, 신규 사용자 표면(슬래시 커맨드·호출 가능 스킬)은 동일하게 유지된다.

### Changed — 스킬 통합 (38 → 34, 4종 흡수)

각 통합은 호출 표면을 줄이되 기능은 흡수 대상 스킬의 모드로 보존한다.

- **`deliver/stakeholder-review` → `deliver/ask-team --mode review`** — 이해관계자 리뷰 세션 준비(아젠다·사전 읽기·결정 항목·후속 정리)를 ask-team의 리뷰 모드로 흡수.
- **`deliver/stakeholder-update` → `operate/ops-review`** — 이해관계자별 비동기 업데이트 초안(Power-Interest 티어 정렬·Notion/email/Slack/Confluence export)을 operate의 ops-review로 흡수.
- **`deliver/roadmap` → `deliver/prd --mode roadmap`** — 게이트 판정 + 스프린트 추정을 우선순위 타임라인·의존성·마일스톤 뷰로 변환하는 로드맵 생성을 prd의 모드로 흡수.
- **`architect/router` → `architect/orchestration --pattern router`** — 복잡도별 T1~T4 모델 자동 라우팅 + 폴백 체인(40-80% 비용 절감)을 orchestration의 router 패턴으로 흡수.

**플러그인별 스킬 수**: hplan 8 · discover 6 · architect 4 · deliver 10 · operate 6 = **34**. 커맨드는 12개(harness-* 8 + `/hplan` + `/cogs-sentinel` + `/evidence-rubric` + `/prd`)로 유지.

### Fixed — CRITICAL / HIGH 안정화

- **eval 러너** — `operate/evals/run_trigger_evals.py`의 repo-root 경로 해석 수정(`parent.parent`→`parents[2]`) + 폐기된 플러그인명(`measure`/`learn`) 제거. `evals/`→`operate/evals/` 이동 이후 skills 카탈로그를 0개 로드하던 버그를 고쳐 트리거 eval이 실제로 채점되도록 정상화.
- **gate fail-closed** — Build Gate 미승인/오류 시 통과가 아닌 **차단(fail-closed)**으로 동작하도록 수정. checkpoint.json 부재·파싱 실패 시 PRD/spec 쓰기 차단.
- **cogs 통화 처리** — COGS sentinel의 통화 단위 처리 정합화로 마진 오판정 경로 차단.
- **CI 게이트** — CI 파이프라인에 정합성 게이트(`.github/workflows/ci-validate.yml`) 추가로 카운트·버전·링크 drift가 머지 전에 검출되도록 함.
- **customer-reach 경로** — `discover/skills/customer-reach`의 interview-questions 입력 경로를 잘못된 `harness/brainstorm-assumptions.md`에서 실재 위치인 `docs/brainstorm-assumptions.md`로 정정.
- **.gitignore** — harness 이해관계자/리뷰 산출물(`team-map.json`·`signoff-record.md`·`review-log.md`·`review-request.md`, 리뷰어 email/Slack PII 포함)을 ignore 목록에 추가해 우발적 커밋 차단.

### Docs

- `README.md` / `README-ko.md` — 버전 0.14.1, 스킬 수 34(+플러그인별 8/6/4/10/6) 통일. 흡수된 4종을 스킬 목록·표·라우팅 표·File Structure 트리에서 제거하고 흡수 위치(`--mode`/`--pattern`)를 반영. 죽은 내부 링크(`deliver/claude-md` → `deliver/agent-setup`) 수정. 커맨드 수 표기 정합(12개).

---

## [0.14.0] — 2026-06-03

> **사용자 영향**: 스킬 수 37 → 38. `discover/socratic-question` 신설(Phase 0 가정 심문). `deliver/roadmap`, `deliver/stakeholder-review`, `deliver/stakeholder-update`, `discover/customer-reach` 정식 추가. `harness-discover`에 Phase 0 진입점 추가. `sprint --step codebase-status` 신설(probe 없이 능동 코드베이스 탐색).

### Added — 신규 스킬 1개 + 기존 스킬 2개 강화

**`discover/socratic-question`** — 결정 전 AI 가정 심문 도구. 6가지 질문 유형(명료화·가정·증거·관점·함의·메타)으로 "만들 가치가 있나"를 심문하고 사고 검증 질문 세트 1장을 만든다. harness-discover Phase 1 진입 전 선택적 Phase 0.

**`hplan/commands/harness-discover` Phase 0 추가** — `--mode socratic` 플래그 및 Phase 0 진입점 신설. 가정이 불분명할 때 `socratic-question`으로 선라우팅 후 Phase 1(opp-tree)로 복귀하는 파이프라인 완성.

**`deliver/sprint --step codebase-status`** — probe hook 없이도 동작하는 능동 탐색 단계. 서브에이전트 스폰 → git log/diff/status·테스트 실행·`.track/` 인용 → `harness/codebase-report.md` 생성. 데이터 수집 결정론, 산문 합성만 LLM.

---

## [0.13.1] — 2026-06-02

> **사용자 영향**: 신규 스킬 2개 추가로 총 스킬 수 31 → 33. ticket-bridge(GitHub Issues ↔ sprint 연결), ask-team(팀원 비동기 질문 채널) 신설. sprint probe hook 실재화(track-probe.sh) + metrics-capture 문서화.

### Added — 신규 스킬 2개 + hook 실재화

**`deliver/ticket-bridge`** — GitHub Issues ↔ hplan sprint `.track/` 번역기. `--mode pull`(이슈 → WBS 후보), `--mode estimate`(predicted.json p50/p90 → 이슈 코멘트), `--mode status`(actual_log + git/PR → 이슈 코멘트). 추정치를 직접 계산하지 않고 sprint 산출물을 전달만 한다. Rule 5 준수: 라벨→complexity 매핑·이슈↔태스크 매칭·commit/PR 매칭 전부 결정론.

**`deliver/ask-team`** — PM이 팀원에게 질문하고 답을 수집하는 비동기 채널. Gmail/Notion/Zoom MCP 활용. `--mode ask`(초안 생성, 자동발송 불가), `--mode pull-answers`(스레드·회의록에서 답 수집), `--mode digest`(요약 → decision-log/ticket-bridge 라우팅). Gmail send 도구 부재로 구조적 자동발송 불가.

**`deliver/sprint/references/track-probe.sh`** — PostToolUse 훅으로 등록되는 probe. Write/Edit/NotebookEdit 이벤트마다 ts·loc_delta·task·exit_code를 `.track/actual_log.jsonl`에 append. tokens는 훅 페이로드에 없어 N/A(Rule 8 정직 처리).

---

## [0.13.0] — 2026-05-27

> **사용자 영향**: conductor 자동 파이프라인 연결 강화(Phase 0 PRD→플랜 자동생성·COGS 3단계·sprint 모드). tc-gate에 PRD 링크 assertion 추가(3타입). COGS gate/MCP gate 핵심 경로 버그 수정. 스킬 수 31 유지.

### Changed — 스킬 기능 강화

**`deliver/conductor`** — 3가지 강화:
- **Phase 0 신설**: `harness/PRD.md` 존재 확인 후 `harness/implementation-plan.md` 자동 생성. PRD §7·§11 읽어 태스크 단위 플랜 생성 + `depends_on` 의존 관계 명시. 파이프라인 brainstorm → prd → conductor 자동 연결.
- **Step E (COGS 영향 검토)**: 태스크 완료 후 `harness/build-gate/cogs_result.json` 기반 LLM 호출 패턴 검토. 예측 범위 초과 시 `CONDITIONAL_PASS`.
- **`--mode sprint`**: `depends_on: []` 독립 태스크는 병렬 서브에이전트 동시 디스패치, 의존 태스크는 순차 유지. Spec/Quality 리뷰 생략 대신 COGS 검토는 마지막에 유지.

**`deliver/conductor/prompts/spec-reviewer.md`** — PRD 로드 필수화: `docs/PRD.md 존재 시` 선택 → `harness/PRD.md` 필수 로드. 없으면 FAIL. §3·§11·§14·§7 4항목 전수 확인.

**`deliver/ui-validate`** — `--check tc-gate` assertion 엔진 추가:
- QA_CHECKLIST TC 행에 `Expected State` 8번째 컬럼 추가 (선택). 없거나 `—`이면 기존 스크린샷 전용 동작.
- 지원 assertion 3타입: `url_contains:<path>` / `element_exists:<selector>` / `element_text:<selector>:<text>`
- `summary.json`에 `critical_assertion_fails` 필드 추가.
- assertion이 TC-ID → PRD §11/§14까지 추적 가능.

**`hplan/commands/harness-build`** — Phase 8 ④ UI Evidence Gate에 `BLOCK_ASSERTION_FAILED` 상태 추가. Critical TC assertion 실패 시 차단.

### Fixed

- `cogs_sentinel.py`: `_validate_params()` 추가 — 음수/0/범위 초과 입력 시 `SystemExit`. GREEN 오판정 경로 차단.
- `hplan_mcp/server.py`: `product_gate()` — `checkpoint.json` 승인 + `cogs_result.json` GREEN/CONDITIONAL_GO 실제 검사. `handoff()` — Product Gate 미통과 시 블록, `force=True`는 `force_override` audit 플래그.

---

## [0.12.0] — 2026-05-27

> **사용자 영향**: brainstorm 스킬 신설(31개). conductor 지속 실행 강화. ui-validate TC 스크린샷 증거 수집(tc-gate). pm-engine 기술 결정 기록(save-decision)·코드베이스 인덱싱(index-codebase). prd 설계 시각화(design-shotgun).

### Added — 신규 스킬 1개

**`hplan/brainstorm`** — Phase 0 Worth-Building 3문 체크(특정 사람? / 우회로? / 행동 변화?) → Phase 1 1문1답 대화 설계(2-3가지 접근법 제시) → Phase 2 Signal Gate Bootstrap(harness/pain.md seed · brainstorm-assumptions.md · PRD-draft-section1.md 3개 artifact 생성). 제품을 만들기 전에 "만들 가치가 있는가"를 결정론적으로 검증한다.

### Changed — 기존 스킬 기능 확장

**`deliver/conductor`** — Continuous Execution 기본 동작으로 변경(이전: 단계별 확인 기본, 이제 `--confirm-plan`으로 opt-in). PRD-aware 모델 선택: §7-11(설계·배포·운영) → opus, §1-6(발견·설계) → sonnet, mechanical → haiku. 외부 프롬프트 템플릿 3개 신설(`prompts/implementer.md`, `prompts/spec-reviewer.md`, `prompts/quality-reviewer.md`) — spec-reviewer가 PRD §3/§11/§14/§7 교차 검증.

**`deliver/ui-validate`** — `--check tc-gate [URL]` 5번째 검사 모드 추가. `harness/QA_CHECKLIST.md`의 TC-ID를 파싱하여 Playwright로 URL 스크린샷을 찍고 `harness/ui-evidence/`에 시각 증거 저장. `summary.json`에 `evidence_type: "screenshot_only"` 명시 — 자동 assertion 없음, PM/QA 육안 검토용. `deliver/skills/ui-validate/scripts/pw_runner.py` 신설.

**`operate/pm-engine`** — `--mode save-decision`: 기술 결정을 `harness/tech-decisions/TD-NNN.yaml`(id·date·decision·alternatives·prd_link·evidence·outcome 필드)로 저장, post-retro 시 outcome 업데이트. `--mode index-codebase`: package.json/pyproject.toml/README 스캔 후 기존 TD와 교차 비교해 미기록 기술 결정 후보 제안.

**`deliver/prd`** — `--mode design-shotgun` 추가. PRD §11(Output Spec) 해석 차이를 기반으로 HTML 변형 4개 생성: variant-A(스텝퍼/탭), B(모달/오버레이), C(미니멀 폼), D(프로그레시브 공개). 출력: `harness/design-variants/variant-{A-D}.html` + `comparison.md`. §11 존재 여부는 `grep`으로 결정론 판정(LLM 호출 전).

### Changed — 커맨드 기능 확장

**`hplan/commands/harness-build`** Phase 8 ④ — UI Evidence Gate 추가(5-state 결정론 게이트). `harness/QA_CHECKLIST.md` 존재 여부로 UI 제품 판정 → SKIP(백엔드 전용) / PASS / BLOCK_MISSING(`summary.json` 없음) / BLOCK_EMPTY(TC 0개) / BLOCK_INCOMPLETE(Critical TC 스크린샷 미완).

### Fixed

- `pw_runner.py` — TC 파싱을 정규식에서 split 방식으로 교체. `|` 문자를 셀 내부에 포함하는 행도 정확히 파싱. TC가 0개면 `sys.exit(1)` fail-loud(이전: 빈 리스트 silent return).
- `harness-build` ④ — `|| echo "SKIP"` 패턴 제거. QA_CHECKLIST.md 부재 시만 SKIP, 존재하지만 summary.json 없으면 BLOCK_MISSING으로 분리. (이전: 어떤 실패든 SKIP으로 통과)
- `pm-engine save-decision` — TD 번호를 `wc -l + 1`(삭제 시 충돌)에서 `max + 1` 방식으로 수정. TD 덮어쓰기 즉시 에러 처리 추가.
- `prd design-shotgun` — §11 섹션 존재 여부를 LLM 판단에서 `grep -in` 결정론 검사로 교체(Rule 5 준수). 0매칭 → 즉시 fail loud.
- `validate_plugins.py` — `EXPECTED_ACTIVE_SKILLS` 30 → 31 갱신(brainstorm 신설 반영).

---

## [0.11.0] — 2026-05-26

> **사용자 영향**: 스킬 48→30 통합 (Conductor·QA Checklist 신규, 18개 제거/병합). Spec Compliance Review discoverability 개선. 배포 후 회고(post-retro) Phase 추가. Cursor MCP 설정 예시 추가. pm-engine --mode save 빠른 메모 기능 추가.

### Added — 신규 스킬 2개

**`deliver/conductor`** — 태스크별 fresh subagent 디스패치 + 2단계 게이트(spec→quality) 반복. parallel-team의 역할 병렬 패턴과 달리, 구현 → Spec Compliance Review → Quality Gate 순서를 태스크마다 반복해 품질을 강제한다.

**`deliver/qa-checklist`** — `docs/PRD.md` §3(ICP)·§11(테스트 전략)·§14(실패 시나리오) 기반 QA 체크리스트 자동 생성. TC를 critical/major/minor 3등급으로 AI 분류, 디바이스·환경 링크 포함. 출력: `harness/QA_CHECKLIST.md`.

### Added — 커맨드 기능 확장

**`harness-build --step spec-review|quality-gate`** — `argument-hint` 및 `description` 프론트매터에 명시적으로 추가해 discoverability 개선. 기존에 Phase 7·8로 존재했으나 슬래시 커맨드 자동완성에서 노출되지 않던 문제 해결.

**`harness-verify --spec`** — `--spec` 단축 플래그 추가. `harness-build --step spec-review`로 라우팅해 개발 완료 후 즉시 PRD 준수 여부를 확인할 수 있다.

**`harness-operate --mode post-retro`** — 배포 후 closed-loop 회고 Phase 추가. 원래 Evidence Gate 8개 축 예측 vs 실제 사용자 행동 대조, COGS 예측 vs 실제 비용 비교. 판정: HYPOTHESIS_CONFIRMED / PARTIAL_MATCH / HYPOTHESIS_WRONG. 결과는 `harness/operate/post-retro-YYYY-MM-DD.md`에 저장.

**`hplan_mcp/README.md`** — Cursor 전용 `.cursor/mcp.json` 설정 예시 추가. Windsurf/Kiro 설정 파일 위치 명시.

**`operate/pm-engine --mode save`** — 세션 중 발견한 인사이트를 TK 추출 플로우 없이 즉시 `PM-ENGINE-MEMORY.md`에 저장하는 빠른 메모 기능 추가. 저장 형식: `TK-QUICK-[YYMMDDHHmm]`.

### Changed — 스킬 통합 48→30 (-18 제거/병합, +7 신규)

| 플러그인 | 이전 | 이후 | 변경 |
|---|---|---|---|
| hplan | 8 | 7 | pmf-gate 제거 (harness-operate post-retro 흡수) |
| discover | 6 | 4 | assumptions+build-or-buy 통합; agent-gtm 제거 |
| architect | 7 | 5 | biz-model+moat+growth-loop → strategy 통합 |
| deliver | 13 | 8 | +conductor·qa-checklist 신규; agent-setup·sprint 통합; 5개 제거 |
| operate | 14 | 6 | ops-review·portfolio 신규 통합; pm-decision→pm-engine 흡수; 5개 제거 |
| **합계** | **48** | **30** | |

**통합 원칙**: "커맨드에 이미 있으면 스킬이 아니다." `agent-plan-review`(→harness-build Phase 7), `ctx-budget`(→prd 스킬 내부), `harness-design`(→harness-build 커맨드)처럼 커맨드에 흡수된 스킬들을 제거. 고유 내용은 흡수 대상 스킬에 이식 후 삭제.

### Fixed

- `validate_plugins.py`: `EXPECTED_ACTIVE_SKILLS` 46 → 30으로 갱신 (v0.11.0 통합 반영)

---

## [0.10.2] — 2026-05-26

> **사용자 영향**: PostToolUse 훅에 MD→HTML 자동 렌더러 추가. hplan 커맨드가 `.md`를 Write하면 같은 위치에 `.html`이 자동 생성되어 브라우저에서 즉시 열 수 있다.

### Added — MD→HTML Auto-Renderer (`hplan/scripts/`, `hplan/templates/`, `hooks/PostToolUse.sh`)

**L3 Hooks 확장 — PostToolUse MD→HTML 렌더링**

`hooks/PostToolUse.sh`에 `.md` Write 이벤트 감지 블록 추가. `hplan/scripts/md_renderer.py`를 호출해 MD 파일을 파싱하고 `.html`을 자동 생성한다. 훅은 항상 `exit 0`으로 비차단 실행된다.

**`hplan/scripts/md_renderer.py`** — 핵심 변환 엔진
- 경로 패턴 기반 템플릿 선택 (`_TEMPLATE_MAP`, 11개 규칙)
- `__DATA_JSON__` 플레이스홀더 치환으로 Python → 브라우저 JS 데이터 전달
- 9개 제외 경로 패턴 (`CHANGELOG`, `CONTRIBUTING`, `README` 등)
- Python stdlib only (re, json, pathlib)

**`hplan/scripts/parsers/`** — 11개 MD 파서 (generic + 10개 전용)

| 파서 | 대상 파일 | 주요 추출 필드 |
|---|---|---|
| `generic` | 모든 `.md` | title, headings, has_mermaid, body_md |
| `evidence_gate` | `harness/evidence/*.md` | score, decision, axes(8축), weak_axes |
| `cogs_sentinel` | `harness/cogs.md` | scenarios(margin/label), cogs_ceiling, cogs_ok |
| `gate_state` | `harness/build-gate/*.md` | conditions(status ✅/❌), passed_count, total |
| `pain_board` | `harness/pain.md` | cards(tag/quote), interview_count, signal_gate_met |
| `ost_viewer` | `harness/ost.md` | mermaid_code, solutions |
| `market_intel` | `harness/market.md` | table(headers/rows) |
| `architecture` | `harness/ARCHITECTURE.md` | memory_items, routing_table |
| `sprint_tracker` | `harness/sprint.md` | items(done/blocker), pct, cogs_ok |
| `prd_reader` | `docs/PRD.md` | evidence_score, cogs_verdict, state, sections |
| `design_system` | `.design/design-system.md` | colors(hex/rgb), typography, tailwind_tokens |

**`hplan/templates/`** — 11개 HTML 템플릿
- Tailwind CSS CDN + Chart.js 4.4.2 + Mermaid 11 + marked.js 9
- `createElement`/`textContent` 전면 적용 (XSS 안전)
- 동적 차트 max 값 (`Math.max(fallback, ...data)` 패턴)
- `__DATA_JSON__` → JSON.parse로 Python 파싱 결과 수신

**`.gitignore`** — 자동 생성 HTML 제외 패턴 추가
```
harness/**/*.html
docs/*.html
.design/*.html
specs/**/*.html
```

**테스트**: 143 passed, 0 failed

---

## [0.10.1] — 2026-05-23

> **사용자 영향**: 2차 Codex adversarial review 수정 + 5 페르소나 피드백 반영. `audit()`·`list --phase` KeyError 수정, Signal Gate pre-commit staged index 기준 강화, Evidence Source 페널티 자동 적용, Phase 5·6 빌드 리뷰 추가, PM 용어 설명 추가.

### Fixed — `hplan/scripts/decision_log.py`

HITL 레코드(`type: "hitl"`)와 gate 레코드 스키마 불일치 두 건 수정:

**[HIGH] `audit()` KeyError 방지**
- `audit()` 진입 전 `type != "hitl"` 필터 추가
- HITL 레코드에는 `decision` 필드가 없어 `Counter(e["decision"] ...)` 호출 시 KeyError 발생하던 문제 제거

**[HIGH] `list --phase` 필터링 정합성**
- HITL 레코드: `phase` 필드 기준으로 필터
- gate 레코드: `gate` 필드 기준으로 필터
- 이전: 혼재된 레코드에서 특정 타입만 누락되거나 빈 결과 반환하던 버그 제거

### Fixed — `scripts/install-hooks.sh`

**[HIGH] Signal Gate pre-commit — staged index 기준으로 변경**

- 이전: `[ -f "$sdoc" ]` — working tree 파일 존재 여부 확인 (bypass 가능)
- 변경: `git cat-file -e ":$sdoc" 2>/dev/null` — staged index 기준 확인
- 효과: `git add` 없이 harness 문서를 파일 시스템에만 두고 commit하는 bypass 차단
- 에러 메시지도 "staged index" 반영

### Fixed — `README.md`

**[MEDIUM] 삭제된 per-plugin 커맨드 4개 섹션 참조 제거**

| 이전 (삭제됨) | 현재 |
|---|---|
| `/discover` · `/validate` | `/harness-discover` |
| `/architecture` · `/strategy-review` | `/harness-plan` |
| `/write-prd` · `/set-okr` · ... | `/harness-build` |
| `/health-check` · `/cost-review` · ... | `/harness-operate` |

---

### Added — Signal Gate v2: Evidence Source 페널티

**`hplan/scripts/generate_report.py`**

- `_EVIDENCE_SOURCE_PATTERNS` 딕셔너리 추가: 4개 Signal Gate 문서별 출처 섹션 패턴 정의
- `evidence_source_penalty(root)` 함수: 출처 섹션 없는 문서당 -5점 자동 적용 (최저 0점)
- 스코어 계산에 페널티 반영, 결과에 "Evidence Source 누락 페널티: -Npt" 표시

**`hplan/commands/hplan.md`**

- Step 2 앞 "Signal Gate v2 — Evidence Source 요건" 블록 추가
- 4개 문서별 필요 출처 형식 명시: 날짜 인터뷰, 가격 링크, 리포트 DOI/URL, 직접 테스트 노트

### Added — `hplan/commands/harness-build.md`

**Phase 5 — Spec Compliance Review**

- PRD Section 3 ICP 정합성 체크: 실제 사용자가 PRD ICP에 해당하는지 확인
- PRD Section 9 비기능 요건 vs 실측값 비교표 생성
- PRD Section 14 실패 모드 fallback 커버 확인
- `--step spec-review` 플래그 지원

**Phase 6 — Quality Gate**

- 테스트 커버리지 기준: happy path + 주요 실패 시나리오 최소 1개
- 기술 부채 마커 임계값: ≤5 통과 / 6-15 경고 / ≥16 차단
- 보안 기본 점검: 하드코딩 시크릿, 미검증 외부 입력
- `--step quality-gate` 플래그 지원

### Added — `hplan/hooks/gate_guard.py`

**PLACEHOLDER_PATTERNS 확장 (+7개)**

기존 TBD/미정/추후/나중에 외에 vague ICP 표현 탐지 패턴 추가:
- `여러 고객`, `많은 사람`, `일반 사용자`, `target user` (비구체적 타겟)
- `TODO`, `미기입`, `검토 예정` (미완료 마커)

### Added — Interview Discipline

**`hplan/commands/harness-discover.md`**

Signal Gate 이전 "Interview Discipline" 섹션 신설:

| 규칙 | 내용 |
|---|---|
| 1 | 질문 1개씩 — 멀티 질문 금지 |
| 2 | Multiple choice 우선 — open-ended는 필요할 때만 |
| 3 | AI 생성 페르소나 ≠ 인터뷰 증거 — 실제 인터뷰가 없으면 interview_lines = 0 |
| 4 | Source/Date/Quote 3필드 필수 — Phase 5 전 최소 3건 |

### Added — PM 용어 설명 (4개 커맨드 파일)

`harness-discover.md` · `harness-plan.md` · `harness-build.md` · `harness-operate.md`

각 파일에 2가지 방식으로 PM 용어 접근성 개선:
1. **"왜" 블록**: 각 Phase 앞 1-2문장으로 이 단계가 왜 필요한지 설명
2. **Inline 용어 설명**: Signal Gate, ICP, CONDITIONAL_GO, COGS, Orchestration, 3-Tier, Moat, Execution Handoff, KPI, North Star, P95/P99, Burn Rate 등 첫 등장 시 blockquote 설명

---

## [0.10.0] — 2026-05-23

> **사용자 영향**: ADK (Agent Development Kit) 5-Layer 구조 완성. `git clone` + `bash scripts/install-hooks.sh` 한 번으로 모든 레이어가 활성화됩니다.

### Added — ADK L1 Memory: Root `CLAUDE.md`

`CLAUDE.md` (repo root 신규)

- **9개 행동 원칙** 내장: Think Before Coding · Simplicity First · Surgical Changes · Goal-Driven Execution · 모델은 판단 작업에만 · Tests Verify Intent · Checkpoint · Fail Loud · Agent Scope Declaration
- **hplan Gate Rules** 섹션: Signal Gate 4문서 작성 기준, No-Placeholder 규칙, Decision Log 필수성
- **ADK Layer 표** 포함: L1~L5 어떤 파일이 어느 레이어인지 한눈에 확인
- 사용자는 이 파일을 clone 후 hplan Context 섹션만 프로젝트에 맞게 수정하면 바로 적용

### Added — ADK L3 Guardrail: `hooks/` 디렉토리

세 개의 Claude Code hook shell 래퍼 신설:

| 파일 | 이벤트 | 동작 |
|------|--------|------|
| `hooks/SessionStart.sh` | 세션 시작 | Build Gate checkpoint 상태 + Signal Gate 문서 인벤토리 출력 |
| `hooks/PreToolUse.sh` | Write/Edit 전 | `hplan/hooks/gate_guard.py` 위임 — checkpoint 없으면 차단 |
| `hooks/PostToolUse.sh` | Write/Edit 후 | API 키 / secret 패턴 스캔 → 경고 출력 (차단 안 함) |

`hooks/README.md` 포함: 수동 테스트 명령, 등록 방법, 제거 방법 문서화.

### Updated — `scripts/install-hooks.sh`: Claude Code 훅 등록 추가

기존: git pre-commit hook만 설치  
변경 후:

1. git pre-commit hook (기존 유지)
2. Claude Code hook 등록 — `.claude/settings.json`에 SessionStart · PreToolUse · PostToolUse 3개 항목 자동 추가
3. `--remove` 옵션도 양쪽 모두 제거하도록 업데이트

### Updated — `README.md` + `hplan/PLUGIN.md`

- README: "Option 2: Clone Locally (Full ADK Stack)" — ADK 5-layer 테이블 추가
- README: 버전 배지 `0.9.9` → `0.10.0`
- PLUGIN.md: Cross-Cutting Assets에 CLAUDE.md(L1) · hooks/(L3) 항목 추가

---

## [0.9.9] — 2026-05-23

> **사용자 영향**: Release Polish — 배지·버전 설명·Quick Start·커맨드 목록 업데이트. 8역할 병렬 팀 공식 등록.

### Added — 8-Role Parallel Team (`deliver/skills/parallel-team`)

**`deliver/skills/parallel-team/SKILL.md`** 전면 재작성

기존 generic parallel dispatch → 역할 기반 기본 팀 정의:

| 역할 | 담당 |
|---|---|
| 디자이너 | 화면 레이아웃, 컴포넌트 디자인, 디자인 시스템 설계 |
| 개발자 | 코드 구현, 버그 수정, 기능 추가, 리팩토링 |
| 품질담당자 | 테스트 코드 작성, 엣지 케이스 발굴, 회귀 방지 |
| 마케터 | 랜딩 카피, SEO, 출시 메시지, 채널별 콘텐츠 |
| 리서처 | 경쟁사 분석, 시장 조사, 기술·라이브러리 비교 |
| 배포 담당자 | 인프라 셋업, 환경 변수 관리, 도메인 연결, CI/CD |
| 까칠이 | 팀원 결과물 약점 발굴·반박 (adversarial reviewer, 항상 마지막) |
| 보안 담당자 | 시크릿 노출 검사, 권한·취약점 점검 (머지 전 블로킹 게이트) |

Role Selection Guide(키워드 기반 자동 선택) + 최소 팀 4인 규칙 + 까칠이 Protocol + 보안 게이트 체크리스트(7항목) 추가.

### Changed — README / README-ko 업데이트

- 배지: `skills-65` → `skills-72`, `version-0.9.2` → `version-0.9.9`
- 버전 설명: v0.9.4–v0.9.9 변경 요약 반영
- Quick Start: `/harness-doctor` 설치 검증 단계 + `/harness-*` 라이프사이클 예시 추가
- 커맨드 목록: 9개 실제 커맨드로 정정 (`harness-*` 명명 반영)

### Verified

- `python3 validate_plugins.py`: ✅ 5 plugins, 55 active + 17 alias = 72 skills, 9 commands, 0 errors

---

## [0.9.8] — 2026-05-23

> **사용자 영향**: 큰 태스크를 자동으로 2주 단위로 분할하는 Scope Decomposition 체크리스트 추가. PRD v0.1→v0.2→v0.3 버전 체인이 harness-build Phase 4 도입부에 명시되어 "지금 어디까지 왔나"를 한눈에 파악 가능.

### Added — Scope Decomposition Check (`harness-plan`)

`harness/ARCHITECTURE.md` 생성 직후, Execution Handoff 진입 전에 **Scope Decomposition Check** 단계 삽입:

- 각 태스크에 3가지 질문: 2주 내 완료 가능? / 독립 검증 가능? / 산출물 파일명 명확?
- 2주 초과 태스크 → Wave A(핵심 happy path) / Wave B(에러 처리) / Wave C(최적화) 분할
- 분할 완료 후 `harness/ARCHITECTURE.md` 업데이트 → Execution Handoff 진행

### Added — PRD Living Document 안내 (`harness-build`)

Phase 4 도입부에 PRD 버전 체인 시각화 블록 삽입:

```
v0.1 — Signal Gate + harness-build: 사용자·문제·범위·에이전트 사양 초안
v0.2 — harness-plan 완료 후: 오케스트레이션·Tier·메모리·라우팅 결정 반영
v0.3 — harness-operate 피드백 후: KPI·실패 모드·개선 계획 반영
```

---

## [0.9.7] — 2026-05-23

> **사용자 영향**: Signal Gate 문서에 증거 출처가 없으면 경고 또는 차단. "잘 쓰인 문서"와 "진짜 증거 기반 문서"를 구분하기 시작.

### Added — Evidence Source Check (`hplan.md` + `gate_guard.py`)

**문제**: Signal Gate = 문서 완성도 측정, NOT 시장 가설 검증. 의견(Opinion)을 증거(Evidence)처럼 쓰는 경로 존재.

**수정**:

1. **`hplan/commands/hplan.md`** — Signal Gate 섹션에 `Evidence Source 요건 (v0.9.7)` 테이블 추가:
   - pain.md: 인터뷰 날짜(`YYYY-MM-DD`) 또는 `## Evidence` 섹션 필수
   - cogs.md: 가격 출처(provider pricing) 또는 `## Evidence` 섹션 필수
   - market.md: 시장 규모 출처(산업 리포트, TAM source) 또는 `## Evidence` 섹션 필수
   - competitors.md: 직접 테스트 또는 사용자 발화 인용 필수

2. **`hplan/hooks/gate_guard.py`** — `evidence_source_check()` 함수 추가:
   - `EVIDENCE_PATTERNS` 상수: 4개 문서 × 문서별 3개 패턴
   - 4개 모두 미충족 → **차단(exit 2)**
   - 일부 미충족 → **경고** 출력 후 계속 진행

---

## [0.9.6] — 2026-05-23

> **사용자 영향**: PM이라면 누구나 써야 할 4개 계획 규율이 명령어에 내장됨. "기준 없이 기능부터" 패턴을 구조적으로 차단.

### Added — 4 Planning Disciplines

**G1 — Criteria First** (`harness-build.md` Pre-Step 4-0):
- PRD 섹션 작성 전 North Star Metric + Business KR 1–2개 + Anti-Metric 1개 먼저 정의
- 이 기준이 Section 4 결정 매트릭스와 Section 5 Out-of-Scope의 필터로 작동
- 근거: "기능을 먼저 쓰면 기능이 목표를 정의한다"

**G2 — Named Artifacts** (`harness-plan.md` Planning Disciplines):
- Phase 시작 직후 산출물 파일명·섹션명 먼저 선언 의무
- 5 Phase 산출물 테이블 (Orchestration → 3-Tier → Memory → Routing → Architecture Doc)

**G3 — Decision Commit** (`harness-plan.md` Planning Disciplines):
- 모든 HITL 결정 지점: 옵션 3개 이상 → 정확히 1개 커밋
- "A 또는 B 방향으로 갈 수 있습니다" 같은 미결 처리 금지
- `decision_log.py hitl` 기록 필수

**G4 — Phase Context Budget** (`harness-plan.md` Planning Disciplines):
- 각 Phase 최대 3개 파일 로드 원칙
- Phase 시작 전 전체 프로젝트 파일 일괄 Read 금지

---

## [0.9.5] — 2026-05-22

> **사용자 영향**: 8개 라이프사이클·유틸리티 커맨드가 `harness-*`로 통일. `/hplan` 게이트 브랜드 진입점은 유지.

### Changed — `harness-*` 커맨드 명명 통일

8개 커맨드 파일 rename + 66개 크로스 레퍼런스 업데이트:

| 이전 | 이후 |
|---|---|
| `/hplan-discover` | `/harness-discover` |
| `/hplan-plan` | `/harness-plan` |
| `/hplan-build` | `/harness-build` |
| `/hplan-operate` | `/harness-operate` |
| `/hplan-exclude` | `/harness-exclude` |
| `/hplan-handoff` | `/harness-handoff` |
| `/hplan-verify` | `/harness-verify` |
| `/hplan-doctor` | `/harness-doctor` |

`/hplan` (Evidence + Product + COGS 3-gate) 브랜드 진입점은 그대로 유지.

### Added — Execution Handoff (항목 E, `harness-plan`)

ARCHITECTURE.md 작성 완료 후 3가지 실행 전략 HITL:
- A) 단독 실행 → `/harness-build`
- B) 병렬 팀 구성 → `/deliver:parallel-team`
- C) 단계적 실행 → `/harness-build --step`

---

## [0.9.4] — 2026-05-22

> **사용자 영향**: Signal Gate 문서에 TBD/미정/추후/다양한 사용자 같은 모호 표현이 있으면 빌드 차단. 인터뷰 질문을 한 번에 하나씩 도출하도록 강제.

### Added — No-Placeholder Gate (항목 B, `gate_guard.py`)

**문제**: Signal Gate가 존재 여부만 확인하고, 내용이 모호해도 통과시켰음.

**수정**: `PLACEHOLDER_PATTERNS` + `placeholder_gate_check()` 추가 (`gate_guard.py`):
- 6개 패턴: TBD · 미정 · 추후 · 나중에 · 다양한 사용자 · 여러 ...층
- 감지 시 exit 2 (빌드 차단), 구체적인 내용 교체 안내

### Added — Interview Discipline (항목 G6, `harness-discover`)

Phase 2 가정 분석에 **Interview Discipline** 블록 삽입:
- 가정 검증 질문을 한 번에 하나씩 도출
- yes/no 또는 객관식 형태로 설계 권장
- 이전 답변 기반으로 다음 질문 조정 (대화형 탐색)

---

## [0.9.2] — 2026-05-22

> **사용자 영향**: 30개 커맨드 → 9개로 통합. 4개 라이프사이클 커맨드(`/hplan-discover`, `/hplan-plan`, `/hplan-build`, `/hplan-operate`)에 `--mode`/`--step` 파라미터 라우팅이 내장되어, 이전에는 별도 커맨드를 설치해야 했던 세밀한 제어가 파라미터 한 줄로 가능합니다.

### Changed — 30 commands → 9 commands 통합

**파라미터 라우팅 패턴**: 각 라이프사이클 커맨드에 `$ARGUMENTS`에서 `--mode`/`--step` 플래그를 파싱하는 Routing 테이블 내장.

| 커맨드 | 흡수된 커맨드 | 파라미터 |
|--------|-------------|---------|
| `/hplan-discover` | `discover.md`, `validate.md` | `--mode opp\|assumptions\|cost\|build-or-buy\|validate` |
| `/hplan-plan` | `architecture.md`, `strategy-review.md` | `--mode orchestration\|3-tier\|memory\|routing\|review` |
| `/hplan-build` | `hplan-evidence.md`, `hplan-product.md`, `hplan-cogs.md`, `hplan-scope-guard.md`, `write-prd.md`, `set-okr.md`, `sprint.md`, `craft-init.md`, `craft-lint.md`, `track-init.md`, `track-status.md`, `track-retro.md` | `--step evidence\|product\|cogs\|prd\|okr\|sprint\|craft-init\|craft-lint\|track-init\|track-status\|track-retro\|scope` |
| `/hplan-operate` | `health-check.md`, `cost-review.md`, `decide.md`, `extract.md`, `tk-to-instruction.md` | `--mode kpi\|reliability\|cost\|improve\|extract\|decide\|tk` |

### Removed — 21 개별 커맨드 파일 삭제

discover, architect, deliver, operate 플러그인의 개별 커맨드 `.md` 파일 21개가 라이프사이클 커맨드에 흡수되어 삭제됨. `hplan` 플러그인 utility 5개(`/hplan`, `/hplan-exclude`, `/hplan-handoff`, `/hplan-doctor`, `/hplan-verify`)는 유지.

### Design — 파라미터 없으면 전체 플로우, 있으면 해당 Phase만

- 플래그 없음: 대부분의 Phase를 순서대로 실행하며 Checkpoint에서 사용자 확인 대기
- `--mode`/`--step` 지정 시: 해당 Phase만 실행하고 종료 (세밀한 제어 및 재실행 지원)
- 스킬 참조 포함하되 instructions 인라인 — 다른 플러그인 미설치 상태에서도 동작

### Verified

- `python3 validate_plugins.py`: ✅ 5 plugins, 55 active + 17 alias = 72 skills, **9 commands**, 0 errors, 3 warnings(pre-existing)

---

## [0.9.1] — 2026-05-21

> **사용자 영향**: Evidence Gate 루브릭이 `generate_report.py` 실제 구현과 이제 일치합니다 — 7개 기준/80점 기준에서 8개 기준/75점 기준으로 통일. `/hplan-doctor` 로 훅·체크포인트·레지스트리 상태를 한 번에 진단 가능. 컨설턴트 워크플로에서 `--profile` 플래그로 클라이언트별 exclusions 격리. README.md 영어 전용 정리.

### Fixed — Evidence Gate 루브릭 불일치 (항목 A)

**[bug] `hplan.md` 인라인 루브릭 ↔ `generate_report.py` 구현 불일치**
- 원인: `hplan.md` 에 7개 기준(각 15/15/15/15/15/15/10pt), 80/60 임계값이 수동 기술되어 있었고, `generate_report.py` 는 8개 기준(20/15/15/10/15/10/10/5pt)과 75/55/35 임계값으로 실제 구현되어 있었음
- 영향: 같은 아이디어가 `/hplan` 에서는 80점 필요, `/hplan-evidence` 에서는 55점에서 interview 처리되는 혼란 발생
- 수정: `hplan.md`, `hplan-evidence.md`, `evidence-rubric/SKILL.md` 를 `generate_report.py` 실제 구현 기준으로 동기화
  - 기준 7개→8개 (Switching trigger 추가, 점수 배분 재정렬)
  - 임계값 80/60 → 75/55/35
  - build 판정 조건에 `interview_lines ≥ 2 AND economic_pain` 필수 명시 (anti-gaming, 이미 스크립트에 구현되어 있었으나 미문서화)
  - 각 판정별 "다음 3 액션" 블록 추가 (GO / INVESTIGATE / HOLD)

### Added — `/hplan-doctor` 설치 진단 커맨드 (항목 B)

**`hplan/commands/hplan-doctor.md`** — 신규
- 5개 체크 항목 자동 진단: Hook 등록, Hook 실행(exit=2 = 정상), Checkpoint 상태, Exclusions 레지스트리 유효성, Git pre-commit 훅
- 출력: `[ PASS/WARN/FAIL ]` 형식 + Summary + Recommended actions
- 온보딩 시 "훅이 실제로 작동하는지 어떻게 아냐?" 질문에 대한 결정적 답변

### Added — Exclusions Registry `--profile` 지원 (항목 E)

**`hplan/scripts/exclusions_registry.py`**
- `registry_path()` 에 `profile` 파라미터 추가: `--profile client-acme` → `harness/profiles/client-acme/exclusions.jsonl`
- `add`, `check`, `list` 서브커맨드 모두 `--profile` 인자 지원
- backward-compatible: `--profile` 미지정 시 기존 `harness/exclusions.jsonl` 동일
- `.gitignore` 에 `harness/profiles/` 추가 (클라이언트 kill-decision 데이터 보호)

### Fixed — README.md 영어 전용 정리 (항목 F)

9개 한국어 라인 영어 번역:
- 원칙 테이블 헤더(`hplan 원칙 | 대립 가정` → `hplan Principle | Opposing Assumption`)
- 원칙 3행 전체 번역 (conversation↓ docs↑, big tasks step by step, validate first build later)
- 4개 스킬 "When to use" 셀 번역 (design-reference, design-token, prd, mobile-check)

### Changed — Remotion Lifecycle 영상 v0.9.0 반영 (항목 G)

**`tools/intro-video/src/scenes/v8d-05-Lifecycle.tsx`**
- STAGES: 9개 → 5개 (hplan/discover/architect/deliver/operate)
- 타이틀: `"9-stage lifecycle · 62 skills"` → `"5-plugin lifecycle · 65 skills"`
- 자막: `"v0.9 · hplan → discover → architect → deliver → operate"`

**`tools/intro-video/src/Root.tsx`**
- `HplanV9Core` composition 추가 (기존 `HplanV8CoreTrack` 유지, backward-compatible)

### Refactored — `evals/` → `operate/evals/` 이동

- 스킬 품질 측정(eval)은 `operate` 레이어에 귀속 — 5-plugin 구조 일관성 확보
- `README.md`, `README-ko.md`, `CONTRIBUTING.md` 경로 참조 갱신
- `git mv` 로 blame/log 이력 보존 (~100개 파일)

### Verified
- `python3 validate_plugins.py hplan`: ✅ 0 errors
- `python3 hplan/scripts/exclusions_registry.py add "test" --why "test" --reopen "never" --profile demo`: ✅ `harness/profiles/demo/exclusions.jsonl` 생성 확인
- `python3 hplan/scripts/exclusions_registry.py list`: ✅ 기존 글로벌 레지스트리 영향 없음
- `grep -n "[가-힣]" README.md | grep -v "한국어"`: ✅ 0건

---

## [0.9.0] — 2026-05-21

> **사용자 영향**: 플러그인 구조가 9단계에서 5플러그인(hplan/discover/architect/deliver/operate)으로 재편. `track` + `craft` 가 `deliver` 로 통합. `measure` + `learn` 이 `operate` 로 통합. 커맨드 네이밍 `hplan-*` 통일. 스킬 수 62개 → 65개.

### Changed — 5-Plugin 구조 전환

- **9-stage 구조 폐기**: `hplan → discover → architect → deliver → measure → learn` 에서 `hplan → discover → architect → deliver → operate` 5플러그인으로 단순화
- **deliver 통합**: `track` (A/B·실험) + `craft` (UI/디자인) 스킬이 `deliver` 플러그인으로 흡수
- **operate 신설**: `measure` + `learn` 스킬이 `operate` 플러그인으로 통합
- **커맨드 네이밍 정비**: 모든 hplan 커맨드 `hplan-*` 접두사 통일

### Added — 신규 스킬 (v0.9.0)

- `deliver/design-reference`, `deliver/design-token`, `deliver/mobile-check` 추가
- `hplan/pmf-gate` 스킬 추가 (Post-launch PMF 신호 루프)
- 총 65개 스킬 (v0.8.4 대비 +3)

---

## [0.8.4] — 2026-05-17

> **사용자 영향**: `/craft-lint` 가 잘못된 형식의 DESIGN.md 를 만나도 안전하게 fail 합니다 (traceback 없이 명확한 한국어 에러 메시지). 자체 regression test 2 종 (`evals/skill-uplift.py --test` + `scripts/validate-craft-lint.py --test`) 으로 미래 회귀 자동 차단. **`/craft-lint` / `/track-status` 같은 명령이 깨진 입력으로 인해 알 수 없는 traceback 으로 종료되는 일이 없어집니다.**
>
> **(내부 detail)** 3차 Codex adversarial review fix patch. v0.8.3 의 `isinstance(dict)` 검증이 top-level 만 보호 — nested schema (`colors: [{primary:blue}]` 또는 비-string key) 가 여전히 crash 가능했음. nested guard + regression suite 추가.

### Fixed — Codex 3차 검수 반영

**[medium] check_cross_ref() nested type guards** (`scripts/validate-craft-lint.py`)
- v0.8.3 의 약점: `load_yaml_block()` 이 top-level dict 만 검증. `check_cross_ref()` 가 `design.get("colors")` 가 dict 라 가정하고 `k.lower()` 호출 → valid YAML `colors: [{primary: blue}]` 또는 `colors: [1, 2]` 같은 nested list 면 AttributeError + traceback
- v0.8.4 fix:
  - `design.colors`: `isinstance(dict)` 검증 → 비-dict 면 controlled error ("dict 형식 필수")
  - `design.colors` key: `isinstance(str)` 검증 → 비-string key 면 controlled error
  - `design.typography`: 같은 nested guard 적용
  - 모든 비-dict / 비-string 경우 traceback 0, 명확한 안내 메시지

### Added — Regression Suite for craft-lint

`python3 scripts/validate-craft-lint.py --test`:
- 7 deterministic assertions for `check_cross_ref()`:
  - None / empty / non-dict (list, string) design
  - colors = list-of-maps (Codex 3차 finding 핵심 reproducer)
  - colors = list-of-int
  - colors = dict with int keys
  - typography = list (nested guard)
  - valid dict (no false positive)
- 두 번째 self-contained test 명령 (skill-uplift.py 옆) — CI 호환

### Verified
- `python3 scripts/validate-craft-lint.py --test`: ✅ all 7 pass
- `python3 evals/skill-uplift.py --test`: ✅ all 7 pass (v0.8.3 회귀 0)
- `validate_plugins.py`: 9 plugins / 62 skills / 26 commands / Errors 0 / Warnings 0

### Architecture — 3 라운드 Codex 검수 수렴

- v0.8.0~0.8.1 → 1차 review: 4 findings (3 high + 1 medium) → v0.8.2
- v0.8.2 → 2차 review: 3 findings (1 high + 2 medium) → v0.8.3
- v0.8.3 → 3차 review: 1 finding (0 high + 1 medium) → v0.8.4
- (예상) v0.8.4 → 4차 review: 0 findings 수렴 가능성

findings 수 4→3→1 수렴 + high 잔여 0. cross-model adversarial review 가 mechanical enforcement gate 의 정확한 self-correction 루프로 작동. 같은 Claude 의 self-review 였으면 직관적 fix 가 새 결함 도입한 것을 못 잡았을 것 — Codex 가 직접 `judge()` 호출, malformed schema process substitution 으로 traceback 위치까지 reproduce. 메모리 [[feedback_slide_review]] "2명 합의 + 90점+ 목표" 패턴의 가장 정밀한 사례.

---

## [0.8.3] — 2026-05-17

> **2차 Codex adversarial review fix patch.** v0.8.2 의 fix 자체가 새 결함을 도입한 것을 cross-model review 가 발견. 3 findings (1 high + 2 medium) 모두 해결 + self-contained regression test 추가.

### Fixed — Critical (Codex 2차 검수 반영)

**[high] judge() off-mode positive = baseline miss (재재설계)** (`evals/skill-uplift.py`)
- v0.8.2 의 잘못된 가정: off-mode 에서 should_trigger=True 쿼리는 `predicted == "none"` 이면 pass (정답 fallback 인정)
- 실제 결과: LLM 이 영리하게 "none" fallback 잘 하면 → off_pass_rate 1.0 → uplift 0 → 정상 스킬도 quarantine
- v0.8.3 fix: off-mode 의 should_trigger=True 는 **본질적으로 baseline miss** (이 스킬이 채우는 라우팅 빈 공간). 항상 `False` 반환.
- 검증: perfect-router 시나리오 (2 positives + 2 negatives 모두 정답) → on=1.0, off=0.5, uplift=+0.5 → promote ✅
- ETH -3pp 함정: on-mode 의 false positive 증가 → on_pass_rate 하락 → uplift 음수 → quarantine ✅

**[medium] DESIGN.md parsing 안전화** (`scripts/validate-craft-lint.py`)
- v0.8.2 의 약점: `load_yaml_block()` 이 markdown text 받으면 `yaml.YAMLError` 또는 scalar/list 반환 → `check_cross_ref()` 의 `design.get()` 호출이 AttributeError + 깨진 traceback
- v0.8.3 fix:
  - `load_yaml_block`: `yaml.YAMLError` catch + `isinstance(parsed, dict)` 검증 → 안전한 None 반환
  - `check_cross_ref`: design 인자 dict 타입 명시 검증 + controlled error 메시지 ("fenced ```yaml 블록 필수")
- 결과: 어떤 형식의 DESIGN.md 가 와도 craft-lint 가 traceback 없이 명확한 안내 메시지로 fail

**[medium] `.design/hierarchy-baseline.json` gitignore 누락 마감** (`.gitignore`)
- v0.8.2 의 누락: `/craft-init` 가 `hierarchy-baseline.json` 생성하지만 .gitignore 에 없음 → 첫 baseline 실행이 personal state 를 commit 에 노출
- v0.8.3 fix: `.design/hierarchy-baseline.json` 추가 (craft runtime ignore block 완성)

### Added — Self-contained regression test

`python3 evals/skill-uplift.py --test`:
- 7 deterministic assertions for `judge()` (on/off × positive/negative 4 cases + edge)
- Perfect-router uplift = +0.5 회귀 차단 (v0.8.2 의 false-quarantine 함정 재발 방지)
- CI 에서 모듈 import 없이 단일 명령으로 실행 가능

### Verified
- `python3 evals/skill-uplift.py --test`: ✅ all pass
- `validate_plugins.py`: 9 plugins / 62 skills / 26 commands / Errors 0 / Warnings 0
- v0.7.5..v0.8.2 회귀 0 (operate / track / craft / evals 모두 그대로)

### Architecture — 2 라운드 Codex 검수의 정합성

v0.8.0 (track + craft) → v0.8.1 (evals 시드) → v0.8.2 (1차 fix) → v0.8.3 (2차 fix). 두 라운드 모두 같은 패턴: cross-model adversarial review 가 self-review 가 못 본 logic 결함 발견. v0.8.2 fix 의 "off-mode positive 'none' pass" 정책이 직관적이었지만 실제로는 perfect-router 를 false-quarantine 시키는 함정이었음을 Codex 가 직접 `judge()` 호출로 검증해 잡음. 메모리 [[feedback_slide_review]] "2명 합의 + 90점+ 목표" 패턴의 가장 정확한 사례.

---

## [0.8.2] — 2026-05-17

> **Codex adversarial review fix patch.** v0.7.5..v0.8.1 검수에서 도출된 4 findings (3 high + 1 medium) 모두 해결. v0.8.0/v0.8.1 의 mechanical enforcement 약속을 진짜로 작동시키는 patch.

### Fixed — Critical (Codex 검수 반영)

**[high] skill-uplift judge() 로직 재설계** (`evals/skill-uplift.py`)
- 기존: off-mode 에서 target skill 카탈로그 제거 → 모델이 절대 선택 불가 → `judge()` 가 should_trigger 든 false 든 항상 pass → off_pass_rate trends to 1.0 → 정상 라우팅 스킬도 uplift 음수 → false quarantine
- 수정: off-mode 에서 should_trigger=True 쿼리는 **predicted == "none" 만 정답** 으로 판정. LLM 이 fallback 잘 못 하면 off_pass_rate 낮음 → uplift 양수 (스킬 추가 의미 있음). on-mode false positive 증가 (ETH 취리히 -3pp 함정) → uplift 음수 (진짜 quarantine 후보).
- 의미: uplift = on_routing_accuracy - off_routing_accuracy 가 실제 의미를 가짐. v0.8.1 trigger-eval gate 가 진짜 결정론 게이트가 됨.

**[high] craft-lint DESIGN.md 누락 자동 fail** (`scripts/validate-craft-lint.py` + `craft/commands/craft-lint.md`)
- 기존: `check_cross_ref()` 가 DESIGN.md 없으면 warning 만, exit 0 (`/craft-lint` 가 `--strict` 없이 호출) → 디자인 게이트 무력화
- 수정: DESIGN.md 누락을 error 로 격상 (warning 아님) + `/craft-lint` Step 1 에 `--strict` 명시 (defense in depth)
- 의미: Google DESIGN.md base 없이는 ship 게이트 통과 못 함. craft release 의 "mechanical enforcement" 약속 진짜로 작동.

**[high] .track/ 및 craft runtime profiles 격리** (`.gitignore`)
- 기존: `.gitignore` 에 `.track/` 부재 (progress-probe install 시점에만 append). 공유 repo 에서 operator 간 runtime state (actual_log / predicted / blockers) 충돌 가능.
- 수정: repo-level `.gitignore` 에 `.track/` + `**/.track/` 미리 등록. craft runtime 파일 (hierarchy-report.json / motion-drift.md / ui-drift-report.md) 도 .design/ 안 개별 등록.
- 추후 별도 cycle: SKILL.md 의 path 를 `profiles/<operator>/track/<feature>/` 구조로 격리 (구조 변경, surgical 아님)

### Fixed — Medium

**[medium] v0.8.1 metadata 불일치 정합** (9 plugin.json + marketplace.json + README + README-ko)
- 기존: v0.8.1 tag 였으나 manifests 모두 0.8.0 (Codex 권고 4번)
- 수정: 9 plugin.json + marketplace.json + README badges + intro 모두 0.8.2 일괄. v0.8.1 tag 그대로 유지 (force-update 안 함, 외부 사용자 영향 회피). v0.8.2 에서 통합 정합.

### Verified
- `validate_plugins.py`: 9 plugins / 62 skills / 26 commands / Errors 0 / Warnings 0
- v0.7.5 회귀 0 (operate 4 스킬 그대로)
- 4 fix 모두 결정론 (Rule 5 위반 0)

### Architecture — Codex 검수의 가치
v0.8.0 release 후 v0.8.1 patch 진행 상태에서 외부 모델 (Codex/GPT-5) 의 적대적 검수가 4 findings 도출. 3 high finding 모두 mechanical enforcement (Rule 5) 의 정확한 적용을 막던 logic 결함이었고, 이번 patch 로 진짜 결정론 게이트가 됨. 메모리 [[feedback_slide_review]] "2명 합의" 패턴의 정확한 적용 — 같은 Claude 가 self-review 했으면 발견 못 했을 logic 버그를 cross-model review 가 잡음.

---

## [0.8.1] — 2026-05-17

### Added — evals 인프라 완성

`evals/trigger-evals.json`: 31 → 42 entries, 124 → 168 queries (+44).
- 11 신규 스킬 (velocity-baseline / estimate-tasks / progress-probe / blocker-detect / progress-report / gate-checkpoint / respect-checkpoint / respect-brief / hierarchy-rules / motion-language / ui-drift-detect) 각 4 시드 (should_trigger 2 + should_not 2).
- should_not 시드는 헷갈리는 라우팅 경계 케이스 (예: velocity-baseline false 시드 → estimate-tasks 가야 하는 쿼리).

`evals/skill-uplift.py` PLUGINS 에 track + craft 추가 (catalog scan 갱신).

> ⚠️ v0.8.1 의 manifests 는 0.8.0 그대로 (release skew). v0.8.2 에서 통합 정합.

### Pending — API 한도 풀린 후 (2026-06-01)
```bash
ANTHROPIC_API_KEY=<key> python3 evals/skill-uplift.py --all --runs-per-query 3 --threshold 0.05
```

---

## [0.8.0] — 2026-05-17

> **Build-to-Ship 사이의 빈 공간을 닫는 두 신규 플러그인.** "이 존중은 사람이 넣는 겁니다" (영상 5번 통찰) 를 mechanical enforcement 로. 11 신규 스킬 모두 Rule 5 위반 0 (LLM 분류만 허용, routing/policy/metric 결정은 결정론).

### Added — 신규 2 플러그인 (track + craft) + 11 스킬 + 5 commands

**`track`** — prompt-level 진행률 추적 (7 스킬 + 3 commands)
- `velocity-baseline`: git log + token usage → complexity 1-5 × percentile lookup table 결정론 추출 (LLM 호출 0)
- `estimate-tasks`: WBS 분해 (LLM 분류) + lookup 기반 loc/tokens/minutes p50/p90 예측 (LLM 호출 0 in Step 4)
- `progress-probe`: PostToolUse Hook (primary) + shell fallback (defensive, claude-code issue #17688 대응) 이중 메커니즘
- `blocker-detect`: 5종 결정론 신호 (self_doubt 정규식 50 패턴, retry_loop_file, test_fail_repeat, context_pressure, stall) + 부가 (cycle_dependency, token/time overrun), severity 가중치 합산
- `progress-report`: 7 event-driven 트리거 강제 보고 (operate/weekly-rollup cadence와 차별화)
- `gate-checkpoint`: 6 phase 전환 게이트 (requirements → design → tasks → implementation → verification → ship), PreToolUse Hook 차단
- `respect-checkpoint`: AI 분류 (screen_type/traffic_level) + 결정론 매트릭스 lookup → α (인간 7초) + β (72h 데이터) + γ (Playwright + saliency map) 게이트 조합
- commands: `/track-init` / `/track-status` / `/track-retro`

**`craft`** — DESIGN.md + RESPECT.md 이중 파일 디자인 시스템 (4 스킬 + 2 commands)
- `respect-brief`: RESPECT.md 5 섹션 (three_second_rule / next_action / social_proof / hierarchy_rules / motion_language) 인터뷰 강제 생성, 영상 5번 통찰 시스템화
- `hierarchy-rules`: Playwright + DOM saliency + pixel KMeans + WCAG AA 런타임 측정 (5 룰 + contrast)
- `motion-language`: CSS transition / framer-motion AST 결정론 스캔, RESPECT 명세 대비 drift 보고
- `ui-drift-detect`: 5+ 화면 pHash + KMeans palette + DOM tree edit distance (5 차원 drift score)
- commands: `/craft-init` / `/craft-lint`

### Added — 기존 스킬 3 확장 (Phase 2 통합 패턴)

- `learn/skills/pm-engine`: `/pm-tacit-from-retro` 트리거 + Route에 track/retro-extract 자동 promote 경로 (deviation_pct ≥ 50% OR recurrence ≥ 3)
- `deliver/skills/prd`: Route + Quality Gate + Instructions Phase 3 보강 (craft/respect-brief 라우팅), 14-section 구조 그대로 surgical 추가
- `scripts/validate-craft-lint.py` 신규 (180 LOC, RESPECT.md + DESIGN.md cross-ref 결정론 검증)

### Added — evals 인프라

- `evals/skill-uplift.py` (208 LOC): ETH 취리히 -3pp 함정 자동 감지 runner. 각 스킬을 (on/off) 두 모드로 trigger eval → uplift threshold (+5pp 기본) 미달 시 quarantine 후보 분류. LLM 호출은 1줄 라우팅 결정만, uplift 계산·judge·quarantine 모두 결정론.

### Changed — monorepo 버전 정렬

- 모든 plugin.json + marketplace.json 0.7.5 → 0.8.0 일괄
- marketplace.json description: 50/18/7 → 62/26/9 + v0.8 신규 플러그인 설명
- README badges + intro callout 양방 갱신 (README.md + README-ko.md)
- validate_plugins.py PLUGINS 상수에 "track", "craft" 추가

### Verified

- `validate_plugins.py`: 9 plugins / 62 skills / 26 commands / Errors 0 / Warnings 0
- 4 worktree (track + craft + integration + evals) 병렬 작업 → 단일 main 머지 (conflict: validate_plugins.py + marketplace.json 2건, 둘 다 결정론 해결)
- Ralph Loop 자율 모드 6 Phase 완주 ([[feedback_ralph_loop_autonomous]] 준수 — 질문 금지, pending_inputs 묶음, 백업+dry-run+검증)

### Architecture — "AI 는 기능을 만들어 주지만, 이 존중은 사람이 넣는 겁니다"

v0.7 까지의 hplan 은 "what to build" + "how to operate portfolio" 에 강점. v0.8 은 "build 와 ship 사이" 의 빈 공간을 두 플러그인으로 메움:

- `track` 은 단일 프로젝트의 prompt-level 실시간 가시성 (operate 의 weekly cadence 와 차별화)
- `craft` 는 AI 코딩의 "professionally generic" 수렴 함정을 token 위의 의도 레이어 (RESPECT.md) 로 차단

두 플러그인 모두 mechanical enforcement of "human intent" — Rule 5 의 정확한 적용. LLM 을 if 문으로 쓰지 않고, 인간의 의도를 yaml 정책으로 인코딩한 뒤 결정론으로 강제.

---

## [0.7.5] — 2026-05-16

### Fixed — Validator warnings 12 → 0

7개 스킬(`exclusions`, `evidence-rubric`, `cogs-sentinel`, `decision-log`, `interview-synthesis`, `ost`, `handoff`) body에 `Running for: **$ARGUMENTS**` 라인 추가 — `argument-hint` frontmatter는 있었지만 body가 `$ARGUMENTS`를 참조하지 않아 validator가 경고를 띄우던 상태였습니다.

3개 커맨드 description에 "Use when" 트리거 패턴 적용:
- `hplan-scope-guard.md`: "Use before implementing" → "Use when implementing"
- `hplan-verify.md`: "Use before marking" → "Use when marking"
- `write-prd.md`: 14-section 설명에 "Use when ... before build" 절 삽입

`hplan.md` 커맨드에 `## Output Format` 섹션 명시 (verdict block 형식이 인라인 Step 4에만 있어 검사기가 못 찾던 문제).

### Added — `cogs_sentinel.py --mode realtime`

PMF Gate 정식 승격 조건 1번 충족. 베타 출시 후 실측 호출 데이터(`--actual-calls-per-user-month`, `--actual-tokens-in`, `--actual-tokens-out`)를 주입하면 Build Gate 예측값(`harness/build-gate/cogs_input.json`)과 자동 비교해 `delta_pp`를 계산합니다.

```bash
python3 hplan/scripts/cogs_sentinel.py --mode realtime \
  --actual-calls-per-user-month 65 \
  --provider anthropic --model claude-sonnet-4-6 --arpu 29
```

출력에 `## Realtime Comparison` 블록 추가:
- predicted vs actual p90 margin
- delta_pp (±)
- ±15pp 임계치 초과 시 ⚠️ EXCEEDED 표시 + reasons[0]에 PMF threshold 경고 삽입

기본 `--mode predict`는 이전과 100% 동일하게 동작합니다 (backward-compatible).

### Changed — `pmf-gate` 스케치 → 정식 스킬

`hplan/skills/pmf-gate/SKILL.md`를 7-section 표준 구조로 승격:
- frontmatter 표준화 (`argument-hint`, `allowed-tools`, `model`)
- `Running for: **$ARGUMENTS**` 포함
- Core Goal / Trigger Gate (Use·Route·Boundary) / Inputs / Steps / Outputs / Verification 섹션 분리
- "스케치" 표시 제거

여전히 외부 의존 항목 (Habix Legal W6 실측 검증)은 운영 단계에서 충족 예정.

### Sync — Plugin version metadata

`marketplace.json` + 7개 `plugin.json`이 v0.7.0~0.7.4 동안 동기화되지 않아 모두 `"version": "0.7.0"`이었던 누적 drift를 v0.7.5로 일괄 정렬.

---

## [0.7.4] — 2026-05-16

### Added — Gate Integrity Harness

**배경**: hplan은 "만들어야 하는가"를 판단하는 게이트지만, 게이트를 건너뛰거나 세션이 바뀌면 결정 컨텍스트가 사라지는 세 가지 구조적 취약점이 있었습니다. 최소 구현으로 해결합니다.

#### 취약점 1 해소 — HARD-GATE (게이트 건너뛰기 차단)

`hplan/commands/hplan-product.md` 상단에 `<HARD-GATE name="evidence">` 추가:
- Evidence Gate 미통과 시 Product Gate 진입 차단
- **예외**: 경쟁사 분석·고객 프로파일링·AI persona 초안·시장 리서치는 게이트 전 실행 가능 (Evidence Gate 인풋이지 통과 대체물이 아님)

`hplan/commands/hplan-build.md` 상단에 `<HARD-GATE name="product">` 추가:
- Product Gate 미통과 시 Build Gate 진입 차단
- Journey map + Sitemap 없이 PASS 선언 금지

`hplan/PLUGIN.md` Rule 9 추가: "AI persona 초안 ≠ Evidence Gate pass."

#### 취약점 2 해소 — STATE.md + SessionStart hook (세션 컨텍스트 유지)

`/hplan-build` CONDITIONAL_GO 출력 시 `harness/STATE.md` 자동 생성:
- 현재 게이트·verdict·decision_id
- Active 조건 테이블 (`verified_by` 파일 경로 + ❌/✅ 상태)
- 블로커 목록·다음 진입 조건

`harness/PROGRESS.md` 자동 생성 (STATE.md와 쌍):
- `STATE.md` = 게이트 상태 (기계가 읽음)
- `PROGRESS.md` = 마일스톤별 "시작 전 체크" 블록 (사람이 읽음)

`hplan/references/settings-example.json` (새 파일):
```jsonc
"SessionStart": [{"hooks": [{"command": "[ -f harness/STATE.md ] && cat harness/STATE.md || true"}]}]
```
프로젝트 `.claude/settings.json`에 복사하면 세션 시작 시 STATE.md 자동 주입.

참조 템플릿: `hplan/references/state-template.md`, `hplan/references/progress-template.md`

#### 취약점 3 해소 — 조건 anchor 테이블 (조건 → 검증 추적)

CONDITIONAL_GO 출력에 `| 조건 | verified_by | 상태 |` 테이블 포함:
- `verified_by` 파일이 없음 = 조건 미검증 = 게이트 통과 불완전
- `validate_docs.py --check condition_coverage`가 자동 교차 검사

---

### Added — 개발 진행 스킬 (Phase 2)

#### `/hplan-verify` — 완료 선언 전 증거 게이트

`hplan/commands/hplan-verify.md` (새 파일):
- `STATE.md`의 `verified_by` 파일 존재 여부 확인 → ❌→✅ 갱신
- 파일 존재만 체크 (테스트 실행은 CI 책임 — 결정론/비결정론 경계 유지)
- 전체 / 특정 조건 이름 매칭 선택 실행
- 판정: `COMPLETE` / `PARTIAL` / `BLOCKED`
- condition-sync 스킬 흡수 (별도 스킬 불필요)

#### `/hplan-scope-guard` — 범위 이탈 + COGS 티어 차단

`hplan/commands/hplan-scope-guard.md` (새 파일):
- Step 1: 영구 제외 레지스트리 충돌 확인 → BLOCK
- Step 2: checkpoint.json `allowed_paths` 범위 확인 → DEFER
- Step 3: 새 피처의 외부 API/모델 추가 탐지 → COGS 티어 경고
- 판정: `ALLOW` / `DEFER` / `BLOCK`
- DEFER 시 `harness/v2-backlog.md` 자동 기록
- 설계 시점 차단 (scope-guard) + 커밋 시점 차단 (gate_guard) 이중 레이어

---

### Added — Build Gate 출력 개선 (Phase 3)

`hplan/commands/hplan-build.md` Phase 3에 PROGRESS.md 생성 지시 추가:
- CONDITIONAL_GO 시 `harness/PROGRESS.md` 자동 생성
- 각 Wx 마일스톤에 "시작 전 체크" 블록 (조건·기술결정·COGS 추정·블로커) 포함
- `/hplan-build` 재실행으로 전체 사이클 종료 선언
- `hplan-discuss` 스킬 제거 (Build Gate 출력물에 흡수)

---

### Added — PMF Gate 스케치 (Phase 4)

`hplan/skills/pmf-gate/SKILL.md` (새 파일, 스케치 상태):

hplan 사이클을 닫는 운영 후 루프:
```
Evidence → Product → Build → [출시] → PMF Gate → Evidence (다음)
```

트리거 기준 4종:
- 시간: 베타 출시 후 30일 (기본값, PROGRESS.md에서 오버라이드)
- 사용자: 유료 전환 10명 또는 베타 30일 재방문
- COGS: 실측 p90 margin이 sentinel 예측과 ±15%p 이상 차이
- STATE.md "다음 진입 조건" 충족

출력: `harness/pmf-output.yaml` — `cogs_sentinel.py` 실측값 + 행동 지표 + `evidence_carry_over` (다음 Evidence Gate 인풋)

스케치 → 정식 승격 조건: `cogs_sentinel.py --mode realtime` 파라미터 추가 + Habix Legal W6 실측 검증 후.

---

### Fixed — Pre-commit soft warning for unfilled STATE.md anchors

`scripts/install-hooks.sh` 확장:
- commit 시 `harness/STATE.md`를 스캔해 `verified_by = 추후 기입` + ❌ 항목 카운트
- N > 0이면 `/hplan-verify` 권장 경고 출력
- **커밋은 허용** (exit 0 유지) — 완료 의식 없이 hard block하면 우회 인센티브만 생김
- `harness/STATE.md` 없으면 조용히 스킵 (후방 호환)

---

## [0.7.3] — 2026-05-16

### Added — Operational Gap Fixes (3 Phases)

Five gaps discovered while using hplan in a real project (habix / legal-graph-RAG). All gaps share the same root: hplan issued a point-in-time gate but provided no enforcement layer to keep code honest *after* the gate passed.

#### Phase 1 — CONDITIONAL_GO scope enforcement

**Problem**: Both `GO` and `CONDITIONAL_GO` wrote `status: "approved"` to checkpoint.json. The guard checked only `status`, so CONDITIONAL_GO became indistinguishable from full approval after the gate opened — outstanding conditions and prototype limits were silently dropped.

**`checkpoint.json` schema extended**:
```jsonc
{
  "status": "approved",
  "decision": "CONDITIONAL_GO",   // new — "GO" | "CONDITIONAL_GO"
  "conditions": ["..."],           // new — human-readable gate conditions
  "allowed_paths": ["specs/001-", "docs/DESIGN.md"],  // new — write-scope constraint
  "required_tests": ["tests/unit/test_gate_f.py"],    // new — must exist at commit time
  "expires_at": "2026-06-01"       // new — conditional window hard deadline
}
```

**`hplan/hooks/gate_guard.py`**:
- `gate_approved()` now returns `(bool, reason, dict)` — passes checkpoint data downstream to avoid a second filesystem read.
- New `check_conditional_scope(data, target)`: if `decision == "CONDITIONAL_GO"`, blocks writes outside `allowed_paths` and blocks if `expires_at` is past.
- BYPASS moved to top of `main()` for early return before any filesystem work.

**`scripts/install-hooks.sh`** — git pre-commit updated:
- `git show :harness/build-gate/checkpoint.json` now reads the **staged index blob**, not the working tree. Prevents bypass via leaving an approved checkpoint unstaged.
- Python inline block extended to output `STATUS FRESHNESS_VERDICT SCOPE_VERDICT` (3 fields).
- New `SCOPE_VERDICT` blocks: `expired:<date>` (CONDITIONAL_GO past deadline) and `missing_tests:<file1>|<file2>` (required test files absent).

#### Phase 2 — Handoff canonical paths

**Problem**: `export_handoff.py` wrote generated specs/agent files under `harness/exports/<target>/` and told operators to copy them manually. Claude Code, Kiro, and Spec-Kit read from their own canonical locations — the handoff files were never consumed.

**`hplan/scripts/export_handoff.py`**:
- `export()` now writes directly to canonical paths:
  - spec-kit → `root/specs/NNN-slug/{spec,plan,tasks}.md`
  - kiro → `root/.kiro/specs/slug/{requirements,design,tasks}.md`
  - claude → `root/AGENTS.md` + `root/CLAUDE.md` (AGENTS.md is the OpenAI Codex standard)
  - gstack → unchanged (harness/exports/ is authoritative — GStack has no canonical root path)
- `_mirror()` helper silently writes a backup copy to `harness/exports/` for audit trail.
- Post-export verification returns a `phantom` list; `main()` exits 1 if any written file is missing on disk.

#### Phase 3 — Deterministic cross-reference validator

**Problem**: docs drift accumulates silently after gate generation. During one real project session, 7 inconsistencies were found manually: conflicting prices, phantom AGENTS.md references, wrong code paths in Implementation anchor fields, and CONDITIONAL_GO conditions with no matching test coverage.

**`hplan/scripts/validate_docs.py`** (new):

Three deterministic checks — no LLM, no external deps, pure stdlib:

| Check | What it finds |
|-------|--------------|
| `path_existence` | `**Implementation anchor**` / `**Verified by**` declared paths that don't exist on disk |
| `price_consistency` | Same plan keyword (Pro/Starter/Free/Enterprise) maps to two different price tokens across docs |
| `condition_coverage` | CONDITIONAL_GO `conditions[]` entries that have no `@pytest.mark.hplan_condition("...")` in tests/ |

```bash
python3 hplan/scripts/validate_docs.py              # human report, exit 0/1
python3 hplan/scripts/validate_docs.py --json       # JSON for CI
python3 hplan/scripts/validate_docs.py --check path_existence
```

Scans: `docs/`, `specs/`, `harness/` for doc files; `tests/` for pytest marks.
Exit codes: 0 = all pass, 1 = one or more failures, 2 = usage error.

Wire into project scaffolds via `scripts/run_checks.sh` or pre-commit hook for docs changes.

---

## [0.7.2] — 2026-05-16

### Added — Context Engineering Layer (3 new artifacts)

**Problem**: hplan ran evidence-rubric scoring even when the context fed to it was garbage — no way to know if a 45/100 score reflected a weak idea or weak research.

**Solution**: a full Context Engineering layer that gates on *input quality* before running rubrics.

#### `hplan/scripts/context_quality_scorer.py` — Context Quality Score (CQS)

RAGAS-inspired 100-point scorer measuring PM research richness *before* the evidence rubric runs. 6 dimensions (100 pts total):

| Dimension | Max | Signal |
|-----------|-----|--------|
| Interview volume | 25 | Torres convergence threshold: 5+ = pattern likely |
| Segment diversity | 20 | Behavioral ICP > demographic ICP |
| Evidence recency | 20 | within_30d = fresh signal; older = decayed |
| Source independence | 15 | +5 per type (interviews / public reviews / market data) |
| Competitor coverage | 10 | pricing + segment depth required |
| Workaround specificity | 10 | tool + quantified pain = strong demand |

Gate verdicts: CQS ≥ 75 = HIGH ✅ / 55-74 = MODERATE ⚠️ / 30-54 = LOW ⚠️ / < 30 = INSUFFICIENT 🚫 (blocks gate).

No external dependencies (pure stdlib). `--json` flag for CI integration.

```bash
python3 hplan/scripts/context_quality_scorer.py harness/context-intake.md
python3 hplan/scripts/context_quality_scorer.py --json harness/context-intake.md
```

#### `hplan/references/competitor-context.md` — Competitive Gate Template

5-Block structure extracting GO/HOLD signals from competitive analysis:

- **Block A**: Market existence — direct + indirect competitors
- **Block B**: Segment gap — what incumbent neglects + your wedge
- **Block C**: Business model conflict — copy cost for incumbent (counterposition test)
- **Block D**: Hard blockers — 3 boolean fields; any `true` = immediate HOLD
- **Block E**: Entry rationale — `why_now` + `unfair_advantage` (both required)

Copy template to `harness/competitor-context.md` per project.

#### `hplan/commands/hplan.md` — Step 0 Context Intake Check added

`/hplan` orchestrator now runs a pre-flight before Step 1 (exclusions):
1. Reads `harness/context-intake.md` if present → runs CQS scorer → blocks if CQS < 30
2. Reads `harness/competitor-context.md` if present → any `blocker == true` → immediate HOLD

### Added — Freshness Enforcement + Dual-Defense Hook (Phase 1, shipped 2026-05-14)

**`hplan/hooks/gate_guard.py`** extended with `check_freshness()`:
- Reads `context_dates` from `harness/build-gate/checkpoint.json`
- Per-field thresholds: `customer_interviews` warn 60d/block 90d; `competitive_analysis` warn 45d/block 90d; `provider_pricing` warn 30d/block 60d; `market_size` warn 90d/block 180d
- Backward compatible: absent `context_dates` → silently passes

**`scripts/install-hooks.sh`** — git pre-commit hook installer (second defense layer):
- `gate_guard.py` = soft UX warning when Claude attempts the write
- `git pre-commit` = deterministic hard block before the commit lands
- `CLAUDE_HPLAN_BYPASS=1` env var for authorized bypass

**`hplan/references/context-intake.md`** — 9-section structured intake template with ✅/❌ inline examples for every field. Eliminates LLM inference dependency on GIGO inputs.

### Fixed — Pre-commit hook reads staged index, not working tree (security)

**Reported by**: Codex adversarial review.

**Bug**: `scripts/install-hooks.sh` read `harness/build-gate/checkpoint.json` from the working tree via `open(path)`. Git commits the index, not the working tree — a user could leave an approved checkpoint unstaged while staging guarded PRD/spec files; the hook would pass, but the resulting commit contained no approved checkpoint.

**Fix**: Replace `open(checkpoint)` with `git show :harness/build-gate/checkpoint.json` to read the index blob. Also run `context_dates` freshness threshold check against the staged blob (was: only gate_guard.py soft warning; now hard-blocks stale evidence at commit time).

Bypass: `CLAUDE_HPLAN_BYPASS=1` still available for authorized use.

---

### Added — Dovetail artifact rule + Netflix density penalty in CQS interview scoring

Two design weaknesses identified via adversarial review + market research (Guest et al. 2006, Dovetail, Netflix DORA):

**약점 2 — self-report unverifiable (Dovetail artifact rule)**
- New field: `interview_artifact` — link to Zoom recording / transcript / Dovetail board / note file. One artifact required.
- `score_interview_volume()` caps at 12/25 when `interview_count > 0` but no artifact is present.
- Prevents zero-evidence interview count claims from scoring as HIGH.

**약점 3 — gamification incentive (Netflix density penalty)**
- New field: `unique_insights` — number of distinct insights discovered across interviews.
- Density = `unique_insights / interview_count`; if < 0.5 → −3 pts applied.
- Discourages bulk low-quality interviews that inflate count without discovery.

**Evidence**: gaming scenario (10 interviews, no artifact, 1 insight) → 9/25. Honest scenario (10 interviews, artifact linked, 7 insights) → 25/25. The 16-point gap crosses the MODERATE ↔ HIGH boundary.

**약점 1 note — threshold calibration**: CQS thresholds (30/55/75) remain as **v0.7.2 hypotheses** — empirically derived only from Guest, Bunce & Johnson (2006) saturation research and Stage-Gate risk calibration patterns. Real calibration requires outcome tracking: collect 20+ hplan-gated project results (6-month retention, COGS accuracy) and back-calculate from pass/fail distributions. Planned for a future release once usage data accumulates.

---

## [0.7.1] — 2026-05-14

### Changed — `deliver/skills/prd` expanded to **Unified PRD 14-section**

Previously the `prd` skill was Agent-PRD-only (7-section: Overview / Instruction / Tools / Memory / Trigger / Output / Failure). This expansion unifies it with the customer-facing product PRD format so PMs maintain a **single source of truth** for both the product and the LLM agents inside it.

**Why unify:**
- In 2026, virtually every SaaS contains an LLM agent. The product PRD vs agent PRD split was artificial.
- One PRD = one cognitive entry point for PMs and solo builders.
- Solo-builder 60-day cycle teams maintain a single PRD they re-version (v0.1 → v0.3) instead of juggling two documents.

**New 14-section structure:**

Top (1-6) — People / Problem / Decisions
1. ICP & personas (via `discover/agent-gtm` beachhead 5-criteria)
2. JTBD with Switch 4 Forces
3. Core problem + 10x value (quantified)
4. Decision options matrix (`discover/build-or-buy` + `architect/orchestration` + `discover/hitl`)
5. Out-of-scope (min 5, via `hplan/exclusions`)
6. Now/Next/Later + cogs p50/p90 (via `discover/cost-sim`)

Middle (7-11) — Agent / Execution Spec
7. Role + Primary Goal + Anti-Goals (≥ 3) — `deliver/instruction` for detail
8. Tools & Integrations + call limits mandatory
9. Memory & Context (3-tier: Working / Long-term / Procedural)
10. Trigger & Execution Flow (Cron/Event/Manual/Pipeline)
11. Output Specification + sample

Bottom (12-14) — Metrics / Hypotheses / Failure
12. Dual-axis OKR (North Star + Business + Operational + Anti-Metric; cost KR mandatory) — `measure/north-star` + `deliver/okr`
13. Top-3 hypotheses (Value/Feasibility/Reliability/Ethics) + 2-day experiment — `discover/assumptions`
14. Failure modes (≥ 4) + Human-in-the-loop triggers

**Migration from v0.6 → v0.7 PRD:**

| v0.6 (Agent PRD 7-section) | v0.7 (Unified 14-section) |
|---|---|
| Section 1 Overview | Section 1 (페르소나) + Section 3 (문제) |
| Section 2 Instruction Design | Section 7 (Role + Anti-Goals) |
| Section 3 Tools & Integrations | Section 8 (same) |
| Section 4 Memory Strategy | Section 9 (same) |
| Section 5 Trigger & Execution | Section 10 (same) |
| Section 6 Output Specification | Section 11 (same) |
| Section 7 Failure + Success Metrics | Section 12 (success) + Section 14 (failure) split |

New sections to fill in for migration: 1·3·4·5·6·13 (people / decisions / hypotheses).

**Pure-agent use case (internal LLM agents)**:
Section 1·3 personas = internal users. Section 2 JTBD = internal workflow. Section 7-11 stays detailed.

**Pure-SaaS use case (no LLM agent)**:
Section 7-11 may be marked "N/A — no AI feature" with a single line, leaving placeholders for future AI additions.

**Quality Gate**: `scripts/validate-prd.sh` updated to check all 14 sections (was 7). 17 quality gate items total (14 sections + consistency + TK citations + Y/N coverage).

### Updated

- `deliver/skills/prd/SKILL.md` (449 lines) — 14-section template + Trigger Gate + Quality Gate + Phase 1-5 instructions
- `deliver/commands/write-prd.md` (123 lines) — 5-phase chain with 2 user checkpoints
- `deliver/skills/prd/examples/good-01.md` — 1인 변호사 한국 판례 RAG SaaS (full 14-section example)
- `deliver/skills/prd/examples/bad-01.md` — anti-pattern with 14-section diagnostic table
- `deliver/skills/prd/references/test-cases.md` — 17 Quality Gate items + interview validation
- `deliver/skills/prd/references/troubleshooting.md` — 10 FAQs (general SaaS vs agent-heavy SaaS, etc.)
- `deliver/skills/prd/context/domain.md` — 60-day cycle + domain notes + v0.6 → v0.7 migration table
- `scripts/validate-prd.sh` — 14-section keyword check
- `README.md` / `README-ko.md` — `prd` skill description updated to "Unified PRD 14-section"

### Not breaking — backward compatible

- Existing v0.6 Agent PRDs remain valid; missing sections (1·3·4·5·6·13) show as "TBD" in validate-prd.sh warnings but don't block.
- `/write-prd` command preserved (no rename); chain extended.

---

## [0.7.0] — 2026-05-14

운영 노하우 4영역(실행 통합 / PRD 검증 깊이 / 에이전트 생태계 / PPTX 생산성)을 hplan에 흡수.

### Added — new plugin

- **operate** — 에이전트 포트폴리오 운영. 단일 에이전트 KPI(measure)를 넘어서 5+ 에이전트 운영을 다룬다.
  - `agent-portfolio` — T1~T5 티어링 + 인시던트 가중치
  - `scorecard-5axis` — Accuracy/Reliability/Cost/Velocity/Satisfaction 5축 가중 점수
  - `weekly-rollup` — 주차별 평균·Δ·Top 이동자·이상치 자동 요약
  - `cross-team-routing` — capability + 부하 + 티어 + handoff cost 기반 단일 라우팅 결정

### Added — deliver 확장 (실행 통합도)

- `deliver/harness-design` — 4명+ 빌드 팀 + Ralph Loop + 백업 + dry-run + pending_inputs 배치
- `deliver/parallel-team` — 독립 태스크 ≥2 시 worktree 격리 병렬 디스패치
- `deliver/build-loop` — 발견→리서치→설계→PRD→분해→구현 한 루프 (`/build`)

### Added — PRD mermaid 정합성 게이트 (결정론 검증)

- `scripts/validate-mermaid.py` — workflow ↔ userflow ↔ requirements 차분 검증 Python 스크립트
- `scripts/validate-prd.sh`가 mermaid 검증을 자동 호출
- `deliver/skills/prd/SKILL.md`에 게이트 섹션 + 두 다이어그램 의무화
- `deliver/skills/prd/examples/good-02-mermaid-consistency.md`, `bad-02-mermaid-orphan.md` 예시
- `cogs-sentinel`과 같은 결정론 게이트 가족

### Changed — pptx 4엔진 라우터

- `deliver/skills/pptx-ai-slide`가 단일 흐름에서 **4엔진 라우터**로 재정의
  - mckinsey (30+장, 강의 시리즈)
  - hifidelity (≤10장, 이미지 자동 생성)
  - html-qa (5~25장, 디폴트, 자동 QA)
  - video (영상 입력 전처리, 후속 엔진 체이닝 필수)
- `references/engine-comparison.md`, `examples/good-02-engine-routing.md`, `bad-02-engine-misroute.md` 추가
- description을 라우터 문법으로 갱신

### Added — profiles/ 패턴

- `profiles/_template/` — 새 운영자가 복사해서 시작할 yaml 4종
  - `agent-fleet.yaml`, `scorecard-weights.yaml`, `pptx-engines.yaml`, `ralph-loop.yaml`
- `.gitignore`에 `profiles/*` + `!profiles/_template/` + `!profiles/README.md` 추가
- 공개 스킬 ↔ 개인 운영 데이터 레이어 분리

### Added — pm-engine starter TK 4종

- `learn/skills/pm-engine/examples/PM-ENGINE-MEMORY-STARTER.md`에 TK-006~TK-009 추가
- TK-006: 독립 태스크 ≥2 → worktree + 4명+ 팀
- TK-007: PRD는 workflow + userflow 두 다이어그램 정합성 검증
- TK-008: 5+ 에이전트 → 5축 가중 ScoreCard
- TK-009: PPTX는 4엔진 라우팅 결정으로 시작

### Added — 메타 데모 시드

- `tools/intro-video/scenes/v0.7-meta-demo-script.md` — "hplan으로 hplan을 짠다" 70초 자기참조 영상 스크립트

### Infra

- `validate_plugins.py`의 PLUGINS에 `operate` 추가
- 총 7 플러그인 / 50 스킬 / 18 커맨드
- `evals/trigger-evals.json`에 신규 7개 스킬(harness-design, parallel-team, build-loop, agent-portfolio, scorecard-5axis, weekly-rollup, cross-team-routing) 시드 추가 — 스킬당 should_trigger 2건 + should_not 2건. 총 31 스킬 / 124 쿼리. **실제 회귀 평가는 v0.7.x patch에서 진행 예정** (96→124 쿼리 확장 측정 포함).

---

## [0.6.0] — 2026-05-11

### Breaking — 5 plugins renamed to PM standard vocabulary

The original Greek-mythology names (oracle / atlas / forge / argus / muse) were chosen for memorability in v0.3 but caused two problems:
- New users had to learn what each mythology name meant
- They didn't match the vocabulary PMs actually use (Double Diamond, Lean Startup, Teresa Torres CDH)

v0.6 renames each plugin to a PM lifecycle word everyone recognizes:

| Old | New | Why |
|---|---|---|
| `oracle` | `discover` | Continuous discovery / Double Diamond's first D |
| `atlas` | `architect` | System architecture, not UI design (avoids "design = UI" confusion) |
| `forge` | `deliver` | Double Diamond's Deliver phase |
| `argus` | `measure` | Lean Startup's Build–Measure–Learn |
| `muse` | `learn` | Lean Startup's Build–Measure–Learn |

`hplan` (Gate) is unchanged — it's an English brand acronym for **H**arness **Plan**ning and intentionally distinct from the lifecycle stage names.

New lifecycle: `hplan → discover → architect → deliver → measure → learn`

### Changed

- Plugin directories renamed (5 × `git mv`)
- All 6 `plugin.json` `name` fields updated; version bumped to 0.6.0
- `.claude-plugin/marketplace.json` plugin entries renamed + descriptions refreshed
- README.md / README-ko.md / GUIDE-ko.md / CONTRIBUTING.md — every reference to the old plugin names updated
- Plugin lifecycle SVG (`docs/images/plugin-lifecycle.svg`) — box labels + lifecycle phase labels (Execution → Delivery, Monitoring → Measurement, Knowledge → Learning)
- How-it-works SVG (`docs/images/how-it-works.svg`) — plugin pills relabeled
- All SKILL.md "Route to Other Skills When" cross-references updated
- `validate_plugins.py` PLUGINS list updated

### Migration for existing users

Old install commands like `/plugin install oracle@kimsanguine-hplan` now become `/plugin install discover@kimsanguine-hplan`. GitHub auto-redirect handles old paths; users with installed plugins should re-install under the new name.

### Preserved (intentional)

- The Greek tier-name **`Atlas`** inside `architect/skills/3-tier/SKILL.md` — refers to the Prometheus → Atlas → Worker pattern, which is the *content* of the skill, not the plugin name. Mythology tier name remains.
- All historical CHANGELOG entries and `.archive/` work logs.

---

## [0.5.0] — 2026-05-11

### Added — `hplan` plugin (6th plugin, lifecycle Stage 0)

A new plugin that runs BEFORE oracle's discovery — the **Evidence + COGS + Decision gate** that decides whether the product deserves to be built at all.

**New skills (7) under `hplan/skills/`:**

| Skill | What it does |
|---|---|
| `evidence-rubric` | Score idea against 100-point evidence rubric (ICP / recent painful event / workaround / repetition / economic pain / switching trigger / MVP narrowness / acquisition path) |
| `interview-synthesis` | Import AI-clustered interview output (BuildBetter / Perspective / Granola / Otter), force human strength + Push/Pull/Habit/Anxiety axes tagging, audit 5/3 strong-Push rule |
| `exclusions` | Append-only Do-Not-Build registry with Korean-aware char-bigram fuzzy match + reopen_trigger |
| `cogs-sentinel` | Executable COGS gate — p50/p90 monthly margin via lognormal sampling, free-user abuse blend, GREEN/CONDITIONAL_GO/RED decision |
| `ost` | Generate Teresa Torres-style Opportunity Solution Tree with Mermaid + `docs/OPPORTUNITY_TREE.md` |
| `decision-log` | Append-only build/interview/pivot/hold log + 3-6 month self-eval audit (hit_rate, false_holds, missed_builds) |
| `handoff` | Multi-target Build Gate brief → Spec-Kit `specs/NNN-slug/`, Kiro `.kiro/specs/`, GStack `/office-hours`, Claude Code `AGENTS.md` + `CLAUDE.md` |

**New commands (6):**

- `/hplan-evidence`, `/hplan-product`, `/hplan-build`, `/hplan-cogs`, `/hplan-exclude`, `/hplan-handoff`

**Cross-cutting infrastructure:**

- `hplan/hplan_mcp/server.py` — MCP server exposing 6 hplan tools to Cursor / Windsurf / Kiro / Codex / Goose
- `hplan/hooks/gate_guard.py` — Claude Code PreToolUse hook blocking writes to PRD.md / spec.md / `specs/` / `.kiro/specs/` until `harness/build-gate/checkpoint.json` has `status: "approved"`
- `hplan/agents/` — 4 role-locked reviewer agents (evidence / product / economics / build)
- `hplan/references/` — 14 playbooks + `provider_pricing.json` (2026-05-11 snapshot)
- `hplan/scripts/` — 9 deterministic Python scripts

### Changed

- Lifecycle reordered: `hplan → oracle → atlas → forge → argus → muse`
- Marketplace version 0.4.0 → 0.5.0
- "36 skills, 5 plugins" → "43 skills, 6 plugins"
- Added `Route to hplan when ...` lines to 7 existing skills: `discover/cost-sim`, `discover/opp-tree`, `discover/hitl`, `discover/assumptions`, `discover/build-or-buy`, `deliver/prd`, `measure/burn-rate`
- README.md + README-ko.md top sections updated with hplan callout + 6-stage lifecycle table

### Fixed

- Removed accidentally committed `.git_broken/` directory (hundreds of git internals)
- Removed stale `EVAL_QUICK_REFERENCE.txt` (2026-03 internal note)

### Moved

- `todolist.md` → `.archive/2026-03-todolist.md`
- `progress.md` → `.archive/2026-03-progress.md`
- `eval_metrics.json` → `evals/pm-framework-baseline.json`
- `eval-workspace/` → `evals/workspace/`

---

## [1.0.0] — 2026-03-07

### v1.0 Structural Upgrade

Every skill now follows a consistent v1.0 structure that adds production-grade rigor on top of the original educational content.

**New sections in every SKILL.md:**

- **Core Goal** — 1-2 sentence purpose statement
- **Trigger Gate** — Use / Route / Boundary for accurate skill selection
- **Failure Handling** — table of failure → detection → fallback
- **Quality Gate** — self-check checklist before delivery
- **Examples** — good/bad output signals

### New Skills (3)

| Skill | Plugin | What it does |
|-------|--------|-------------|
| `infographic-gif-creator` | forge | Animated infographic GIF/MP4 for agent architecture visualization |
| `pptx-ai-slide` | forge | Agent project presentation deck (pitch, review, investor) |
| `agent-demo-video` | forge | Remotion-based demo video for stakeholders |

### Stats

- **35 skills** (was 32), **12 commands**, **5 plugins**
- Trigger accuracy: 97.9% (94/96)
- Quality eval: with-skill 100% vs without-skill 88% (+12%)
- All 35 skills validated via `validate_plugins.py` — 0 errors, 0 warnings

### Documentation

- README.md / README-ko.md updated (badges, status, forge details, file structure, skill origin)
- CONTRIBUTING.md updated with v1.0 SKILL.md format guide
- GUIDE-ko.md updated (forge 11 skills, total 35)
- "What Makes This Different" — added section 6: v1.0 Structural Rigor
- CHANGELOG.md created (this file)

---

## [0.4.0] — 2026-03-06

### Phase 3 Complete — Eval Framework

- Quality eval: 10 tests, 54 assertions — with-skill 100% vs without-skill 88%
- Trigger eval: 96 queries, 97.9% accuracy
- eval-review.html viewer (237KB self-contained)
- benchmark.json structured results

### Phase 2 Complete — Description Optimization

- All 24 skills → 200+ char descriptions with "Use when..." trigger patterns
- `opp-tree` description expanded (307→646 chars)
- `run_eval.py` baseline: 94/96 passed

### Phase 1 Complete — Structure Migration

- Plugin manifests: PLUGIN.md → `.claude-plugin/plugin.json` (×5)
- Command frontmatter: removed unofficial `skills:` field (×12)
- All skills: added `argument-hint` frontmatter (×24)

---

## [0.3.0] — 2026-03-06

### Initial Content Release

- 5 plugins: oracle, atlas, forge, argus, muse
- 24 skills with Korean concepts + English instructions
- 12 commands (multi-skill chaining workflows)
- Greek mythology naming: Oracle / Atlas / Forge / Argus / Muse
- README.md (EN) + README-ko.md (KO)
- CONTRIBUTING.md + GUIDE-ko.md
