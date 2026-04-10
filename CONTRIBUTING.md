# Contributing to ARP

ARP is developed in the open. The protocol matters more than any single implementation, so contributions that strengthen the spec, sharpen the schemas, or add conforming implementations are all welcome.

## What kind of contribution should I file?

| If you want to... | File this |
|---|---|
| Report ambiguity, a bug in the spec, or a confusing example | A GitHub Issue |
| Propose a non-trivial design change (new phase field, new tool, semantic shift) | An RFC under [`rfcs/`](rfcs/) |
| Add or improve a payload example | A Pull Request touching [`examples/`](examples/) |
| Tighten a JSON Schema (new field, stricter constraint, new enum value) | A Pull Request touching [`schema/`](schema/) **and** the matching `spec/*.md` |
| List your implementation | A Pull Request touching [`implementations/`](implementations/) |
| Ask a question or float an idea before committing to a design | Open a GitHub Discussion (or Issue tagged `question`) |

If you're unsure which bucket your change falls into, open an issue first and ask. Better to spend five minutes aligning than to write a PR that needs reshaping.

## Filing an Issue

Good issues include:

1. **What you expected** the spec, schema, or example to say
2. **What it actually says** (link to the file and line)
3. **Why the gap matters** for an implementor — concrete impact beats abstract concern
4. **A suggested fix** if you have one (optional, but appreciated)

If you found the issue while building an implementation, mention which phase you were trying to implement. That context helps prioritize.

## Submitting an RFC

RFCs are for changes that need design discussion before code. They live in [`rfcs/`](rfcs/) and follow [`rfcs/0001-initial-spec.md`](rfcs/0001-initial-spec.md) as a template.

1. Copy `0001-initial-spec.md` as `rfcs/00NN-short-title.md` where `00NN` is the next available number
2. Set `Status: Draft`
3. Cover at minimum: **Problem Statement**, **Design Alternatives Considered**, **Proposed Design**, **Known Limitations**
4. Open a Pull Request titled `RFC 00NN: <title>`
5. Discussion happens in the PR. Status moves to `Accepted` when merged, `Rejected` if closed, `Superseded` if replaced by a later RFC

You don't need permission to start an RFC. If you've thought hard about a problem and have a design to propose, open it.

## Pull Request Guidelines

- **Keep PRs focused.** One conceptual change per PR. A schema tightening and a doc rewrite should be two PRs.
- **Update all the surfaces.** A change to a schema field usually means updating: the schema file, the matching `spec/*.md` file, the example payload in `examples/`, and possibly the RFC. The CI of this repo is your eyeballs — please check all four.
- **Don't break existing examples.** If your change makes an example invalid against the schema, update the example in the same PR.
- **Cite the RFC** when implementing one. PR description should link to the RFC number.
- **Version bumps** to `0.1.x` happen via PR to [`CHANGELOG.md`](CHANGELOG.md). The maintainer cuts releases.

## Conformance and the Spec

ARP defines four conformance levels in [`SPEC.md`](SPEC.md) §7:

- **Sense-conformant** — implements `get_fleet_context` and `get_node_status`
- **Score-conformant** — additionally implements `score_node_fit` with explanations
- **Commit-conformant** — additionally implements `commit_workload_intent` with credit escrow
- **Full ARP** — additionally implements `settle_workload` with all three delta artifacts

Each level is independently useful. You don't need to ship Full ARP to be on the implementations list — Sense-conformant counts.

## Listing an Implementation

To add your implementation to [`implementations/README.md`](implementations/README.md):

1. Open a PR adding a row to the implementations table
2. Include: name, link, conformance level, language/runtime, license
3. Link to a test report (or example output) demonstrating conformance at the claimed level
4. Implementations don't need to be open source, but they do need to be reachable (public docs, demo, or contact channel)

## Code of Conduct

Be direct, be specific, be kind. Assume contributors are working in good faith with limited time. Critique designs, not people. Disagreement about technical choices is healthy; personal attacks are not.

## License

By contributing, you agree your contribution is licensed under the [MIT License](LICENSE) of this repository.
