# Changelog

## Unreleased

- `spec/02-score.md`: `wes_history` is now continuous. The `0.50 <= ratio < 0.80` band is `2.5 * (ratio - 0.50)` (was `0.50 * ratio`, which dropped from 0.75 to 0.40 at `ratio = 0.80`).
- `spec/02-score.md` and `examples/02-score-response.json`: the worked WES numbers in the `wes_history` details now match the formula (the factor values and composite scores are unchanged).
- `implementations/`: list arp-agent.
- `scripts/validate.py` (+ `requirements-dev.txt`): checks every schema is a valid JSON Schema for the draft it declares, every `$id` is unique, and every example validates against its schema. Intended for CI.
- `examples/`: end-to-end payload set tracing one workload through Sense → Score → Commit → Reconcile
- `CONTRIBUTING.md`: how to file issues, submit RFCs, and list implementations
- `spec/02-score.md`: per-factor computation defined for thermal_headroom, vram_fit, wes_history, reliability, and confidence — v0.1 starting heuristics so independent implementations produce comparable scores
- `spec/02-score.md`: low-confidence flag in `explanation` is now MUST (was SHOULD)
- `SPEC.md` §3: Score formula now references the per-factor definitions
- `schema/`: all four schemas now declare `$id`, set `additionalProperties: false` on every object, and reference the matching `examples/` payload in their description. Examples validate clean against the tightened schemas.
- `.gitignore`: added

## 0.1.0 — April 2026

- Initial draft specification
- Sense phase: fleet context and node status schemas
- Score phase: workload input schema and fit score output format
- Commit phase: intent schema and credit model (draft)
- Reconcile phase: settlement artifacts and delta computations (draft)
- Founding RFC: design rationale
