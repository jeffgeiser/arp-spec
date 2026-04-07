# Phase 4: Reconcile

## Purpose

Reconcile is where the protocol generates intelligence. Every completed job produces three artifacts that make Score predictions more accurate, agent behavior more predictable, and fleet operations more stable. This is the flywheel.

## Tool Contract

### `settle_workload(reservation_id, actual_metrics)`

**Input:**
```json
{
  "reservation_id": "res-uuid-xxxx",
  "actual_metrics": {
    "duration_s": 52,
    "vram_used_gb": 27.8,
    "avg_wes": 8.4,
    "avg_tok_s": 42.5,
    "avg_power_w": 12.3,
    "thermal_state_worst": "Fair",
    "completion_status": "success"
  }
}
```

**Output:** `ReconcileReceipt` (see schema/reconcile-receipt.json)

```json
{
  "reservation_id": "res-uuid-xxxx",
  "settlement": {
    "credits_committed": 12,
    "credits_settled": 11.2,
    "adjustment": -0.8,
    "adjustment_reason": "Node delivered 8.4 WES vs predicted 9.1 (thermal degradation during run)"
  },
  "deltas": {
    "agent_accuracy": {
      "duration_predicted_s": 60,
      "duration_actual_s": 52,
      "vram_predicted_gb": null,
      "vram_actual_gb": 27.8,
      "accuracy_score": 0.87
    },
    "node_reliability": {
      "wes_predicted": 9.1,
      "wes_actual": 8.4,
      "thermal_stable": false,
      "reliability_score": 0.82,
      "note": "Thermal state degraded from Normal to Fair at T+34s"
    }
  }
}
```

## The Three Artifacts

### ActualResourceReceipt
What was promised vs. what was delivered. The financial settlement.

| Field | What it captures | What it feeds |
|-------|-----------------|---------------|
| credits_committed vs credits_settled | Over/under delivery | Fleet owner economics |
| WES predicted vs actual | Node performance gap | Score calibration |
| Duration predicted vs actual | Execution accuracy | Agent reputation |

### AgentAccuracyDelta
How accurately the agent predicted its own resource consumption.

- Duration: predicted vs actual
- VRAM: declared vs measured (if declared)
- Overall accuracy score (0.0–1.0)

This feeds the **agent reputation** system. Agents that consistently declare accurately earn lower Commit costs and priority scheduling.

### NodeReliabilityDelta
Whether the node honored its commitment.

- WES predicted (from Score at Commit time) vs actual
- Thermal stability during the run
- Overall reliability score (0.0–1.0)

This feeds **Score** directly. Unreliable nodes get lower Score predictions for future workloads.

## Settlement Rules

Settlement is **asymmetric by design**:

| Scenario | Outcome |
|----------|---------|
| Both deliver as committed | Receipt closes cleanly, both deltas trend positive |
| Node under-delivers (thermal throttle, WES degrades) | Agent gets pro-rated refund proportional to shortfall |
| Agent over-consumes (uses more VRAM than declared) | Bounded surcharge — capped, not punitive |

**Why bounded surcharges?** Over-penalizing trains agents to over-declare defensively, which corrupts the intent log. The surcharge should be enough to incentivize accuracy, not enough to make agents lie.

## The Flywheel

```
More Commits
    → Richer Reconciliation data
        → Better Score predictions
            → Agents trust the protocol more
                → More Commits
```

The product gets better without any new features shipping after Reconcile exists. Every reconciled job improves Score accuracy. This runs automatically.

## Auto-Settlement

If an agent doesn't call `settle_workload()` within 2x the declared `duration_estimate_s`:

1. System reads actual metrics from the hardware monitoring layer
2. Auto-generates the three artifacts using measured data
3. Settles with the agent's committed credits (no refund for timeout)
4. Marks the agent's accuracy delta as "auto-settled" (lower confidence)

This prevents credit lockup from crashed or misbehaving agents.
