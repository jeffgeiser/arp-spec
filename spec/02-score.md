# Phase 2: Score

## Purpose

Score transforms Sense data into a workload-specific prediction. Given a node and a workload description, Score returns a 0.0–1.0 fit scalar with a human-readable explanation of why.

## Tool Contract

### `score_node_fit(node_id, workload)`

**Input:**
```json
{
  "node_id": "WK-XXXX",
  "workload": {
    "model_family": "llama",
    "parameter_count_b": 70,
    "quantization": "Q4_K_M",
    "context_length": 8192,
    "batch_size": 1,
    "expected_duration_s": 60
  }
}
```

All workload fields except `model_family` are optional. Score degrades gracefully with missing information — it just widens confidence intervals.

**Output:** `ScoreResponse` (see schema/score-response.json)

```json
{
  "node_id": "WK-XXXX",
  "score": 0.73,
  "confidence": 0.85,
  "explanation": "Primary constraint: thermal headroom (node at 78C, 12C from throttle threshold). Secondary: VRAM margin tight for this context length at current batch size.",
  "constraints": [
    { "factor": "thermal_headroom", "weight": 0.30, "value": 0.58, "detail": "78C / 90C threshold, 12C margin" },
    { "factor": "vram_fit", "weight": 0.30, "value": 0.72, "detail": "28.5GB required, 32GB available (89% fill)" },
    { "factor": "wes_history", "weight": 0.25, "value": 0.85, "detail": "Similar workload baseline: 8.2 WES, current: 7.8 WES" },
    { "factor": "reliability", "weight": 0.15, "value": 0.92, "detail": "Node completed 47/50 recent jobs successfully" }
  ]
}
```

### `rank_fleet_for_workload(workload)`

Returns all accessible nodes ranked by fit score for a given workload.

**Input:** Same `workload` schema as `score_node_fit`.

**Output:** Array of `ScoreResponse` objects sorted by score descending. Includes a `recommended` field on the top-ranked node.

## Score Formula (v1)

Starting weights, adjustable based on Reconcile data:

| Factor | Weight | Source |
|--------|--------|--------|
| Thermal headroom | 30% | Current temp vs throttle threshold, thermal trend slope |
| VRAM fit | 30% | Model VRAM requirement vs available, accounting for KV cache overhead |
| WES history | 25% | Historical WES for similar workloads on this node (DuckDB per-model baseline) |
| Node reliability | 15% | Reconcile history — what fraction of recent Commits completed successfully |

## Design Decision: Score Must Be Explainable

Not just `0.73` but: "0.73 — primary constraint: thermal headroom." An agent that can explain its routing decision to a human operator is dramatically more trustworthy. The `constraints` array in the response enables this.

## Relationship to Sense

Score consumes Sense data. It reads the fleet context and node status that Sense provides, then applies workload-specific reasoning. A Score implementation without Sense is not possible.

## Feedback Loop

When Reconcile exists (Phase 4), the Score formula incorporates `NodeReliabilityDelta` history automatically. Score predictions improve with each reconciled job without any manual tuning. This is the beginning of the flywheel.
