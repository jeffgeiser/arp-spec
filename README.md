# Agentic Resource Protocol (ARP)

**An open specification for how AI agents interact with inference compute they control.**

ARP defines four phases — **Sense, Score, Commit, Reconcile** — that together give agents the ability to observe fleet state, predict workload fit, declare intent before execution, and settle the difference between what was promised and what was delivered.

---

## The Gap ARP Fills

| Protocol | What it does | Status |
|----------|-------------|--------|
| **MCP** | How agents connect to tools and data sources | Shipped (Anthropic → Linux Foundation) |
| **A2A** | How agents discover and delegate to each other | Shipped (Google) |
| **ACP** | How agents handle commercial transactions | Shipped (OpenAI + Stripe) |
| **ARP** | What happens after connection — should I use this resource? How do I declare intent? What does the system learn when I'm done? | This spec |

MCP, A2A, and ACP get agents to the door. ARP is what happens after they walk through it.

## The Four Phases

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────────┐
│  SENSE  │ ──▶ │  SCORE  │ ──▶ │ COMMIT  │ ──▶ │  RECONCILE  │
│         │     │         │     │         │     │             │
│ "What   │     │ "Which  │     │ "I am   │     │ "Did        │
│  is the │     │  node   │     │  claiming│     │  reality    │
│  state  │     │  fits?" │     │  this    │     │  match      │
│  of my  │     │         │     │  node."  │     │  intent?"   │
│  fleet?"│     │ 0.0–1.0 │     │         │     │             │
└─────────┘     └─────────┘     └─────────┘     └─────────────┘
                                                       │
                                                       ▼
                                                 Feeds Score
                                                 (flywheel)
```

### Sense — Context
A structured, LLM-ready payload of node health, thermal headroom, and availability. Not raw metrics — a decision-ready feed.

### Score — Match
A scalar 0.0–1.0 prediction of execution success for a specific model on a specific node. Thermals, VRAM pressure, WES history — abstracted to a confidence value.

### Commit — Reserve
An intent schema that soft-reserves compute before execution. Credits into escrow. Prevents over-subscription. The audit trail starts here.

### Reconcile — Settle
Three artifacts: `ActualResourceReceipt`, `AgentAccuracyDelta`, `NodeReliabilityDelta`. Training data that makes Score smarter every cycle. The flywheel.

## Key Design Principles

- **Operator model, not consumer model.** ARP is for agents reasoning about infrastructure they already control — not agents shopping a marketplace. You own the hardware.
- **Metal-layer signals.** Score accuracy requires driver-level data: VRAM thrashing, PCIe saturation, thermal throttle timing, clock degradation under sustained load. You can't get this from a cloud API.
- **Reconcile is the moat.** Every completed job writes training data that improves Score predictions. The flywheel runs automatically.
- **Agent reputation.** Infrastructure tooling has always let operators rate their hardware. ARP is the first framework that lets your hardware rate the agents running on it.

## Specification

| Document | Description |
|----------|-------------|
| [SPEC.md](SPEC.md) | Full normative specification (single file) |
| [spec/](spec/) | Same content, navigable by phase |
| [schema/](schema/) | JSON Schema definitions for all payloads |
| [examples/](examples/) | Example payloads for each phase |
| [rfcs/](rfcs/) | Design rationale and founding decisions |

## Implementations

| Implementation | Phases | Status |
|---------------|--------|--------|
| [Wicklee](https://wicklee.dev) | Sense (complete), Score (in progress) | Reference implementation |

See [implementations/](implementations/) for details.

## Version

**Current: 0.1.0** (draft)

The spec will reach 1.0.0 when at least two independent implementations exist. See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT — see [LICENSE](LICENSE).

## Contributing

ARP is developed in the open. Issues, RFCs, and PRs welcome. The protocol is more valuable than any single implementation. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to file issues, submit RFCs, and list implementations.
