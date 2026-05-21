# Agent PRD: Automated Code Review Agent

---

## Overview

**Agent Name:** CodeReviewBot  
**Version:** 1.0  
**Date:** 2026-03-06

An autonomous agent that triggers on GitHub pull request events, analyzes code changes across three dimensions (security, style, performance), and posts structured inline comments directly on the PR diff.

---

## Problem Statement

Manual code review is a bottleneck. Reviewers spend significant time catching mechanical issues (SQL injection, unused imports, O(n²) loops) that can be automated—leaving human reviewers to focus on architecture, logic, and intent.

---

## Agent Architecture

```
GitHub Webhook (PR opened/updated)
         │
         ▼
    Trigger Layer
    ─────────────
    • Validate webhook signature (HMAC-SHA256)
    • Extract: repo, PR number, base/head SHAs, diff URL
    • Enqueue job (deduplicate on PR + head SHA)
         │
         ▼
    Orchestrator Agent
    ──────────────────
    • Fetch full diff via GitHub API
    • Split diff into file-level chunks
    • Fan out to 3 specialist sub-agents in parallel
         │
    ┌────┴─────────────────────┐
    ▼           ▼              ▼
Security     Style          Performance
Sub-Agent    Sub-Agent      Sub-Agent
    │           │              │
    └────┬───────┘──────────────┘
         ▼
    Aggregator Agent
    ────────────────
    • Deduplicate overlapping findings
    • Rank by severity
    • Format as GitHub Review comments (inline + summary)
         │
         ▼
    GitHub API
    • POST /repos/{owner}/{repo}/pulls/{number}/reviews
    • Inline comments anchored to diff positions
    • Summary comment with overall verdict
```

---

## Inputs

| Input | Source | Format |
|---|---|---|
| PR diff | GitHub REST API | Unified diff |
| Repository metadata | GitHub REST API | JSON |
| Config file | `.codereview.yml` in repo root | YAML |
| Language detection | File extensions + heuristics | — |
| Secrets baseline | Prior scan results (cache) | JSON |

### `.codereview.yml` Schema

```yaml
version: 1
checks:
  security:
    enabled: true
    severity_threshold: medium   # low | medium | high | critical
    ignore_paths: ["tests/fixtures/**"]
  style:
    enabled: true
    rulesets: ["pep8", "eslint-recommended"]
    ignore_rules: ["E501"]       # per-rule suppression
  performance:
    enabled: true
    ignore_paths: ["scripts/**"]
max_comments_per_pr: 40          # prevent comment flood
post_summary: true
block_merge_on: [critical]       # optional: set PR status check
```

---

## Sub-Agent Specifications

### 1. Security Sub-Agent

**Scope:** Detect vulnerabilities in the changed lines only (not full repo scan).

**Checks:**
- Injection flaws: SQL, command, LDAP, XPath
- Hardcoded secrets/credentials (entropy-based + pattern matching)
- Insecure deserialization
- Path traversal
- Dangerous function calls (`eval`, `exec`, `pickle.loads`, `innerHTML =`)
- Dependency additions in `package.json`, `requirements.txt`, `go.mod` → check against OSV/NVD

**Severity Levels:** `critical`, `high`, `medium`, `low`, `info`

**Model Behavior:**
- Analyze each changed hunk with the surrounding 10 lines of context
- Output structured JSON per finding: `{file, line, severity, rule_id, message, suggested_fix}`
- Do not flag the same pattern twice in the same file

---

### 2. Style Sub-Agent

**Scope:** Enforce language-specific conventions on changed lines.

**Checks:**
- Linting rule violations (configurable ruleset)
- Naming conventions (camelCase vs snake_case per language)
- Dead code: unused imports, unreachable branches
- Missing or malformed docstrings/comments on exported symbols
- Overly long functions (>50 lines), files (>500 lines)
- Consistent error handling patterns (e.g., not mixing `try/catch` and `.catch()` in same file)

**Behavior:**
- Suppress findings on lines that already have a `# noqa` / `// eslint-disable` annotation
- Group multiple style issues on the same line into a single comment

---

### 3. Performance Sub-Agent

**Scope:** Identify algorithmic and resource inefficiencies.

**Checks:**
- Nested loops over collections (O(n²) risk flagged, not blocked)
- Database queries inside loops (N+1 detection for common ORM patterns)
- Missing pagination on list endpoints
- Synchronous I/O in async contexts
- Unbounded memory growth: appending to global list/dict in a loop
- Regex compilation inside a loop (should be pre-compiled)
- Large payload serialization without streaming

**Behavior:**
- Flag with `suggestion` tone, not `error` — performance issues are rarely blocking
- Include a brief explanation of the asymptotic risk

---

## Outputs

### Inline Comment Format

```
**[SECURITY · HIGH]** `rule: hardcoded-secret`

A high-entropy string that resembles an API key was detected.
Hardcoded credentials can be leaked via version history even after removal.

**Suggested fix:**
```python
# Use environment variable instead
api_key = os.environ["SERVICE_API_KEY"]
```

_CodeReviewBot · [suppress this rule](link-to-docs)_
```

### PR Summary Comment

```markdown
## CodeReviewBot Summary

| Category    | Critical | High | Medium | Low |
|-------------|----------|------|--------|-----|
| Security    | 0        | 1    | 2      | 3   |
| Style       | —        | 0    | 4      | 7   |
| Performance | —        | 0    | 1      | 2   |

**Verdict:** ⚠️ Review required — 1 high-severity security issue found.

<details><summary>Suppressed findings (3)</summary>
...
</details>
```

### Commit Status (Optional)

If `block_merge_on: [critical]` is set, the agent posts a GitHub Check Run:
- `failure` if any critical findings exist
- `success` otherwise

---

## Tool Use

The orchestrator and sub-agents use the following tools:

| Tool | Purpose |
|---|---|
| `github_get_diff` | Fetch unified diff for the PR |
| `github_get_file` | Fetch full file content for context |
| `github_post_review` | Post inline comments + summary as a single Review |
| `github_post_check_run` | Set merge-blocking status |
| `osv_lookup` | Check new dependencies against OSV vulnerability DB |
| `cache_read` / `cache_write` | Store per-repo baseline to avoid re-flagging old issues |

---

## Failure Modes

### F1: GitHub API Rate Limiting
- **Trigger:** >5,000 requests/hour on the token
- **Behavior:** Exponential backoff (1s → 2s → 4s → 8s, max 3 retries). If still blocked, post a single PR comment: "CodeReviewBot is rate-limited; review will be reposted within 1 hour." Enqueue for retry.
- **Mitigation:** Use a GitHub App token (higher limits) rather than a PAT.

### F2: Diff Too Large
- **Trigger:** PR diff >5,000 lines or >100 files changed
- **Behavior:** Run security checks only (highest value). Post comment explaining partial review. Log skipped files.
- **Threshold:** Configurable via `max_diff_lines` in `.codereview.yml`.

### F3: Unsupported Language
- **Trigger:** File extension not in supported set
- **Behavior:** Skip file silently. Include in summary as "N files skipped (unsupported language)."
- **No false positives** — do not attempt heuristic analysis on unknown file types.

### F4: Model Hallucination / False Positive
- **Trigger:** Agent posts a finding with no actual evidence in the diff
- **Mitigation:** Each finding must include a `quoted_snippet` from the actual diff. Aggregator validates that the quoted snippet exists in the raw diff before posting. Findings without a valid snippet are dropped.
- **Recovery:** Users can react with 👎 on a comment to log negative feedback for fine-tuning.

### F5: Secrets in Diff Sent to Model
- **Trigger:** PR diff contains what appears to be a real secret
- **Behavior:** Before sending to the model, redact high-entropy strings matching secret patterns (replace with `[REDACTED-SECRET]`). The security sub-agent is still told "a potential secret was detected at this location" without seeing the raw value.
- **Note:** This is a privacy/security control on the agent itself.

### F6: Comment Flood
- **Trigger:** >40 findings (default `max_comments_per_pr`)
- **Behavior:** Post only the top N by severity. Remaining findings included as a collapsed `<details>` block in the summary comment. Never exceeds the cap as inline annotations.

### F7: `.codereview.yml` Invalid or Missing
- **Trigger:** Config file absent or fails schema validation
- **Behavior:** Fall back to safe defaults (all checks enabled, `medium` threshold, no paths ignored). Post an `info`-level comment once explaining the fallback.

### F8: Webhook Replay / Duplicate Trigger
- **Trigger:** GitHub retries a webhook delivery; same PR+SHA processed twice
- **Behavior:** Idempotency key = `{repo_id}:{pr_number}:{head_sha}`. If a completed review already exists for this key in the job store, no-op. Delete and repost only if the PR head SHA changes.

### F9: Agent Timeout
- **Trigger:** Sub-agent exceeds 120s (configurable)
- **Behavior:** Orchestrator cancels the sub-agent, marks that category as "timed out" in the summary comment, and posts the findings from completed sub-agents. Never blocks indefinitely.

### F10: GitHub API Outage
- **Trigger:** GitHub returns 5xx for >3 consecutive requests
- **Behavior:** Abort current run. Persist job in a retry queue with exponential backoff up to 6 hours. Post no comment (there's no point — GitHub is down). Alert on-call via configured webhook.

---

## Out of Scope (v1.0)

- Auto-applying suggested fixes (write access to the branch)
- Review of binary files, generated code, or vendored dependencies
- Tracking review coverage over time (v2 roadmap)
- Multi-repo policy enforcement
- Self-healing: creating issues for unfixed findings after merge

---

## Success Metrics

| Metric | Target |
|---|---|
| False positive rate | <10% of inline comments flagged as incorrect |
| Coverage (critical/high security issues) | >90% recall on test suite of known vulns |
| p95 review latency (PR open → comments posted) | <60 seconds |
| Comment flood rate | 0% of PRs exceed `max_comments_per_pr` |
| Agent timeout rate | <1% of runs |

---

## Security & Trust Model

- Agent runs with **read-only** repo access + PR comment write access. No push access.
- Webhook payloads validated via HMAC-SHA256 before any processing.
- All diff content treated as untrusted input — prompt injection via PR content is a known threat vector. Diffs are passed as **data** (inside a code block delimiter), never interpolated as instructions.
- Secret redaction (F5) applied before any external model call.
- Audit log of every review posted, retained 90 days.