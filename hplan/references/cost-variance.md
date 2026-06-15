# Cost Variance Priors — p90/p50 per-call cost ratio

COGS Sentinel models per-call cost as a lognormal distribution. The p90/p50 ratio
controls how heavy the right tail is. Instead of one hardcoded constant, the ratio is
resolved in layers (best available source wins):

```
1. measured    realtime mode — actual production p90/p50 from logs
2. distribution --p90-p50-ratio — computed from your own token distribution
3. workload     --workload {chat|rag|agent|batch} — research-calibrated prior (below)
4. fallback     2.2 — unchanged default for backward compatibility
```

## Workload priors (research-calibrated)

| workload | p90/p50 | confidence | basis |
|---|---|---|---|
| chat   | 2.3 | Med  | Azure Inference Trace 2023 (mixed p90/p50≈2.7), LMSYS-Chat subset; chat CV is the lowest (0.6–0.8) |
| rag    | 3.0 | Low  | input dominated by context-chunk count variance; estimated as mixed-trace + RAG context spread |
| agent  | 5.0 | Med-High | VIDUR agent-heavy trace p90/p50=4.0 (measured); LMSYS overall 4.62; MCP-agent tasks ~122K vs RAG ~47K tokens |
| batch  | 1.8 | Low  | schema-bound structured extraction caps output length; Azure code-completion median 13 tokens (tight) |
| *(fallback)* | 2.2 | — | legacy default kept to avoid silently shifting existing verdicts |

> Values are single representative points inside the researched ranges
> (chat 2.0–2.5, rag 2.5–3.5, agent 4.0–6.0, batch 1.5–2.0). Ratios are for **output**
> tokens primarily; agentic total-token ratios run higher due to input accumulation.

### Sources
- arXiv:2604.00499 — "Scheduling LLM Inference with Uncertainty-Aware Output Length Predictions" (2025). LMSYS-Chat-1M: **p90/p50=4.62, p99/p50=10.77, CV=1.09**.
- VIDUR, MLSys 2024 — Azure traces: mixed p90≈4,242 (p90/p50≈2.7); agent-heavy p90=16,384 (p90/p50=4.0).
- DynamoLLM, HPCA 2025 / Azure LLM Inference Dataset 2024 — code-completion median 13 tok vs chat median 129 tok (10× workload spread).
- CASTILLO, arXiv:2505.16881 (2025) — response-length distributions are lognormal; CV 0.6–1.2; p99/p50 ≈ 4–8.

> Note: the fallback (2.2) is a known underestimate vs measured mixed traces (~2.7);
> raising it shifts every existing verdict, so that change is left as an explicit
> operator decision, not a silent default.

## Caching / batch multipliers

`cost_per_call` accepts optional `cached_tokens_in` and `batch`:
- Cached input tokens bill at **0.1×** (Anthropic prompt-caching read rate).
- `batch=True` bills all tokens at **0.5×** (Batch API).
- Defaults (`cached_tokens_in=0`, `batch=False`) reproduce the legacy full-price formula exactly.

> Cache *write* cost (1.25×/2× one-time) is intentionally not modeled here — it amortizes
> away in steady-state per-call COGS. Model it separately if writes dominate.

## Pricing snapshot freshness

`references/provider_pricing.json` carries `_meta.snapshot_date`. The CLI warns (stderr)
when the snapshot is older than 30 days. The snapshot is reference-only — verify against
current provider docs before publishing margins. (Pricing numbers themselves are updated
separately, not by this change.)
