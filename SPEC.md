# Agentic Resource Protocol — Specification v0.1.0

**Status:** Draft
**Date:** April 2026
**License:** MIT

---

## 1. Overview

The Agentic Resource Protocol (ARP) specifies how AI agents interact with inference compute they control. It defines four phases that together give agents the ability to observe fleet state, predict workload fit, declare intent before execution, and settle the difference between what was promised and what was delivered.

ARP is designed for the **operator model**: agents reasoning about infrastructure they already have access to — not agents shopping a marketplace. The operator owns the hardware. The agents run locally. The data stays sovereign.

ARP runs over MCP. It is complementary, not competing. ARP tools are MCP tools with additional semantic requirements.

## 2. Sense

Sense provides a structured, decision-ready view of fleet state. Every numeric field MUST include a machine-readable status assessment. Every degraded or critical status MUST include a suggested action.

### Tools

- `get_fleet_context()` — Returns all nodes with current state, WES scores, thermal conditions, and recommendations. Schema: `schema/fleet-context.json`.
- `get_node_status(node_id)` — Deep dive on a single node with full hardware telemetry.

### Event Stream

SSE-based real-time state change notifications: node online/offline, inference state transitions, thermal changes, observation patterns fired/resolved.

## 3. Score

Score transforms Sense data into a workload-specific prediction. Given a node and a workload description, returns a 0.0–1.0 fit scalar with explanation.

### Tools

- `score_node_fit(node_id, workload)` — Returns fit score, confidence, explanation, and per-factor constraint breakdown. Schema: `schema/score-response.json`.
- `rank_fleet_for_workload(workload)` — All nodes ranked by fit score for dispatch decisions.

### Formula (v1)

Thermal headroom (30%) + VRAM fit (30%) + WES history (25%) + Node reliability (15%). Weights adjust based on Reconcile data.

### Requirement: Explainability

Score MUST return a human-readable explanation naming the primary constraint. An agent that can explain its routing decision to a human operator is more trustworthy.

## 4. Commit

Commit is intent declaration. Before using a resource, agents declare what they expect to use, for how long, and how many credits they stake.

### Tools

- `commit_workload_intent(intent)` — Validates, debits credits to escrow, returns reservation ID. Schema: `schema/workload-intent.json`.
- `release_intent(reservation_id)` — Graceful cancellation, returns escrowed credits.

### Required Fields

`agent_id`, `node_id`, `duration_estimate_s`, `credits_committed`. All other fields optional.

### Credits

Credits are coordination primitives, not billing. The fleet owner sets the pool. Credit price = f(node_reliability, agent_reputation, predicted_WES, thermal_headroom).

## 5. Reconcile

Reconcile produces three artifacts from every completed job. These artifacts are training data for Score and the basis for agent reputation.

### Tools

- `settle_workload(reservation_id, actual_metrics)` — Returns receipt with settlement and deltas. Schema: `schema/reconcile-receipt.json`.
- `get_agent_reputation(agent_id)` — Queryable reputation score.
- `get_node_reliability(node_id)` — Queryable reliability score.

### Artifacts

1. **ActualResourceReceipt** — Promised vs delivered. Financial settlement.
2. **AgentAccuracyDelta** — Declared vs actual consumption. Feeds agent reputation.
3. **NodeReliabilityDelta** — Whether the node honored its commitment. Feeds Score.

### Settlement Rules

- Node under-delivers: agent gets pro-rated refund
- Agent over-consumes: bounded surcharge (capped, not punitive)
- Both deliver: receipt closes cleanly, both deltas positive

### Auto-Settlement

If agent doesn't settle within 2x declared duration, system auto-settles from measured metrics.

## 6. Agent Identity

Agents are identified by `agent_id` strings. In v0.1, the fleet owner issues IDs manually or auto-generates UUIDs. Cryptographic agent certificates are planned for v1.0.

Reputation is scoped to the fleet in v0.1. Reputation portability across fleets is planned for v1.0 (opt-in).

## 7. Conformance

An implementation conforms to ARP at a specific phase level:

- **Sense-conformant:** Implements `get_fleet_context` and `get_node_status` with status assessments and suggested actions.
- **Score-conformant:** Additionally implements `score_node_fit` with explanation and constraints.
- **Commit-conformant:** Additionally implements `commit_workload_intent` with credit escrow.
- **Full ARP:** Additionally implements `settle_workload` with all three delta artifacts.

Each level is independently useful and testable.
