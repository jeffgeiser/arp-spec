# Phase 3: Commit

## Purpose

Commit is the intent declaration. Before an agent uses a resource, it declares what it expects to use, for how long, and how many credits it stakes on that prediction. This creates an audit trail, prevents over-subscription, and generates the ground-truth data that Reconcile needs.

## Tool Contract

### `commit_workload_intent(intent)`

**Input:** `WorkloadIntent` (see schema/workload-intent.json)

```json
{
  "agent_id": "agent-claude-desktop-01",
  "node_id": "WK-A1B2",
  "model_family": "llama",
  "parameter_count_b": 70,
  "quantization": "Q4_K_M",
  "context_length": 8192,
  "duration_estimate_s": 60,
  "credits_committed": 12
}
```

**Required fields:** `agent_id`, `node_id`, `duration_estimate_s`, `credits_committed`. Everything else optional — the schema tightens as adoption provides data on what agents actually declare.

**Output:**
```json
{
  "reservation_id": "res-uuid-xxxx",
  "status": "committed",
  "credits_escrowed": 12,
  "expires_at_ms": 1234567890000,
  "score_at_commit": 0.73
}
```

### `release_intent(reservation_id)`

Graceful cancellation. Releases escrowed credits. No penalty for early release — the system should not discourage agents from being conservative.

**Input:** `{ "reservation_id": "res-uuid-xxxx" }`

**Output:** `{ "status": "released", "credits_returned": 12 }`

## Credit Model

In the operator model, credits are not a payment mechanism — they are a **coordination primitive**.

- The fleet owner sets the credit pool
- Agents draw from it when they Commit
- The pool enforces a resource budget across the fleet without centralized scheduling
- Credits represent **predicted resource consumption**, not compute time or money

### Why Credits, Not Just Reservations

A simple reservation system (lock node for N seconds) doesn't capture the asymmetry of inference workloads. A 70B model on a thermally marginal node is more "expensive" than the same model on a cool, high-WES node. Credits encode this: the credit price for a Commit reflects the node's current state, not just VRAM x time.

Credit price = f(node_reliability_history, agent_reputation, predicted_WES, thermal_headroom)

You are pricing **predictability**. Predictability has a real cost to produce, and now it has a real price.

## Design Decision: Lightweight Schema

Commit must be lightweight enough that agents actually use it. If declaring intent is expensive or requires 15 fields, agents skip it — and you lose the entire Reconcile flywheel.

v1 requires only 4 fields. The rest are optional. Tighten the schema as adoption gives you data on what agents actually declare.

## Escrow Mechanics

- Credits debited from agent's pool at Commit time
- Held in escrow until Reconcile
- If agent doesn't call `settle_workload()` within 2x `duration_estimate_s`, the system auto-settles (prevents credit lockup from crashed agents)
- Released credits return to the pool immediately
