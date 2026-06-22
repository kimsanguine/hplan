# Good — 단일 스킬셋을 두 하네스(Claude Code + Codex)로 유지

지금 필요: 멀티 하네스 이식성 (표준 베팅 아님)

```
본체:        SKILL.md 한 벌 (Claude Code·Codex 양쪽 복사 가능)
비이식:      슬래시 commands·hooks → 하네스별 얇은 어댑터로 격리
                - Claude Code: .claude-plugin/commands
                - Codex: AGENTS.md 기반 진입점
durable state: markdown+frontmatter 파일 (메모리·결정 로그·인덱스)
선택 표준:    MCP는 도구 연결 어댑터로만 사용, 상태는 표준에 안 묶음
lock-in:     Low — 전송/하네스 교체해도 본체·상태 보존
재검토:      구글·MS 연결 표준 생태계가 임계 도달 시 어댑터 1개 추가
```

왜 좋은가
- 이식 가능 자산(스킬 본문)과 비이식 자산(commands/hooks)을 물리적으로 분리
- 상태를 파일에 둬서 하네스가 바뀌어도 안 잃음
- 새 표준은 "어댑터 추가" 한 번으로 흡수 — 본체 재작성 없음
- 두 하네스를 별도 코드베이스로 포크하지 않고 한 벌 + 어댑터로 유지
