# hplan MCP Server

This wraps hplan's deterministic helpers as MCP tools so any MCP-compatible host
(Cursor, Windsurf, Kiro, Codex, Goose, Claude Desktop, ...) can call the same
Product Build Gate primitives that the Claude Code skill uses.

## Install

```bash
pip install mcp
```

## Run

From the skill root directory:

```bash
python3 hplan_mcp/server.py
```

> The local package is named `hplan_mcp/` (not `mcp/`) to avoid shadowing the
> installed `mcp` PyPI package.

## Register

### Claude Desktop / Claude Code

`~/.claude/mcp.json` (or via `claude mcp add`):

```json
{
  "mcpServers": {
    "hplan": {
      "command": "python3",
      "args": ["/absolute/path/to/hplan/skills/hplan/hplan_mcp/server.py"]
    }
  }
}
```

### Cursor

`.cursor/mcp.json` (프로젝트 루트 또는 `~/.cursor/mcp.json` 글로벌):

```json
{
  "mcpServers": {
    "hplan": {
      "command": "python3",
      "args": ["/absolute/path/to/hplan/hplan_mcp/server.py"],
      "env": {}
    }
  }
}
```

Cursor 설정 방법:
1. `Cmd+Shift+P` → "MCP: Configure"
2. 위 JSON을 `.cursor/mcp.json`에 저장
3. Cursor 재시작 → 우하단 MCP 아이콘에서 `hplan` 확인

### Windsurf / Kiro / Goose

각 호스트는 자체 MCP 설정 파일을 가지지만 스키마는 동일하다 —
`command`를 `python3`, `args`를 `server.py` 절대 경로로 지정.
설정 파일 위치: Windsurf는 `~/.windsurf/mcp.json`, Kiro는 `.kiro/mcp.json`.

### 기타 MCP 호환 호스트

MCP 프로토콜을 지원하는 모든 호스트 (Codex, 기타 에이전트 프레임워크)에서
동일한 방식으로 `server.py`를 등록할 수 있다.
설정 형식이 다를 경우 해당 호스트 문서의 "Add MCP server" 섹션을 참조.

## Tools

| Tool | Purpose |
|---|---|
| `evidence_check(brief)` | Score Evidence Gate readiness |
| `product_gate(brief)` | Check Product Gate artifacts |
| `cogs_calc(params)` | Run COGS sentinel — p50/p90 margin scenarios |
| `decision_log(entry)` | Append build/interview/pivot/hold decision |
| `exclusion_check(idea)` | Match against append-only exclusions registry |
| `handoff(brief, target)` | Export to spec-kit / kiro / gstack / claude |

## Design Note

The MCP server intentionally exposes **deterministic** primitives only. Prompt-level
gate rules (the 22 "Do Not" rules in `SKILL.md`) stay in the skill — the MCP server
gives every host *measurable* checks, not opinions.
