# RFC 0001: Initial ARP Specification

**Author:** Jeff Geiser
**Date:** April 2026
**Status:** Draft

## Problem Statement

The emerging agentic infrastructure stack has well-defined protocols for connection (MCP), discovery (A2A), and commerce (ACP). None of them specify what happens when an agent needs to reason about physical compute it controls — whether to use a specific node, how to declare intent before using it, and what the system learns when the job completes.

This gap exists because the existing stack was built for a different customer: a human with a browser provisioning cloud resources. The new customer is an LLM making tool calls about infrastructure it already has access to.

## Design Alternatives Considered

### Why not extend MCP?

MCP is a transport and tool-binding protocol. It answers "how does an agent call a tool?" ARP answers "what should the tool's semantics be for resource allocation?" These are different layers. ARP tools are MCP tools — the protocol adds semantic requirements on top, not a competing transport.

### Why not adapt ACP for compute?

ACP (Agentic Commerce Protocol) handles product catalogs, checkout, payment tokens. It's designed for commercial transactions between strangers. ARP is designed for resource allocation within a sovereign fleet — the agent and the infrastructure are controlled by the same operator. The trust model, settlement mechanics, and data ownership are fundamentally different.

### Why four phases and not three or five?

Every resource allocation problem in computing has the same shape: discover → evaluate → reserve → settle. DNS lookup → TCP handshake → data transfer. Service discovery → health check → connection pool. Four is the natural decomposition. We considered merging Sense and Score (a single "evaluate" phase) but separated them because Sense is stateless (read current state) while Score is stateful (requires workload context and historical data). We considered splitting Reconcile into "settle" and "learn" but kept them together because settlement is meaningless without the learning — the delta computations are the point, not the credit transfer.

## Core Design Decisions

### Intent declaration before execution

Most infrastructure systems log what happened after the fact. ARP requires agents to declare what they plan to do before they do it. This is uncomfortable — it adds latency and complexity. We require it because:

1. The declared-vs-actual delta is the training signal for Score. Without intent, you can measure what happened but not how well the prediction worked.
2. Over-subscription prevention requires knowing what's coming, not just what's running.
3. The agent reputation system requires a baseline to compare against.

### Asymmetric settlement

When a node under-delivers, the agent gets a refund. When an agent over-consumes, the surcharge is bounded (capped). This asymmetry is deliberate: over-penalizing agents trains them to over-declare defensively (request 16GB when they need 8GB), which corrupts the intent log and makes Score predictions worse. The system should incentivize honest declaration, not conservative declaration.

### Agent reputation at fleet level

Most governance systems focus on the resource: is the node healthy, is capacity available. ARP also governs the consumer. An agent that consistently over-declares, crashes mid-job, or spikes VRAM unpredictably gets a higher credit cost — not as punishment, but as actuarially correct pricing of unpredictability. This is the first framework where hardware rates the agents running on it.

### Credits as coordination, not billing

In the operator model, credits are not money. They are a coordination primitive that enforces a resource budget across the fleet without centralized scheduling. The fleet owner sets the pool. Agents draw from it. The credit price encodes predictability (node reliability x agent reputation x predicted WES), not just compute time.

## Known Limitations of v0.1

- Score formula is heuristic-weighted, not ML-trained. The weights are starting points; Reconcile data will eventually justify a learned model.
- Agent identity is assumed (fleet owner issues IDs). Cryptographic agent certificates are the right long-term answer but add complexity to v1.
- Multi-fleet support is not specified. Credits and reputation are scoped to a single fleet in v0.1.
- The spec assumes the hardware monitoring layer exists (Wicklee or equivalent). ARP does not specify how hardware telemetry is collected — only how it is consumed.

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/) — Anthropic / Linux Foundation
- [A2A Protocol](https://github.com/google/A2A) — Google
- [ACP Specification](https://www.agenticcommerce.org/) — OpenAI + Stripe
- [Wicklee](https://wicklee.dev) — Reference implementation of ARP Sense
