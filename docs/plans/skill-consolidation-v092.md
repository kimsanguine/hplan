# hplan Skill Consolidation Plan — v0.9.2 목표

**현재**: 65 skills (hplan 8 / discover 7 / architect 8 / deliver 27 / operate 15)
**목표**: 55 skills (-10)
**Codex adversarial review 반영 (2026-05-22)**: pm-trinity 통합 보류, ui-validate 기본값 제거, alias 계약 테이블 추가, track 순차 실행 명시

---

## 원칙

1. **동일 데이터 파이프라인 스킬은 하나로** — 같은 파일을 읽고/쓰고/보고하는 스킬은 `--mode` 인자로 분기
2. **동일 도구 기반 검증 스킬은 하나로** — 실행 메커니즘이 동일하면 통합
3. **항상 함께 쓰이는 스킬은 하나로** — 선행 스킬 없이 후행 스킬이 의미 없는 경우
4. **read-only 와 mutating 오퍼레이션은 같은 스킬로 합치지 않는다** — 신뢰 경계 원칙 (Codex)
5. **통합 후 기존 스킬명은 deprecated alias stub으로 유지** — alias → 신규 스킬 + 정확한 mode/check 매핑 테이블 필수

---

## deliver 통합 (27 → 19, -8)

### 통합 1 — progress-trinity → `track`
⚠️ **공유 파일 스킬 → 순차 실행, 병렬 금지**

| 기존 스킬 | 역할 | deprecated alias 매핑 |
|-----------|------|----------------------|
| `progress-probe` | PostToolUse hook → `.track/actual_log.jsonl` append | `track --mode probe` |
| `blocker-detect` | `.track/actual_log.jsonl` 스캔 → 블로커 패턴 감지 | `track --mode detect` |
| `progress-report` | 이벤트 트리거 시 상태 강제 보고 | `track --mode report` |

**통합 이유**: 세 스킬 모두 `.track/actual_log.jsonl` 단일 파일 공유. 파이프라인 순서 write→detect→report가 암묵적이라 분리 시 사용자가 순서를 추론해야 함.

**기본값**: `--mode probe` (append-only, 파일 mutate 최소)

**공유 파일 정책**: `.track/actual_log.jsonl` 쓰기는 atomic append-only. detect/report는 read-only. 동시 실행 금지.

---

### 통합 2 — UI 검증 클러스터 → `ui-validate`
⚠️ **기본값 없음 — `--check` 명시 필수 (Codex 지적 반영)**

| 기존 스킬 | 역할 | deprecated alias 매핑 |
|-----------|------|----------------------|
| `hierarchy-rules` | Playwright + DOM saliency → 시각 계층 | `ui-validate --check hierarchy` |
| `motion-language` | CSS transition → RESPECT.md 일관성 | `ui-validate --check motion` |
| `ui-drift-detect` | N스크린 pHash 비교 → 시각 drift | `ui-validate --check drift` |
| `mobile-check` | DESIGN.md 브레이크포인트 375/768/1440px | `ui-validate --check mobile` |

**통합 이유**: 모두 Playwright 기반 시각 품질 검증. ship 직전 한꺼번에 실행하는 패턴이 표준.

**기본값**: **없음** — `--check` 인자를 명시하지 않으면 에러 출력 후 사용 가능한 check 목록 안내. auto-routing 시 Trigger Gate에서 `--check <type>` 명시.

**실패 처리**: 각 check는 독립 실패 가능. baseline 없으면 SKIP (FAIL 아님). 타임아웃 30초/check.

**주의**: `respect-checkpoint`(pre-ship gate)·`respect-brief`(RESPECT.md 생성)는 통합 제외.

---

### 통합 3 — 미디어 생성 이원화 → `media-asset`

| 기존 스킬 | 역할 | deprecated alias 매핑 |
|-----------|------|----------------------|
| `agent-demo-video` | Remotion(React) → 에이전트 데모 영상 | `media-asset --type video` |
| `infographic-gif-creator` | HTML/CSS → GIF/MP4 인포그래픽 | `media-asset --type infographic` |

**통합 이유**: 둘 다 "코드(HTML/React/CSS) → 영상 파일" 파이프라인. 기술 스택·출력 형식 동일.

**기본값**: `--type` 필수. gemini-image-flow는 성격이 달라 제외.

---

### 통합 4 — 추정/속도 → `delivery-plan`

| 기존 스킬 | 역할 | deprecated alias 매핑 |
|-----------|------|----------------------|
| `estimate-tasks` | PRD → WBS 분해, 복잡도 1-5 | `delivery-plan --step estimate` |
| `velocity-baseline` | N개 과거 프로젝트 → 개인 속도 추출 | `delivery-plan --step baseline` |

**기본값**: `--step both` (baseline 계산 후 estimate 조정).

---

### 통합 5 — 지시문/프롬프트 → `agent-instructions`

| 기존 스킬 | 역할 | deprecated alias 매핑 |
|-----------|------|----------------------|
| `prompt` | PM 관점 프롬프트 설계 (의도·결과) | `agent-instructions --level draft` |
| `instruction` | System Prompt + tool list + memory_config 완전 명세 | `agent-instructions --level full` |

**기본값**: `--level full`.

---

## operate 통합 (15 → 13, -2)

### ~~통합 6 — pm-trinity → `pm-memory`~~ → **보류 (Codex HIGH 지적)**

`pm-framework`(extract/classify), `pm-engine`(read/write/search), `pm-decision`(apply)는 서로 다른 신뢰 경계. 같은 스킬로 통합 시 의도치 않은 `PM-ENGINE-MEMORY.md` write/apply 트리거 위험. rollback·충돌 처리·승인 게이트 설계 후 v0.9.3에서 재검토.

**현재 상태**: 3개 스킬 개별 유지.

---

### 통합 7 — 메트릭 이원 → `metrics-design`

| 기존 스킬 | 역할 | deprecated alias 매핑 |
|-----------|------|----------------------|
| `north-star` | 에이전트 단일 North Star 메트릭 정의 | `metrics-design --step north-star` |
| `kpi` | AI 에이전트 KPI 정의·추적 | `metrics-design --step kpi` |

**기본값**: `--step both` (North Star → KPI 파생 순서).

---

### 통합 8 — 포트폴리오 리포팅 → `portfolio-report`

| 기존 스킬 | 역할 | deprecated alias 매핑 |
|-----------|------|----------------------|
| `scorecard-5axis` | 5축 가중 루브릭 채점 | `portfolio-report --view scorecard` |
| `weekly-rollup` | 주간 포트폴리오 집계 | `portfolio-report --view rollup` |

**기본값**: `--view rollup`.

---

## 통합 후 스킬 수

| 플러그인 | 현재 | 변경 | 목표 |
|----------|------|------|------|
| hplan | 8 | - | 8 |
| discover | 7 | - | 7 |
| architect | 8 | - | 8 |
| deliver | 27 | -8 | 19 |
| operate | 15 | -2 | 13 |
| **합계** | **65** | **-10** | **55** |

---

## Deprecated Alias 계약 테이블 (전체)

| 구 스킬명 | 신규 스킬 | mode/check/type/step | 출력 동일성 |
|-----------|----------|---------------------|------------|
| `progress-probe` | `track` | `--mode probe` | ✅ |
| `blocker-detect` | `track` | `--mode detect` | ✅ |
| `progress-report` | `track` | `--mode report` | ✅ |
| `hierarchy-rules` | `ui-validate` | `--check hierarchy` | ✅ |
| `motion-language` | `ui-validate` | `--check motion` | ✅ |
| `ui-drift-detect` | `ui-validate` | `--check drift` | ✅ |
| `mobile-check` | `ui-validate` | `--check mobile` | ✅ |
| `agent-demo-video` | `media-asset` | `--type video` | ✅ |
| `infographic-gif-creator` | `media-asset` | `--type infographic` | ✅ |
| `estimate-tasks` | `delivery-plan` | `--step estimate` | ✅ |
| `velocity-baseline` | `delivery-plan` | `--step baseline` | ✅ |
| `prompt` | `agent-instructions` | `--level draft` | ✅ |
| `instruction` | `agent-instructions` | `--level full` | ✅ |
| `north-star` | `metrics-design` | `--step north-star` | ✅ |
| `kpi` | `metrics-design` | `--step kpi` | ✅ |
| `scorecard-5axis` | `portfolio-report` | `--view scorecard` | ✅ |
| `weekly-rollup` | `portfolio-report` | `--view rollup` | ✅ |

---

## 실행 순서 (Codex 병렬화 수정 반영)

```
순차 (공유 파일):
  1. progress-trinity → track           (.track/actual_log.jsonl 공유)

병렬 가능 (독립):
  2a. UI 검증 클러스터 → ui-validate
  2b. 미디어 이원화 → media-asset
  2c. 추정/속도 → delivery-plan
  2d. 지시문/프롬프트 → agent-instructions
  2e. 메트릭 이원 → metrics-design
  2f. 포트폴리오 → portfolio-report

완료 후:
  3. trigger-evals.json 55개 기준 업데이트
  4. validate_plugins.py 통과 확인
  5. deprecated alias eval parity 검증
```

---

## 검증 기준

- [ ] `python3 validate_plugins.py` 0 errors (55 skills)
- [ ] 신규 7개 통합 스킬 단독 eval uplift ≥ +5pp
- [ ] deprecated alias eval: 구 스킬명으로 eval 시 동일 pass/fail 결과
- [ ] 전체 55 스킬 eval on-mode ≥ 93.5% (현행 유지)
- [ ] `ui-validate` 인자 미지정 시 에러 + 목록 안내 출력 확인
- [ ] `track` 동시 실행 시 `.track/actual_log.jsonl` 충돌 없음 확인
