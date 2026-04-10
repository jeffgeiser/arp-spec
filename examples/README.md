# ARP Examples

These payloads trace **a single workload end-to-end** through all four ARP phases. The same agent (`agent-claude-desktop-01`), the same target node (`WK-A1B2`), and the same workload (Llama 70B Q4_K_M, 8K context) thread through Sense → Score → Commit → Reconcile so a reader can follow one job from "what does my fleet look like?" to "what did the system learn?"

| File | Phase | Description |
|------|-------|-------------|
| [`01-sense-fleet-context.json`](01-sense-fleet-context.json) | Sense | Response from `get_fleet_context()`. Three nodes: one healthy, one thermally degraded, one offline. |
| [`02-score-response.json`](02-score-response.json) | Score | Response from `score_node_fit("WK-A1B2", workload)` for the 70B Q4_K_M workload. |
| [`03-commit-intent.json`](03-commit-intent.json) | Commit | Input to `commit_workload_intent(intent)` claiming WK-A1B2 for 60 seconds with 12 credits escrowed. |
| [`04-reconcile-receipt.json`](04-reconcile-receipt.json) | Reconcile | Output of `settle_workload(reservation_id, actual_metrics)` after the job completes in 52s with 8.4 actual WES. |

## The Story These Examples Tell

1. **Sense** — Agent calls `get_fleet_context()`. Sees `WK-A1B2` (healthy, 9.1 WES, Normal thermal), `WK-C133` (degraded, thermal penalty, busy), `WK-D204` (offline).
2. **Score** — Agent asks Score to evaluate `WK-A1B2` for the 70B workload. Gets back `0.84` with the primary constraint identified as VRAM fit at 89% fill.
3. **Commit** — Agent declares intent: 60-second job, 12 credits escrowed. System returns `reservation_id` and locks the credits.
4. **Reconcile** — Job finishes in 52s. Actual WES was 8.4 (predicted was 9.1 — node thermal degraded mid-run). Settlement refunds 0.8 credits (asymmetric: agent gets the refund). Two delta artifacts feed back into Score and agent reputation.

## Notes for Implementors

- These examples are illustrative, not normative. The schemas in [`schema/`](../schema/) are the source of truth.
- Numeric values are realistic but chosen for narrative clarity, not measured from a real fleet.
- Timestamps use Unix milliseconds throughout (consistent with the schemas).
- The `reservation_id` in `03` matches the one referenced in `04` so you can verify the linkage.
