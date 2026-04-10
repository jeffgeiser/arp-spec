# Changelog

## Unreleased

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
