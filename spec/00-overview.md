# ARP Overview

## Why ARP Exists

The existing agentic protocol stack — MCP (tool connection), A2A (agent discovery), ACP (commerce) — solves how agents connect to services. None of them specify what happens after connection when the service is physical compute that an operator controls.

ARP fills this gap for a specific scenario: **an agent reasoning about inference compute on hardware it already has access to.** Not a marketplace. Not rented cloud. Sovereign infrastructure where the operator owns the nodes and the agents run locally.

## The Operator Model

ARP assumes the operator model, not the consumer model:

| Consumer model | Operator model (ARP) |
|---|---|
| Agents roaming a marketplace of GPU time | Agents reasoning about infrastructure they control |
| ARP as hotel booking | ARP as fleet management |
| Trust established via marketplace reputation | Trust established via local Reconcile history |

The operator model is more defensible: the customer already owns hardware, the feedback loop is local (Score predictions improve faster), and sovereignty is the feature.

## Where ARP Sits in the Stack

```
┌──────────────────────────────────────────┐
│  Agent Application (Claude, GPT, custom) │
├──────────────────────────────────────────┤
│  MCP — tool connection                   │
│  A2A — agent-to-agent discovery          │
│  ACP — commerce / payments               │
├──────────────────────────────────────────┤
│  ARP — resource execution layer          │  ← This spec
│  Sense → Score → Commit → Reconcile      │
├──────────────────────────────────────────┤
│  Hardware (GPU, CPU, memory, thermals)   │
└──────────────────────────────────────────┘
```

ARP runs over MCP. It is complementary, not competing. An ARP Sense tool is an MCP tool. An ARP Score response is an MCP tool response. The protocol adds semantics on top of MCP's transport.

## The Four Phases

1. **Sense** — "What is the state of my fleet right now?" Structured, decision-ready payload.
2. **Score** — "Which node fits this workload?" A 0.0–1.0 prediction with explanation.
3. **Commit** — "I am claiming this node and declaring my intent." Soft reservation with credit escrow.
4. **Reconcile** — "Did reality match intent? What does the fleet learn?" Settlement + training data for Score.

Each phase is independently useful. Each makes prior phases more valuable. The flywheel begins at Reconcile.
