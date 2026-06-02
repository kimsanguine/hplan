# metrics-capture.md — Sprint Probe 메트릭 캡처 정직성 문서

> **목적:** `track-probe.sh`가 실제로 기록할 수 있는 메트릭과 기록하지 않는 메트릭을 정확히 서술한다.
> 과장하거나 숨기지 않는 것이 이 문서의 존재 이유다.

---

## 캡처 현황 요약

| 메트릭 | 캡처 가능? | 출처 | 비고 |
|--------|-----------|------|------|
| `ts` | 가능 | 훅 발화 시각 (`datetime.utcnow`) | ISO8601 UTC; 매 Write/Edit/NotebookEdit 이벤트마다 기록 |
| `loc_delta` | 가능 | `tool_input` 필드 직접 계산 | Write=content 줄 수, Edit=new_string−old_string 줄 수, NotebookEdit=new_source 줄 수 |
| `task` | 가능 | `.track/current_task` 파일 | sprint/conductor가 태스크 시작 시 기록; 파일 없으면 `"unassigned"` |
| `exit_code` | 가능 | `tool_response.exit_code` | 없으면 0; 값을 추정하거나 보정하지 않음 |
| `minutes_elapsed` | 간접 유도 | retro 단계에서 산출 | probe가 직접 기록하지 않음 — task별 `ts` 이벤트의 min/max 차로 계산 |
| `tokens` | 불가 | — | Claude Code 훅 페이로드에 token usage 필드가 없음 |

---

## minutes_elapsed는 probe가 기록하지 않는다

probe는 타이머를 갖지 않는다. 단지 이벤트가 발생할 때마다 `ts`를 찍는다.
`minutes_elapsed`는 retro 단계에서 `actual_log.jsonl`을 읽어 같은 `task` 값을 가진 이벤트들의
`ts` 최솟값과 최댓값의 차이를 분(minute) 단위로 환산해 유도한다.

이 방식의 한계: Claude가 아무 Write/Edit도 하지 않은 사고 시간(thinking time)은 기록되지 않는다.
따라서 `minutes_elapsed`는 실제 작업 시간의 하한(lower bound)에 가깝다.

---

## tokens를 기록하지 않는 이유

Claude Code의 PostToolUse 훅이 stdin으로 전달하는 JSON 구조는 다음 세 필드뿐이다.

```
{ "tool_name": "...", "tool_input": {...}, "tool_response": {...} }
```

token usage는 이 페이로드에 포함되지 않는다. 이를 우회하는 방법으로
`transcript_path`(세션 로그 파일)를 파싱해 사후에 tokens를 추출하는 방안이 있으나,
채택하지 않았다. 이유는 두 가지다.

1. **취약성:** transcript 파일의 경로·포맷은 Claude Code 내부 구현이며 공개 계약이 아니다.
   버전 업데이트 한 번으로 조용히 깨질 수 있다.
2. **Rule 2 (Simplicity First) 위반:** 이미 `loc_delta` + `ts`로 충분히 생산성을 추적할 수 있는 상황에서
   불안정한 파싱 로직을 추가하는 것은 불필요한 복잡도다.

따라서 `tokens` 필드는 로그에 기록하지 않으며, retro 출력과 ticket-bridge estimate에서 `N/A`로 표기한다.

---

## trust_grade에 대한 영향

tokens 데이터가 없으므로 probe의 baseline은 **loc 축과 minutes 축만 신뢰할 수 있다.**

- `trust_grade`가 높은 메트릭: `loc_delta` (결정론적 계산), `ts` (시스템 클럭)
- `trust_grade`가 낮은 메트릭: `minutes_elapsed` (thinking time 누락으로 과소 추정)
- `trust_grade` 해당 없음: `tokens` (N/A)

ticket-bridge estimate가 tokens를 `N/A`로 표기하는 것은 이 한계를 숨기지 않기 위함이다.
미래에 Claude Code 훅 페이로드가 token usage를 포함하게 되면 그때 필드를 추가한다.
그 전까지는 null/N/A가 정직한 값이다.
