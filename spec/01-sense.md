# Phase 1: Sense

## Purpose

Sense provides agents with a structured, decision-ready view of fleet state. Not raw metrics — pre-digested context with recommended actions and confidence scores. The agent's DNS lookup for its own infrastructure.

## Tool Contract

### `get_fleet_context()`

Returns the current state of all nodes the agent has access to.

**Input:** None required. Optional `node_filter` to scope to specific nodes.

**Output:** `FleetContext` (see schema/fleet-context.json)

Every field in the response includes:
- A current value
- A machine-readable status (`healthy`, `degraded`, `critical`)
- A suggested action when status is not healthy
- A confidence score (0.0–1.0) for the status assessment

### `get_node_status(node_id)`

Deep dive on a single node.

**Input:** `{ "node_id": "string" }`

**Output:** Full `NodeStatus` with hardware telemetry, inference state, active models, thermal history, and WES efficiency score.

## Design Decision: Pre-Digested, Not Raw

The agent should not have to reason about raw numbers. Sense gives it pre-digested decisions:

```json
{
  "wes": 11.8,
  "wes_status": "degraded",
  "suggested_action": "reduce_batch_size",
  "confidence": 0.84,
  "reason": "WES declined 15% over last 10 minutes — thermal penalty at 1.25x"
}
```

Not just `wes: 11.8`. The status, action, and confidence are as important as the value.

## Relationship to MCP

Sense tools are MCP tools. They conform to the MCP tool contract (JSON-RPC 2.0, tool name, input schema, output schema). ARP adds semantic requirements on top: every numeric field MUST include a status assessment, and every degraded/critical status MUST include a suggested action.

## Event Stream

In addition to request/response tools, Sense includes an event stream for real-time state changes:

- Node came online / went offline
- Inference state transition (idle → live → idle)
- Thermal state change (Normal → Fair → Serious → Critical)
- Observation pattern fired / resolved

The event stream uses Server-Sent Events (SSE) with a defined schema contract.
