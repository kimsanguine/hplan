#!/usr/bin/env bash
# track-probe.sh — sprint --step init이 사용자 프로젝트 scripts/로 복사하는 probe hook.
#
# Claude Code PostToolUse 훅으로 등록되어 Write/Edit/NotebookEdit 이벤트마다 호출된다.
# 실측 데이터(loc_delta, ts)를 .track/actual_log.jsonl에 append한다.
#
# 훅 프로토콜: 입력은 stdin JSON (tool_name, tool_input, tool_response).
#   ⚠ CLI 인자/env-var 방식 아님 — Claude Code는 stdin으로 JSON을 넘긴다.
#
# 캡처 가능 (결정론):
#   - ts          : 훅 발화 시각 (ISO8601 UTC) → retro가 task별 min/max로 minutes_elapsed 산출
#   - loc_delta   : Write=content 줄 수, Edit=new_string−old_string 줄 수, NotebookEdit=new_source 줄 수
#   - task        : .track/current_task 파일 (sprint/conductor가 태스크 시작 시 기록, 없으면 unassigned)
#   - exit_code   : tool_response.exit_code (없으면 0; 추정하지 않음)
# 캡처 불가 (정직하게 비움):
#   - tokens      : 훅 페이로드에 token usage 없음 → 기록하지 않음 (retro에서 null).
#   - minutes     : probe가 직접 기록하지 않음 → retro가 task별 ts min/max 차로 유도.
#
# Exit codes: 항상 0 (PostToolUse는 차단 불가, 추적만).

set -euo pipefail

TRACK_DIR=".track"
LOG="$TRACK_DIR/actual_log.jsonl"

# .track/ 없으면 추적 비활성 상태 — 조용히 종료 (init 전에는 기록하지 않음)
[ -d "$TRACK_DIR" ] || exit 0

INPUT="$(cat)"

# stdin JSON에서 필드 추출 + jsonl 한 줄 append (전부 python으로 — 결정론)
echo "$INPUT" | python3 -c '
import json, sys, datetime, os

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool = d.get("tool_name", "")
if tool not in ("Write", "Edit", "NotebookEdit"):
    sys.exit(0)

inp = d.get("tool_input", {}) or {}
file_path = inp.get("file_path", "") or inp.get("notebook_path", "")

def nlines(s):
    return len(s.splitlines()) if s else 0

if tool == "Write":
    loc_delta = nlines(inp.get("content", ""))
elif tool == "Edit":
    loc_delta = nlines(inp.get("new_string", "")) - nlines(inp.get("old_string", ""))
else:  # NotebookEdit
    loc_delta = nlines(inp.get("new_source", ""))

# 종료 코드: tool_response에 있으면 인용, 없으면 0 (추정 금지)
resp = d.get("tool_response", {})
exit_code = 0
if isinstance(resp, dict):
    exit_code = resp.get("exit_code", resp.get("exitCode", 0)) or 0

# 현재 태스크 (sprint/conductor가 기록, 없으면 unassigned)
task = "unassigned"
ct = os.path.join(".track", "current_task")
if os.path.exists(ct):
    task = open(ct).read().strip() or "unassigned"

entry = {
    "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "task": task,
    "event": "tool_call",
    "tool": tool,
    "file": file_path,
    "loc_delta": loc_delta,
    "exit_code": exit_code,
    "source": "hook",
}
with open(os.path.join(".track", "actual_log.jsonl"), "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
' 2>/dev/null || true

exit 0
