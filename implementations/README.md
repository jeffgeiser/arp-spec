# ARP Implementations

Known implementations of the Agentic Resource Protocol.

## Reference Implementation

### [Wicklee](https://wicklee.dev)

- **Phases implemented:** Sense (complete), Score (in progress)
- **Platform:** Rust agent + React dashboard
- **Hardware support:** Apple Silicon, NVIDIA (NVML), Intel/AMD, Windows
- **Runtimes:** Ollama, vLLM, llama.cpp
- **MCP integration:** Local MCP server (all tiers) + Cloud MCP server (Team+)
- **License:** FSL-1.1-Apache-2.0 (converts to Apache 2.0 after 4 years)
- **GitHub:** [github.com/jeffgeiser/Wicklee](https://github.com/jeffgeiser/Wicklee)

Wicklee's Sense implementation includes:
- `get_node_status` — full hardware + inference metrics snapshot
- `get_inference_state` — 4-state classification with 3-tier detection hierarchy
- `get_fleet_status` — multi-node fleet context with WES scores
- `get_best_route` — routing recommendation by throughput and efficiency
- `get_inference_profile` — correlated timeline (TTFT, KV cache, thermal, power)
- `explain_slowdown` — multi-factor root cause analysis

---

## Adding Your Implementation

To list your ARP implementation, open a PR adding an entry above. Requirements:

1. Implements at least the Sense phase tool contracts
2. Validates against the JSON schemas in `schema/`
3. Links back to this spec
