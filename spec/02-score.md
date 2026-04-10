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

The composite score is the weighted sum of the four per-factor values:

```
score = 0.30 * thermal_headroom
      + 0.30 * vram_fit
      + 0.25 * wes_history
      + 0.15 * reliability
```

Each factor returns a value in `[0.0, 1.0]`, where `1.0` means "no concern at all" and `0.0` means "this factor alone makes the workload infeasible." The composite is therefore also in `[0.0, 1.0]`.

## Per-Factor Computation (v0.1)

These are the v0.1 starting heuristics. They are explicit so two independent implementations produce comparable scores. Reconcile data will eventually justify learned replacements; the formulas below are the floor, not the ceiling.

### Thermal headroom

```
margin_c    = throttle_c - current_c
headroom    = clamp(margin_c / target_margin_c, 0.0, 1.0)
trend_slope = ΔC over last 60s     (positive = warming)
trend_pen   = clamp(1.0 - max(0, trend_slope) / 5.0, 0.0, 1.0)
thermal_headroom = headroom * trend_pen
```

- `throttle_c` is the platform throttle threshold (e.g. `90` for Apple Silicon).
- `target_margin_c` is the comfort margin v0.1 considers "fully safe" — default `30`. A node 30°C below throttle returns `1.0`; a node at the threshold returns `0.0`.
- `trend_pen` reduces the score when temperature is climbing fast (5°C/minute warming → `0.0` penalty multiplier).
- The `current_c` reading is the hottest sensor reported by the platform monitoring layer.

### VRAM fit

```
required_gb = model_weights_gb + kv_cache_gb(context_length, batch_size)
available_gb = vram_total_gb - vram_baseline_gb
fill_ratio   = required_gb / available_gb

vram_fit =
    1.00  if fill_ratio <= 0.60
    1.00 - 0.75 * (fill_ratio - 0.60) / 0.30   if 0.60 < fill_ratio <= 0.90
    0.25 - 0.25 * (fill_ratio - 0.90) / 0.10   if 0.90 < fill_ratio <= 1.00
    0.00  if fill_ratio > 1.00
```

- `kv_cache_gb` is computed from the model architecture and `context_length * batch_size`. Implementations SHOULD use a per-model lookup table and SHOULD fall back to a conservative estimate (`0.0005 * parameter_count_b * context_length / 1000` GB) when the model is unknown.
- `vram_baseline_gb` accounts for OS/driver overhead. Default: `2.0` GB on Apple Silicon, `1.0` GB on discrete GPUs. Implementations SHOULD measure this empirically.
- The piecewise curve gives full credit below 60% fill, degrades smoothly to 0.25 at the 90% boundary, then drops sharply to zero at OOM. The sharp tail above 90% is intentional: predictability collapses near OOM.

### WES history

```
baseline = rolling_mean(WES for last N runs of same model on this node)
current  = current_WES
ratio    = current / baseline

wes_history =
    1.00 if ratio >= 1.05
    ratio - 0.05 if 0.80 <= ratio < 1.05
    0.50 * ratio if 0.50 <= ratio < 0.80
    0.0  if ratio < 0.50
```

- `N = 14` for v0.1 (roughly two weeks of one job/day per model). Implementations MAY use a different window but MUST document it.
- "Same model" matches on `(model_family, parameter_count_b, quantization)`. Different context lengths share a baseline; future versions may stratify.
- If fewer than 3 prior runs exist for the (node, model) pair, `wes_history` defaults to `0.7` and Score MUST reduce its `confidence` field by at least `0.2`. Cold-start penalty.

### Node reliability

```
window = last 30 days of Reconcile receipts for this node
clean  = receipts with reliability_score >= 0.85
total  = all receipts in window

reliability =
    0.50 if total < 5         (cold start)
    clean / total otherwise
```

- A `reliability_score >= 0.85` from Reconcile counts as "clean" — that threshold is what "the node honored its commitment" reduces to in practice.
- Cold start (`total < 5`) returns `0.50` rather than `1.0` so a brand-new node doesn't get over-recommended before it has a track record.
- Auto-settled receipts (timeout) count as `total` but are excluded from `clean` regardless of their score.

### Confidence

The `confidence` field returned alongside `score` reflects how much data went into the prediction. Starting heuristic:

```
confidence = 0.95
           - 0.20 * (1 if cold-start WES history else 0)
           - 0.15 * (1 if total < 5 reliability receipts else 0)
           - 0.10 * (1 if any required workload field missing else 0)
```

Floor at `0.30`. A score with `confidence < 0.50` SHOULD be flagged in `explanation` so the agent can decide whether to escalate or fall back.

## Design Decision: Score Must Be Explainable

Not just `0.73` but: "0.73 — primary constraint: thermal headroom." An agent that can explain its routing decision to a human operator is dramatically more trustworthy. The `constraints` array in the response enables this.

## Relationship to Sense

Score consumes Sense data. It reads the fleet context and node status that Sense provides, then applies workload-specific reasoning. A Score implementation without Sense is not possible.

## Feedback Loop

When Reconcile exists (Phase 4), the Score formula incorporates `NodeReliabilityDelta` history automatically. Score predictions improve with each reconciled job without any manual tuning. This is the beginning of the flywheel.
